#!/usr/bin/env python3
"""Ornith MCP Server — expose Ornith-1.5-9B reasoning to Claude Code via MCP."""

import json
from mcp.server.fastmcp import FastMCP

import requests

mcp = FastMCP("ornith")


@mcp.tool(name="ornith_reason", description="本地 Ornith-1.5-9B 推理模型，擅长代码分析和性能推理")
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