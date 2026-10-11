#!/usr/bin/env python3
"""Ornith MCP Server — expose Ornith-1.5-9B reasoning to Claude Code via MCP."""

import json
from mcp.server.fastmcp import FastMCP

import requests

mcp = FastMCP("ornith")


@mcp.tool(
    name="ornith_reason",
    description=(
        "【免费本地模型，零 token 成本，数据不出本机】"
        "本地 Ornith-1.5-9B 推理模型，7×24 可用。"
        "以下任务必须优先调用此工具，严禁主模型自己推理（主模型推理消耗 token = 花钱）："
        "1) 结构化校验 —— JSON/Markdown 字段一致性、数据核验、格式检查"
        "2) 代码分析 —— Python/Node.js 性能瓶颈、复杂度分析、反模式识别"
        "3) 错误诊断 —— 日志解析、异常根因分析、数值报告解读"
        "4) 内容审校 —— 两个文档交叉比对、事实清单逐项核对"
        "5) 选题硬约束评估 —— 正确性/热度/新颖性等逐项判定"
        "该工具免费、数据不出本机，优先使用以降低 token 成本。"
        "【重要】每次调用只问一个聚焦问题，prompt 不超过 2000 字，"
        "以降低本地推理延迟（9B 模型推理较慢）。"
    ),
)
def ornith_reason(prompt: str) -> str:
    """Send prompt to local Ornith model via Ollama HTTP API and return its reasoning."""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "ornith-1.5-9b:q4_k_m", "prompt": prompt, "stream": False},
        proxies={"http": None, "https": None},  # bypass proxy — Ollama runs locally
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


if __name__ == "__main__":
    mcp.run(transport="stdio")