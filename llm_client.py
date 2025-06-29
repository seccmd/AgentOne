import json
import requests
from typing import List, Dict, Any
from config import ModelConfig

class LLMClient:
    """大模型客户端"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """chat_completion 基于对话历史生成回复
        更直观的理解：对话生成 (chat_generation)、对话推理 (chat_inference)、对话预测 (chat_prediction)
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/assistant/system", "content": "消息内容"}]
            **kwargs: 额外的模型参数，会被传递给具体的 LLM 提供商
        
        **kwargs 的作用：
        1. 灵活性：允许传递任意数量的额外参数，无需修改方法签名
        2. 参数透传：将参数直接传递给底层 LLM API，支持不同提供商的特定参数
        3. 扩展性：新增参数时无需修改接口，保持向后兼容
        
        **kwargs 常用参数示例：
        - temperature: 控制输出的随机性 (0.0-2.0)
        - max_tokens: 最大输出token数
        - top_p: 核采样参数 (0.0-1.0)
        - frequency_penalty: 频率惩罚 (-2.0-2.0)
        - presence_penalty: 存在惩罚 (-2.0-2.0)
        - stop: 停止序列列表
        - stream: 是否流式输出
        
        使用示例：
        ```python
        # 基本使用
        response = client.chat_completion(messages)
        
        # 带参数使用
        response = client.chat_completion(
            messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9
        )
        
        # 流式输出
        response = client.chat_completion(
            messages,
            stream=True,
            temperature=0.5
        )
        ```
        """
        if self.config.provider == "openai":
            return self._openai_chat(messages, **kwargs)
        elif self.config.provider == "ollama":
            return self._ollama_chat(messages, **kwargs)
        elif self.config.provider == "deepseek":
            return self._deepseek_chat(messages, **kwargs)
        else:
            raise ValueError(f"不支持的模型提供商: {self.config.provider}")
    
    def _openai_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """OpenAI聊天
        
        Args:
            messages: 消息列表
            **kwargs: 传递给 OpenAI API 的额外参数
                    例如：temperature, max_tokens, top_p, frequency_penalty 等
        """
        import openai
        
        client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        
        # 转换消息格式为 OpenAI 期望的类型
        # 原因：虽然输入的消息格式看起来正确，但 OpenAI 客户端有严格的类型检查
        # 输入格式示例：
        # [
        #     {"role": "system", "content": "你是一个助手"},
        #     {"role": "user", "content": "你好"},
        #     {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
        # ]
        # 
        # OpenAI 期望的是 ChatCompletionMessageParam 类型，而不是简单的 Dict[str, str]
        # 通过重新构建消息列表，我们确保类型兼容性
        openai_messages = []
        for msg in messages:
            if msg["role"] in ["user", "assistant", "system"]:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # **kwargs 会将所有额外参数传递给 OpenAI API
        # 例如：temperature=0.7, max_tokens=1000 等
        response = client.chat.completions.create(
            model=self.config.model_name,
            messages=openai_messages,  # type: ignore
            **kwargs  # 透传所有额外参数
        )
        
        return response.choices[0].message.content
    
    def _ollama_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Ollama聊天
        
        Args:
            messages: 消息列表
            **kwargs: 传递给 Ollama API 的额外参数
                    例如：temperature, top_p, top_k, repeat_penalty 等
        """
        # 转换消息格式
        # 原因：虽然 Ollama 的消息格式与 OpenAI 类似，但为了确保兼容性
        # 我们重新构建消息列表，只保留必要的字段
        # 
        # 输入格式示例：
        # [
        #     {"role": "system", "content": "你是一个助手"},
        #     {"role": "user", "content": "你好"},
        #     {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
        # ]
        # 
        # Ollama 期望的格式基本相同，但通过重新构建确保没有多余字段
        ollama_messages = []
        for msg in messages:
            if msg["role"] == "user":
                ollama_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                ollama_messages.append({"role": "assistant", "content": msg["content"]})
            elif msg["role"] == "system":
                # Ollama使用system字段
                ollama_messages.append({"role": "system", "content": msg["content"]})
        
        payload = {
            "model": self.config.model_name,
            "messages": ollama_messages,
            **kwargs  # 透传所有额外参数到 Ollama API
        }
        
        response = requests.post(
            f"{self.config.base_url}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            raise Exception(f"Ollama API错误: {response.text}")
    
    def _deepseek_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """DeepSeek聊天
        
        Args:
            messages: 消息列表
            **kwargs: 传递给 DeepSeek API 的额外参数
                    例如：temperature, max_tokens, top_p, frequency_penalty 等
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            **kwargs  # 透传所有额外参数到 DeepSeek API
        }
        
        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"DeepSeek API错误: {response.text}") 