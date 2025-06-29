#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Agent 快速开始示例
演示如何使用 AI Agent 执行简单任务
"""

from agent import AIAgent
from colorama import Fore, Style, init

# 初始化colorama
init()

def quick_demo():
    """快速演示"""
    print(f"{Fore.CYAN}🚀 AI Agent 快速开始演示{Style.RESET_ALL}")
    print("=" * 50)
    
    # 初始化 Agent
    print("1. 初始化 AI Agent...")
    agent = AIAgent("openai")  # 使用 OpenAI 模型
    print()
    
    # 示例任务
    demo_tasks = [
        "创建一个名为 'demo.txt' 的文件，内容为 'Hello from AI Agent!'",
        "计算 10 + 20 * 3 的结果",
        "获取当前目录的文件列表"
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"{Fore.YELLOW}任务 {i}: {task}{Style.RESET_ALL}")
        print("-" * 40)
        
        try:
            result = agent.execute_task(task)
            print(f"{Fore.GREEN}✅ 任务 {i} 完成{Style.RESET_ALL}")
            print(f"成功步骤: {result['successful_steps']}")
            print(f"失败步骤: {result['failed_steps']}")
            print()
            
        except Exception as e:
            print(f"{Fore.RED}❌ 任务 {i} 失败: {str(e)}{Style.RESET_ALL}")
            print()
    
    print(f"{Fore.MAGENTA}🎉 演示完成！{Style.RESET_ALL}")

def interactive_demo():
    """交互式演示"""
    print(f"{Fore.CYAN}🎮 交互式演示{Style.RESET_ALL}")
    print("输入 'exit' 退出")
    print("=" * 30)
    
    agent = AIAgent("openai")
    
    while True:
        try:
            task = input(f"{Fore.GREEN}请输入任务 > {Style.RESET_ALL}").strip()
            
            if task.lower() in ['exit', 'quit']:
                print(f"{Fore.YELLOW}再见！{Style.RESET_ALL}")
                break
            
            if not task:
                continue
            
            print()
            result = agent.execute_task(task)
            print()
            print(f"{Fore.MAGENTA}📋 任务总结:{Style.RESET_ALL}")
            print(result["summary"])
            print()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}输入 'exit' 退出{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        quick_demo() 