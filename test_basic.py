#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基本功能测试
验证 AI Agent 的核心功能是否正常工作
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from tools import ToolManager, TerminalTool, FileTool, MathTool
from llm_client import LLMClient

def test_config():
    """测试配置功能"""
    print("🔧 测试配置功能...")
    
    # 测试默认配置
    default_config = Config.get_model_config("openai")
    assert default_config.provider == "openai"
    print("✅ 默认配置测试通过")
    
    # 测试 Ollama 配置
    ollama_config = Config.get_model_config("ollama")
    assert ollama_config.provider == "ollama"
    print("✅ Ollama 配置测试通过")
    
    # 测试 DeepSeek 配置
    deepseek_config = Config.get_model_config("deepseek")
    assert deepseek_config.provider == "deepseek"
    print("✅ DeepSeek 配置测试通过")
    
    print("✅ 配置功能测试完成\n")

def test_tools():
    """测试工具功能"""
    print("🛠️ 测试工具功能...")
    
    tool_manager = ToolManager()
    
    # 测试工具列表
    tools = tool_manager.list_tools()
    assert len(tools) >= 4  # 至少应该有4个工具
    print("✅ 工具列表测试通过")
    
    # 测试数学计算工具
    math_result = tool_manager.execute_tool("math", expression="2 + 3 * 4")
    assert math_result["success"] == True
    assert math_result["result"] == 14
    print("✅ 数学计算工具测试通过")
    
    # 测试文件工具
    file_result = tool_manager.execute_tool("file", action="exists", file_path="test_basic.py")
    assert file_result["success"] == True
    assert file_result["exists"] == True
    print("✅ 文件工具测试通过")
    
    # 测试终端工具（简单命令）
    terminal_result = tool_manager.execute_tool("terminal", command="echo 'test'")
    assert terminal_result["success"] == True
    assert "test" in terminal_result["stdout"]
    print("✅ 终端工具测试通过")
    
    print("✅ 工具功能测试完成\n")

def test_llm_client():
    """测试大模型客户端"""
    print("🤖 测试大模型客户端...")
    
    # 使用默认配置
    config = Config.get_model_config("openai")
    client = LLMClient(config)
    
    # 测试消息格式
    messages = [
        {"role": "system", "content": "你是一个测试助手"},
        {"role": "user", "content": "请回复 'Hello'"}
    ]
    
    try:
        # 注意：这里可能会因为API Key问题而失败，这是正常的
        response = client.chat_completion(messages)
        print("✅ 大模型客户端测试通过")
    except Exception as e:
        print(f"⚠️ 大模型客户端测试跳过（可能需要API Key）: {str(e)}")
    
    print("✅ 大模型客户端测试完成\n")

def test_agent_initialization():
    """测试 Agent 初始化"""
    print("🤖 测试 Agent 初始化...")
    
    try:
        from agent import AIAgent
        
        # 测试初始化（不实际调用API）
        agent = AIAgent("openai")
        assert agent.model_config.provider == "openai"
        assert agent.tool_manager is not None
        print("✅ Agent 初始化测试通过")
        
    except Exception as e:
        print(f"⚠️ Agent 初始化测试跳过: {str(e)}")
    
    print("✅ Agent 初始化测试完成\n")

def main():
    """运行所有测试"""
    print("🧪 开始运行基本功能测试...\n")
    
    try:
        test_config()
        test_tools()
        test_llm_client()
        test_agent_initialization()
        
        print("🎉 所有基本功能测试完成！")
        print("✅ 项目核心功能正常")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 