import os
from typing import Optional


OPENAI_COMPATIBLE_PROVIDER_CONFIG = {
    "xai": {
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
        "api_key_aliases": (),
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "api_key_aliases": (),
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
        "api_key_aliases": (),
    },
    "shengsuanyun": {
        "base_url": "https://router.shengsuanyun.com/api/v1",
        "api_key_env": "SHENGSUANYUN_API_KEY",
        "api_key_aliases": ("SSY_API_KEY",),
    },
}


def get_provider_setting(provider: str, key: str, default=None):
    """Read a setting for an OpenAI-compatible provider."""
    return OPENAI_COMPATIBLE_PROVIDER_CONFIG.get(provider.lower(), {}).get(key, default)


def resolve_provider_api_key(provider: str, explicit_api_key: Optional[str] = None) -> Optional[str]:
    """Resolve API key from explicit value or provider-specific environment variables."""
    if explicit_api_key:
        return explicit_api_key

    config = OPENAI_COMPATIBLE_PROVIDER_CONFIG.get(provider.lower(), {})
    env_names = [config.get("api_key_env"), *config.get("api_key_aliases", ())]

    for env_name in env_names:
        if not env_name:
            continue
        api_key = os.environ.get(env_name)
        if api_key:
            return api_key

    return None
