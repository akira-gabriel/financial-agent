import json
import asyncio
import os

from dotenv import load_dotenv
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

from financial_agent.tools.market import find_ticker, get_company_snapshot

load_dotenv()

os.environ.pop("ANTHROPIC_API_KEY", None)

MODEL = "claude-sonnet-5-5"
SYSTEM_PROMPT = (
    "You are a financial market analyst focused on brazilian stock exchange. "
    "Use the tools to fetch data before answering. Never invent numbers. "
    "Brazilian tickers end with '.SA' (e.g. PETR4.SA). "
    "Answer in Portuguese."
)

def _ok(data) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}


def _fail(error: Exception) -> dict:
    return {
        "content": [{"type": "text", "text": f"Tool failed: {error}"}],
        "is_error": True,
    }


@tool(
    "find_ticker",
    "Find the ticker symbol of a listed company by name. "
    "Brazilian stocks end with '.SA' (e.g. PETR4.SA).",
    {"query": str},
)
async def find_ticker_tool(args: dict) -> dict:
    try:
        return _ok(await asyncio.to_thread(find_ticker, args["query"]))
    except Exception as error:
        return _fail(error)


@tool(
    "get_company_snapshot",
    "Get price and key fundamentals (P/E, market cap, dividend yield) for a ticker, e.g. 'PETR4.SA'.",
    {"ticker": str},
)
async def get_company_snapshot_tool(args: dict) -> dict:
    try:
        return _ok(await asyncio.to_thread(get_company_snapshot, args["ticker"]))
    except Exception as error:
        return _fail(error)


finance_server = create_sdk_mcp_server(
    name="finance",
    version="1.0.0",
    tools=[find_ticker_tool, get_company_snapshot_tool],
)

OPTIONS = ClaudeAgentOptions(
    model=MODEL,
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"finance": finance_server},
    allowed_tools=[
        "mcp__finance__find_ticker",
        "mcp__finance__get_company_snapshot",
    ],
    disallowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch"],
    max_turns=10,
)


async def run_agent(user_message: str) -> str:
    final_answer = ""
    async for message in query(prompt=user_message, options=OPTIONS):
        if isinstance(message, ResultMessage):
            final_answer = message.result or ""
    return final_answer


if __name__ == "__main__":
    print(asyncio.run(run_agent("Compare o P/L da Petrobras com o da Vale")))