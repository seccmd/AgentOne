import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from colorama import Fore, Style, init

from config import Config
from llm_client import LLMClient
from tools import ToolManager

# 初始化colorama
init()

class TaskStep:
    """任务步骤"""
    
    def __init__(self, step_id: int, description: str, tool_name: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
        self.step_id = step_id
        self.description = description
        self.tool_name = tool_name
        self.parameters = parameters or {}
        self.status = "pending"  # pending, running, completed, failed
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "status": self.status,
            "result": self.result,
            "error": self.error
        }

class AIAgent:
    """AI Agent核心类"""
    
    def __init__(self, model_provider: str = "openai"):
        self.model_config = Config.get_model_config(model_provider)
        self.llm_client = LLMClient(self.model_config)
        self.tool_manager = ToolManager()
        self.conversation_history = []
        
        print(f"{Fore.GREEN}✓ AI Agent 初始化完成{Style.RESET_ALL}")
        print(f"{Fore.CYAN}模型提供商: {self.model_config.provider}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}模型名称: {self.model_config.model_name}{Style.RESET_ALL}")
    
    def add_message(self, role: str, content: str):
        """添加对话消息"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def plan_task(self, task: str) -> List[TaskStep]:
        """任务计划：将任务拆解为多个步骤"""
        print(f"{Fore.YELLOW}📋 正在制定任务计划...{Style.RESET_ALL}")
        
        # 构建系统提示词
        system_prompt = """你是一个专业的任务规划专家。请将用户的任务拆解为具体的执行步骤。

每个步骤应该包含：
1. 步骤描述
2. 需要使用的工具（如果有）
3. 工具参数（如果有）

可用的工具及参数：
{}

请以JSON格式返回步骤列表，格式如下：
[
    {{
        "step_id": 1,
        "description": "步骤描述",
        "tool_name": "工具名称（可选）",
        "parameters": {{"参数名": "参数值"}}
    }}
]

