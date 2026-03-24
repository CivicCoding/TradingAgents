# Shengsuanyun Provider

TradingAgents supports Shengsuanyun as an OpenAI-compatible routed provider.

## Required Configuration

Set the API key:

```bash
export SHENGSUANYUN_API_KEY=...
```

`SSY_API_KEY` is also accepted as a legacy fallback alias.

Base URL:

```text
https://router.shengsuanyun.com/api/v1
```

Model catalog endpoint:

```text
https://router.shengsuanyun.com/api/v1/models
```

## CLI Behavior

- Select `Shengsuanyun` in the provider menu.
- The CLI tries to fetch available models from `/models`.
- If discovery succeeds, quick and deep models are selected from a dynamic list.
- If discovery fails or returns an empty list, the CLI falls back to manual model-id input.

## Python Example

```python
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "shengsuanyun"
config["backend_url"] = "https://router.shengsuanyun.com/api/v1"
config["quick_think_llm"] = "deepseek/deepseek-v3"
config["deep_think_llm"] = "anthropic/claude-sonnet-4-5"

# Optional routed provider parameters
config["shengsuanyun_supplier"] = "deepseek"
config["shengsuanyun_auto_route"] = True
config["shengsuanyun_extra_headers"] = {
    "HTTP-Referer": "https://your-app.example",
    "X-Title": "TradingAgents",
}

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

## Request Routing Notes

- TradingAgents treats Shengsuanyun as a first-class provider value: `llm_provider="shengsuanyun"`.
- The transport is still implemented through the existing OpenAI-compatible client.
- Native OpenAI keeps using the Responses API.
- Shengsuanyun explicitly uses Chat Completions, which matches the provider documentation.

## Optional Parameters

- `shengsuanyun_supplier`
  Passes the preferred upstream supplier to the router.
- `shengsuanyun_auto_route`
  Enables router-side automatic routing when supported.
- `shengsuanyun_extra_headers`
  Lets you send headers such as `HTTP-Referer` and `X-Title`.
