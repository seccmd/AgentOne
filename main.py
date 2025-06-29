#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from typing import Optional
from colorama import Fore, Style, init

from agent import AIAgent
from config import Config

# 初始化colorama
init()

def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    AI Agent 学习示例                          ║
║                                                              ║
║  实现完整的 "任务输入 → 任务计划 → 任务执行 → 任务结果" 流程    ║
║                                                              ║
║  支持的大模型: OpenAI, Ollama, DeepSeek                      ║
║  支持的工具: 终端命令, 文件操作, 网络请求, 数学计算            ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")

def print_help():
    """打印帮助信息"""
    help_text = """
可用命令:
  help                    - 显示此帮助信息
  config                  - 显示当前配置
  models                  - 显示支持的模型
  tools                   - 显示可用工具
  task <任务描述>         - 执行任务
  history                 - 显示对话历史
  clear                   - 清空对话历史
  save <文件名>           - 保存对话历史到文件
  load <文件名>           - 从文件加载对话历史
  exit/quit               - 退出程序

示例任务:
  task 创建一个Python文件并写入"Hello World"
  task 获取当前目录的文件列表
  task 计算 2 + 3 * 4 的结果
  task 创建一个简单的HTML页面
"""
    print(f"{Fore.YELLOW}{help_text}{Style.RESET_ALL}")

def print_config():
    """显示当前配置"""
    print(f"{Fore.CYAN}当前配置:{Style.RESET_ALL}")
    print(f"默认模型: {Config.DEFAULT_MODEL.provider} - {Config.DEFAULT_MODEL.model_name}")
    print(f"Ollama配置: {Config.OLLAMA_CONFIG.base_url}")
    print(f"DeepSeek配置: {Config.DEEPSEEK_CONFIG.base_url}")
    print()

def print_models():
    """显示支持的模型"""
    print(f"{Fore.CYAN}支持的模型提供商:{Style.RESET_ALL}")
    print("1. OpenAI - 需要API Key")
    print("2. Ollama - 本地部署")
    print("3. DeepSeek - 需要API Key")
    print()

def print_tools():
    """显示可用工具"""
    from tools import ToolManager
    tool_manager = ToolManager()
    tools = tool_manager.list_tools()
    
    print(f"{Fore.CYAN}可用工具:{Style.RESET_ALL}")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool['name']} - {tool['description']}")
    print()

def save_history(agent: AIAgent, filename: str):
    """保存对话历史"""
    try:
        history = agent.get_conversation_history()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"{Fore.GREEN}✓ 对话历史已保存到 {filename}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ 保存失败: {str(e)}{Style.RESET_ALL}")

def load_history(agent: AIAgent, filename: str):
    """加载对话历史"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
        agent.conversation_history = history
        print(f"{Fore.GREEN}✓ 对话历史已从 {filename} 加载{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ 加载失败: {str(e)}{Style.RESET_ALL}")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Fore.YELLOW}⚠️  提示: 未设置 OPENAI_API_KEY 环境变量，将使用默认配置{Style.RESET_ALL}")
        print("如需使用OpenAI，请设置环境变量或在.env文件中配置")
        print()
    
    # 选择模型提供商
    print("请选择模型提供商:")
    print("1. OpenAI (默认)")
    print("2. Ollama")
    print("3. DeepSeek")
    
    choice = input("请输入选择 (1-3，默认1): ").strip()
    
    model_provider = "openai"
    if choice == "2":
        model_provider = "ollama"
    elif choice == "3":
        model_provider = "deepseek"
    
    try:
        # 初始化AI Agent
        agent = AIAgent(model_provider)
        print()
        
        # 交互式循环
        while True:
            try:
                command = input(f"{Fore.GREEN}AI Agent > {Style.RESET_ALL}").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit']:
                    print(f"{Fore.YELLOW}再见！{Style.RESET_ALL}")
                    break
                
                elif command.lower() == 'help':
                    print_help()
                
                elif command.lower() == 'config':
                    print_config()
                
                elif command.lower() == 'models':
                    print_models()
                
                elif command.lower() == 'tools':
                    print_tools()
                
                elif command.lower() == 'history':
                    history = agent.get_conversation_history()
                    if history:
                        print(f"{Fore.CYAN}对话历史:{Style.RESET_ALL}")
                        for i, msg in enumerate(history[-10:], 1):  # 显示最近10条
                            role_emoji = "👤" if msg["role"] == "user" else "🤖"
                            print(f"{i}. {role_emoji} {msg['role']}: {msg['content'][:100]}...")
                    else:
                        print(f"{Fore.YELLOW}暂无对话历史{Style.RESET_ALL}")
                    print()
                
                elif command.lower() == 'clear':
                    agent.clear_history()
                    print(f"{Fore.GREEN}✓ 对话历史已清空{Style.RESET_ALL}")
                
                elif command.startswith('save '):
                    filename = command[5:].strip()
                    if filename:
                        save_history(agent, filename)
                    else:
                        print(f"{Fore.RED}请指定文件名{Style.RESET_ALL}")
                
                elif command.startswith('load '):
                    filename = command[5:].strip()
                    if filename:
                        load_history(agent, filename)
                    else:
                        print(f"{Fore.RED}请指定文件名{Style.RESET_ALL}")
                
                elif command.startswith('task '):
                    task = command[5:].strip()
                    if task:
                        print()
                        result = agent.execute_task(task)
                        print()
                        print(f"{Fore.MAGENTA}📋 任务总结:{Style.RESET_ALL}")
                        print(result["summary"])
                        print()
                    else:
                        print(f"{Fore.RED}请提供任务描述{Style.RESET_ALL}")
                
                else:
                    # 默认作为任务处理
                    print()
                    result = agent.execute_task(command)
                    print()
                    print(f"{Fore.MAGENTA}📋 任务总结:{Style.RESET_ALL}")
                    print(result["summary"])
                    print()
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}输入 'exit' 退出程序{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}初始化失败: {str(e)}{Style.RESET_ALL}")
        print("请检查配置和网络连接")
        sys.exit(1)

if __name__ == "__main__":
    main() 