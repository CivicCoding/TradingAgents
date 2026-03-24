import os
import unittest
from unittest.mock import patch

from cli.provider_discovery import fetch_shengsuanyun_models, parse_shengsuanyun_models
from tradingagents.llm_clients.provider_settings import (
    get_provider_setting,
    resolve_provider_api_key,
)
from tradingagents.llm_clients.validators import validate_model


class ShengsuanyunSupportTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict("cli.provider_discovery._MODEL_CACHE", {}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_parse_shengsuanyun_models_extracts_ids(self):
        payload = {
            "data": [
                {"id": "deepseek/deepseek-v3"},
                {"id": "anthropic/claude-sonnet-4-5"},
                {"id": "deepseek/deepseek-v3"},
                {"name": "missing-id"},
            ]
        }

        self.assertEqual(
            parse_shengsuanyun_models(payload),
            ["deepseek/deepseek-v3", "anthropic/claude-sonnet-4-5"],
        )

    def test_fetch_shengsuanyun_models_returns_sorted_models(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"data": [{"id": "z-model"}, {"id": "a-model"}]}'

        with patch("cli.provider_discovery.urlopen", return_value=FakeResponse()):
            models, error = fetch_shengsuanyun_models("https://router.shengsuanyun.com/api/v1/models", timeout=0.1)

        self.assertEqual(models, ["a-model", "z-model"])
        self.assertIsNone(error)

    def test_shengsuanyun_provider_settings_expose_base_url(self):
        self.assertEqual(
            get_provider_setting("shengsuanyun", "base_url"),
            "https://router.shengsuanyun.com/api/v1",
        )

    def test_validate_model_accepts_any_shengsuanyun_model_id(self):
        self.assertTrue(validate_model("shengsuanyun", "deepseek/deepseek-v3"))
        self.assertTrue(validate_model("shengsuanyun", "any/provider-model"))

    def test_resolve_provider_api_key_supports_alias(self):
        with patch.dict(os.environ, {"SSY_API_KEY": "alias-key"}, clear=True):
            self.assertEqual(resolve_provider_api_key("shengsuanyun"), "alias-key")

    def test_factory_routes_shengsuanyun_to_openai_client(self):
        try:
            from tradingagents.llm_clients.factory import create_llm_client
            from tradingagents.llm_clients.openai_client import OpenAIClient
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional deps
            self.skipTest(f"Optional dependency missing: {exc}")

        client = create_llm_client("shengsuanyun", "deepseek/deepseek-v3")
        self.assertIsInstance(client, OpenAIClient)
        self.assertEqual(client.provider, "shengsuanyun")


if __name__ == "__main__":
    unittest.main()
