import json
from typing import Optional, Tuple
from urllib.request import Request, urlopen

from tradingagents.llm_clients.provider_settings import resolve_provider_api_key


_MODEL_CACHE = {}


def parse_shengsuanyun_models(payload) -> list[str]:
    """Extract model ids from a ShengsuanYun /models response payload."""
    data = payload.get("data", []) if isinstance(payload, dict) else []
    model_ids = []

    for item in data:
        if not isinstance(item, dict):
            continue
        model_id = item.get("id")
        if model_id and model_id not in model_ids:
            model_ids.append(model_id)

    return model_ids


def fetch_shengsuanyun_models(models_url: str, timeout: float = 3.0) -> Tuple[list[str], Optional[str]]:
    """Fetch available models from ShengsuanYun.

    Returns:
        (model_ids, error_message). On success, error_message is None.
    """
    cache_key = (models_url, timeout)
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    api_key = resolve_provider_api_key("shengsuanyun")
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        request = Request(models_url, headers=headers)
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))

        model_ids = parse_shengsuanyun_models(payload)
        if not model_ids:
            result = ([], "Shengsuanyun model catalog returned no models.")
        else:
            result = (sorted(model_ids), None)
    except Exception as exc:  # pragma: no cover - exercised via tests with mocks
        result = ([], f"Failed to fetch Shengsuanyun models: {exc}")

    _MODEL_CACHE[cache_key] = result
    return result