重要要求：
1. 必须返回完整的JSON格式，不要截断
2. 不要包含任何额外的文本说明
3. 确保JSON语法正确
4. 每个步骤的description不能为空
5. 如果使用工具，tool_name必须与可用工具列表中的name匹配
6. 参数名称必须与工具定义完全一致""".format(self.tool_manager.get_tools_description())
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请为以下任务制定执行计划：{task}"}
        ]
        
        try:
            response = self.llm_client.chat_completion(messages)
            self.add_message("assistant", response)
            
            # 调试：打印原始响应（前500字符）
            print(f"{Fore.CYAN}🔍 LLM 响应预览: {response[:500]}...{Style.RESET_ALL}")
            
            # 清理响应中的可能干扰JSON解析的内容
            response = response.strip()
            
            # 如果响应为空，抛出异常
            if not response:
                raise ValueError("LLM 返回了空响应")
            
            # 清理代码块格式
            if response.startswith("```json"):
                response = response[7:]  # 移除 ```json
            elif response.startswith("```"):
                response = response[3:]  # 移除 ```
            
            if response.endswith("```"):
                response = response[:-3]  # 移除结尾的 ```
            
            response = response.strip()
            
            # 如果响应为空，抛出异常
            if not response:
                raise ValueError("清理后LLM响应为空")
            
            # 解析JSON响应
            try:
                steps_data = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"{Fore.RED}❌ JSON 解析错误详情: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.RED}❌ 尝试解析的内容: {response}{Style.RESET_ALL}")
                raise
            
            steps = []
            
            for step_data in steps_data:
                step = TaskStep(
                    step_id=step_data["step_id"],
                    description=step_data["description"],
                    tool_name=step_data.get("tool_name"),
                    parameters=step_data.get("parameters", {})
                )
                steps.append(step)
            
            print(f"{Fore.GREEN}✓ 任务计划制定完成，共 {len(steps)} 个步骤{Style.RESET_ALL}")
            return steps
            
        except Exception as e:
            print(f"{Fore.RED}✗ 任务计划制定失败: {str(e)}{Style.RESET_ALL}")
            # 返回默认步骤
            return [TaskStep(1, f"执行任务: {task}")]
    
    def execute_step(self, step: TaskStep) -> bool:
        """执行单个任务步骤"""
        print(f"{Fore.BLUE}🔄 执行步骤 {step.step_id}: {step.description}{Style.RESET_ALL}")
        step.status = "running"
        
        try:
            if step.tool_name:
                # 使用工具执行
                result = self.tool_manager.execute_tool(step.tool_name, **step.parameters)
                step.result = result
                
                if result.get("success", False):
                    step.status = "completed"
                    print(f"{Fore.GREEN}✓ 步骤 {step.step_id} 执行成功{Style.RESET_ALL}")
                    if "stdout" in result and result["stdout"]:
                        print(f"{Fore.CYAN}输出: {result['stdout'][:200]}...{Style.RESET_ALL}")
                    return True
                else:
                    step.status = "failed"
                    step.error = result.get("error", "未知错误")
                    print(f"{Fore.RED}✗ 步骤 {step.step_id} 执行失败: {step.error}{Style.RESET_ALL}")
                    return False
            else:
                # 纯文本步骤，标记为完成
                step.status = "completed"
                step.result = {"message": "步骤完成"}
                print(f"{Fore.GREEN}✓ 步骤 {step.step_id} 完成{Style.RESET_ALL}")
                return True
                
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            print(f"{Fore.RED}✗ 步骤 {step.step_id} 执行异常: {str(e)}{Style.RESET_ALL}")
            return False
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """执行完整任务流程"""
        print(f"{Fore.MAGENTA}🚀 开始执行任务: {task}{Style.RESET_ALL}")
        print("=" * 60)
        
        # 1. 任务输入
        self.add_message("user", task)
        print(f"{Fore.CYAN}📥 任务输入: {task}{Style.RESET_ALL}")
        
        # 2. 任务计划
        steps = self.plan_task(task)
        
        # 3. 任务执行
        print(f"{Fore.YELLOW}⚡ 开始执行任务步骤...{Style.RESET_ALL}")
        successful_steps = 0
        failed_steps = 0
        
        for step in steps:
            if self.execute_step(step):
                successful_steps += 1
            else:
                failed_steps += 1
                # 可以选择是否继续执行后续步骤
                # break
        
        # 4. 任务结果
        print("=" * 60)
        print(f"{Fore.MAGENTA}📊 任务执行结果{Style.RESET_ALL}")
        print(f"总步骤数: {len(steps)}")
        print(f"成功步骤: {successful_steps}")
        print(f"失败步骤: {failed_steps}")
        
        # 生成任务总结
        summary = self.generate_summary(task, steps)
        
        result = {
            "task": task,
            "steps": [step.to_dict() for step in steps],
            "summary": summary,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "total_steps": len(steps),
            "timestamp": datetime.now().isoformat()
        }
        
        self.add_message("assistant", f"任务执行完成。成功步骤: {successful_steps}, 失败步骤: {failed_steps}")
        
        return result
    
    def generate_summary(self, task: str, steps: List[TaskStep]) -> str:
        """生成任务执行总结"""
        print(f"{Fore.YELLOW}📝 正在生成任务总结...{Style.RESET_ALL}")
        
        system_prompt = """你是一个任务总结专家。请根据任务执行情况生成简洁明了的总结报告。"""
        
        steps_summary = []
        for step in steps:
            status_emoji = "✅" if step.status == "completed" else "❌"
            steps_summary.append(f"{status_emoji} 步骤{step.step_id}: {step.description}")
        
        user_prompt = f"""任务: {task}

执行步骤:
{chr(10).join(steps_summary)}

请生成一个简洁的任务执行总结，包括：
1. 任务完成情况
2. 主要成果
3. 遇到的问题（如果有）
4. 建议（如果有）"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            summary = self.llm_client.chat_completion(messages)
            print(f"{Fore.GREEN}✓ 任务总结生成完成{Style.RESET_ALL}")
            return summary
        except Exception as e:
            print(f"{Fore.RED}✗ 任务总结生成失败: {str(e)}{Style.RESET_ALL}")
            return f"任务执行完成。成功步骤: {len([s for s in steps if s.status == 'completed'])}, 失败步骤: {len([s for s in steps if s.status == 'failed'])}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear() 