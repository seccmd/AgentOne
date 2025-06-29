import subprocess
import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

class Tool:
    """工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        raise NotImplementedError
    
    def get_parameters_info(self) -> Dict[str, str]:
        """获取工具参数信息"""
        return {}
    
    def get_full_description(self) -> str:
        """获取完整的工具描述，包括参数信息"""
        params_info = self.get_parameters_info()
        if not params_info:
            return f"- {self.name}: {self.description}"
        
        params_desc = []
        for param, desc in params_info.items():
            params_desc.append(f"  - {param}: {desc}")
        
        return f"- {self.name}: {self.description}\n" + "\n".join(params_desc)

class TerminalTool(Tool):
    """终端命令工具"""
    
    def __init__(self):
        super().__init__(
            name="terminal",
            description="执行终端命令"
        )
    
    def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """执行终端命令"""
        try:
            # 设置工作目录
            if cwd:
                os.chdir(cwd)
            
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "命令执行超时",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def get_parameters_info(self) -> Dict[str, str]:
        """获取工具参数信息"""
        return {
            "command": "要执行的命令",
            "cwd": "工作目录（可选）"
        }

class FileTool(Tool):
    """文件操作工具"""
    
    def __init__(self):
        super().__init__(
            name="file",
            description="文件读写操作"
        )
    
    def execute(self, action: str, file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """执行文件操作"""
        try:
            if action == "read":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "success": True,
                    "action": action,
                    "file_path": file_path,
                    "content": content
                }
            elif action == "write":
                if content is None:
                    return {
                        "success": False,
                        "error": "写入操作需要提供内容",
                        "action": action,
                        "file_path": file_path
                    }
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {
                    "success": True,
                    "action": action,
                    "file_path": file_path,
                    "message": "文件写入成功"
                }
            elif action == "exists":
                exists = os.path.exists(file_path)
                return {
                    "success": True,
                    "action": action,
                    "file_path": file_path,
                    "exists": exists
                }
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {action}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action,
                "file_path": file_path
            }
    
    def get_parameters_info(self) -> Dict[str, str]:
        """获取工具参数信息"""
        return {
            "action": "操作类型（read/write/exists）",
            "file_path": "文件路径",
            "content": "文件内容（write操作时需要）"
        }

class WebTool(Tool):
    """网络请求工具"""
    
    def __init__(self):
        super().__init__(
            name="web",
            description="网络请求操作"
        )
    
    def execute(self, method: str, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行网络请求"""
        try:
            if method.lower() == "get":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.lower() == "post":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                return {
                    "success": False,
                    "error": f"不支持的HTTP方法: {method}"
                }
            
            return {
                "success": True,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": method,
                "url": url
            }
    
    def get_parameters_info(self) -> Dict[str, str]:
        """获取工具参数信息"""
        return {
            "method": "HTTP方法（get/post）",
            "url": "请求URL",
            "data": "请求数据（可选）",
            "headers": "请求头（可选）"
        }

class MathTool(Tool):
    """数学计算工具"""
    
    def __init__(self):
        super().__init__(
            name="math",
            description="数学计算操作"
        )
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """执行数学计算"""
        try:
            # 安全评估数学表达式
            allowed_names = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'len': len, 'int': int, 'float': float
            }
            
            # 移除危险函数
            expression = expression.replace('eval', '').replace('exec', '')
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def get_parameters_info(self) -> Dict[str, str]:
        """获取工具参数信息"""
        return {
            "expression": "数学表达式"
        }

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools = {
            "terminal": TerminalTool(),
            "file": FileTool(),
            "web": WebTool(),
            "math": MathTool()
        }
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有工具"""
        return [
            {"name": name, "description": tool.description}
            for name, tool in self.tools.items()
        ]
    
    def get_tools_description(self) -> str:
        """获取所有工具的完整描述，包括参数信息"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(tool.get_full_description())
        return "\n".join(descriptions)
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        tool = self.get_tool(tool_name)
        if tool:
            return tool.execute(**kwargs)
        else:
            return {
                "success": False,
                "error": f"工具不存在: {tool_name}"
            } 