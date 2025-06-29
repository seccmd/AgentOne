# AI Agent 学习示例

这是一个用于学习 AI Agent 技术原理的完整示例项目，实现了基本的 "任务输入 → 任务计划 → 任务执行 → 任务结果" 的完整闭环流程。

## 🎯 项目特点

- **完整的 Agent 流程**: 实现了任务输入、计划制定、步骤执行、结果总结的完整流程
- **多模型支持**: 支持 OpenAI、Ollama、DeepSeek 三种大模型
- **丰富工具集**: 包含终端命令、文件操作、网络请求、数学计算等工具
- **交互式界面**: 提供友好的命令行交互界面
- **学习友好**: 代码结构清晰，注释详细，适合学习 AI Agent 技术原理

## 🏗️ 项目结构

```
AI-Agent-Learn-Demo/
├── config.py          # 配置管理
├── llm_client.py      # 大模型客户端
├── tools.py           # 工具模块
├── agent.py           # AI Agent 核心
├── main.py            # 主程序入口
├── requirements.txt   # 依赖包
├── .env.example       # 环境变量示例
└── README.md          # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt

# uv 
uv venv
uv pip install -r requirements.txt 
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入相应的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：

```env
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Ollama 配置 (本地部署)
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. 运行程序

```bash
python main.py

# uv
uv run main.py 
```

## 📖 使用说明

### 基本命令

- `help` - 显示帮助信息
- `config` - 显示当前配置
- `models` - 显示支持的模型
- `tools` - 显示可用工具
- `task <任务描述>` - 执行任务
- `history` - 显示对话历史
- `clear` - 清空对话历史
- `save <文件名>` - 保存对话历史
- `load <文件名>` - 加载对话历史
- `exit/quit` - 退出程序

### 示例任务

```bash
# 创建文件
task 创建一个Python文件并写入"Hello World"

# 获取文件列表
task 获取当前目录的文件列表

# 数学计算
task 计算 2 + 3 * 4 的结果

# 创建网页
task 创建一个简单的HTML页面
```

## 🔧 技术架构

### 核心组件

1. **配置管理 (config.py)**
   - 支持多种模型配置
   - 环境变量管理
   - 配置验证

2. **大模型客户端 (llm_client.py)**
   - 统一的模型接口
   - 支持 OpenAI、Ollama、DeepSeek
   - 错误处理和重试机制

3. **工具系统 (tools.py)**
   - 工具基类和扩展机制
   - 终端命令执行
   - 文件操作
   - 网络请求
   - 数学计算

4. **AI Agent (agent.py)**
   - 任务计划制定
   - 步骤执行管理
   - 结果总结生成
   - 对话历史管理

### 工作流程

```
任务输入 → 任务计划 → 任务执行 → 任务结果
    ↓         ↓         ↓         ↓
  用户输入    LLM分析   工具调用   结果总结
```

## 🛠️ 扩展开发

### 添加新工具

在 `tools.py` 中继承 `Tool` 基类：

```python
class MyTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的工具描述"
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # 实现工具逻辑
        return {"success": True, "result": "执行结果"}
```

然后在 `ToolManager` 中注册：

```python
self.tools["my_tool"] = MyTool()
```

### 添加新模型

在 `config.py` 中添加新模型配置，在 `llm_client.py` 中实现对应的聊天方法。

## 📚 学习要点

1. **Agent 架构设计**: 了解如何设计一个完整的 AI Agent 系统
2. **任务分解**: 学习如何将复杂任务拆解为可执行的步骤
3. **工具集成**: 理解如何集成外部工具和 API
4. **错误处理**: 掌握异常处理和错误恢复机制
5. **配置管理**: 学习多环境配置管理
6. **交互设计**: 了解用户交互界面的设计原则

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！
