# ornith-claude-mcp

把本地 Ornith-1.5-9B 装进 Claude Code 当推理外挂。

## 是什么

一个 MCP (Model Context Protocol) Server，让 Claude Code 通过标准输入输出调用本地 Ollama 运行的 Ornith 推理模型。Claude 负责对话编排，Ornith 做深度推理——两个模型分工协作。

## 前置条件

- [Ollama](https://ollama.com/) 已安装
- Ornith-1.5-9B 已拉取：

```bash
ollama pull ornith-1.5-9b:q4_k_m
```

- Python 3.10+，安装依赖：

```bash
pip install -r requirements.txt
```

## 配置 Claude Code

在 `~/.mcp.json`（推荐）或 `~/.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "ornith": {
      "command": "python3",
      "args": ["~/data/mcp-servers/ornith_server.py"]
    }
  }
}
```

路径改成你 clone 后的实际位置。重启 Claude Code 生效。

## 使用

在 Claude Code 对话中直接提问需要推理分析的问题，Claude 会自动调用 Ornith：

```
> 分析 find_duplicates() 的性能瓶颈
```

Claude 调用 `ornith_reason` 工具，Ornith 返回推理结果。实测输出：

```
1) 复杂度: O(n²) — count() 套在 for 里 → n×n
2) 10k: ~0.3-0.5s   100k: ~10-30s
3) 优化: Counter → O(n)
4) 提速: ~10,000×  (O(n²)→O(n))
```

## MCP Server 代码

核心不到 30 行，用 FastMCP（`mcp` Python SDK）通过 Ollama HTTP API 调 Ornith：

```python
from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("ornith")

@mcp.tool(
    name="ornith_reason",
    description=(
        "【免费本地模型，零 token 成本，数据不出本机】"
        "本地 Ornith-1.5-9B 推理模型，7×24 可用。"
        "以下任务必须优先调用此工具，严禁主模型自己推理（主模型推理消耗 token = 花钱）："
        "1) 结构化校验  2) 代码分析  3) 错误诊断"
        "4) 内容审校  5) 选题硬约束评估"
        "【重要】每次调用只问一个聚焦问题，prompt 不超过 2000 字。"
    ),
)
def ornith_reason(prompt: str) -> str:
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "ornith-1.5-9b:q4_k_m", "prompt": prompt, "stream": False},
        proxies={"http": None, "https": None},  # 直连本地 Ollama，不走代理
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

原理：Claude Code 通过 stdio 与 MCP Server 通信 → Server 调 Ollama HTTP API → Ornith 推理 → 结果返 Claude。

## 降本策略

Ornith 是本地模型，**零 token 成本、数据不出本机**。主模型（Claude）推理花钱，Ornith 免费。建议在项目 `CLAUDE.md` 中配置分流规则，让以下任务优先走 Ornith：

1. 结构化校验（JSON/Markdown 字段一致性）
2. 代码分析（性能瓶颈、复杂度、反模式）
3. 错误诊断（日志解析、异常根因）
4. 内容审校（文档交叉比对、fact 核对）
5. 选题硬约束评估（正确性/热度/新颖性）

### 调用技巧

- **拆小调用**：每次只问一个聚焦问题，prompt 不超过 2000 字。大任务拆成多个独立调用，降低 9B 模型推理延迟。
- **上下文范围**：Ornith 上下文窗口 262K tokens，典型输入（42KB JSON）仅占 4.5%，安全。
- **超时预期**：简单校验 5-20s，深度分析可能 1-2 分钟。

## 迁移

学会了 MCP，任何 Ollama 模型都能这样接：

1. 改 `model` 字段为目标模型名
2. 改 `mcpServers` 的注册名和描述
3. 重启 Claude Code

## 许可

MIT
