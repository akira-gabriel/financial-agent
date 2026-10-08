import yfinance as yf

def find_ticker(query: str) -> list[dict]:
    results = yf.Search(query, max_results=5).quotes
    return [
        {
            "symbol": item.get("symbol"),
            "name": item.get("shortname"),
            "exchange": item.get("exchange"),
        }
        for item in results
    ]

def get_company_snapshot(ticker: str) -> dict:
    info = yf.Ticker(ticker).info
    return {
        "ticker": ticker,
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "currency": info.get("currency"),
        "price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "trailing_pe_ratio": info.get("trailingPE"),
        "forward_pe_ratio": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "pe_ratio": info.get("trailingPE"),
        "dividend_yield": info.get("dividendYield"),
    }

TOOL_SCHEMAS = [
    {
        "name": "find_ticker",
        "description": "Find the ticker symbol of a listed company by name. "
        "Brazilian stocks end with '.SA' (e.g. PETR4.SA).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name, e.g. 'Petrobras'"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_company_snapshot",
        "description": "Get price and key fundamentals for a ticker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Ticker symbol, e.g. 'PETR4.SA'"}
            },
            "required": ["ticker"],
        },
    },
]

TOOL_FUNCTIONS = {
    "find_ticker": find_ticker,
    "get_company_snapshot": get_company_snapshot,
}