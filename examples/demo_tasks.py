#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Agent 示例任务
演示各种使用场景和任务类型
"""

from agent import AIAgent
import json

def run_demo_tasks():
    """运行示例任务"""
    
    # 初始化 Agent (使用 OpenAI)
    print("🚀 初始化 AI Agent...")
    agent = AIAgent("openai")
    
    # 示例任务列表
    demo_tasks = [
        {
            "name": "文件操作示例",
            "task": "创建一个名为 'hello.txt' 的文件，内容为 'Hello, AI Agent!'"
        },
        {
            "name": "终端命令示例", 
            "task": "获取当前目录的文件列表"
        },
        {
            "name": "数学计算示例",
            "task": "计算 (15 + 25) * 2 / 5 的结果"
        },
        {
            "name": "网页创建示例",
            "task": "创建一个简单的HTML页面，包含标题、段落和按钮"
        },
        {
            "name": "复杂任务示例",
            "task": "创建一个Python脚本，实现一个简单的计算器功能"
        }
    ]
    
    results = []
    
    for i, demo in enumerate(demo_tasks, 1):
        print(f"\n{'='*60}")
        print(f"📋 示例 {i}: {demo['name']}")
        print(f"任务: {demo['task']}")
        print('='*60)
        
        try:
            result = agent.execute_task(demo['task'])
            results.append({
                "demo_name": demo['name'],
                "task": demo['task'],
                "result": result
            })
            
            print(f"\n✅ 示例 {i} 完成")
            
        except Exception as e:
            print(f"\n❌ 示例 {i} 失败: {str(e)}")
            results.append({
                "demo_name": demo['name'],
                "task": demo['task'],
                "error": str(e)
            })
    
    # 保存结果
    with open('demo_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("📊 所有示例任务完成！")
    print("结果已保存到 demo_results.json")
    print('='*60)

def run_single_task(task_description: str):
    """运行单个任务"""
    print(f"🚀 执行任务: {task_description}")
    
    agent = AIAgent("openai")
    result = agent.execute_task(task_description)
    
    print(f"\n📋 任务总结:")
    print(result["summary"])
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 运行单个任务
        task = " ".join(sys.argv[1:])
        run_single_task(task)
    else:
        # 运行所有示例任务
        run_demo_tasks() 