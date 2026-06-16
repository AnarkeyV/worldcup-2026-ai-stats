import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.config import settings


class LocalLlamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
    ):
        self.base_url = (base_url or settings.llama_base_url).rstrip("/")
        self.model = model or settings.llama_model
        self.timeout_seconds = timeout_seconds or settings.llama_timeout_seconds

    def health_check(self) -> dict:
        try:
            data = self._get_json("/api/tags")
            models = [
                model.get("name")
                for model in data.get("models", [])
                if model.get("name")
            ]

            return {
                "available": True,
                "provider": "local_llama",
                "base_url": self.base_url,
                "configured_model": self.model,
                "models": models,
            }

        except RuntimeError as error:
            return {
                "available": False,
                "provider": "local_llama",
                "base_url": self.base_url,
                "configured_model": self.model,
                "models": [],
                "error": str(error),
            }

    def generate_summary(self, prompt: str) -> dict:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        payload = {
            "model": self.model,
            "prompt": prompt.strip(),
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        }

        data = self._post_json("/api/generate", payload)
        summary = data.get("response", "").strip()

        if not summary:
            raise RuntimeError("Local Llama returned an empty summary.")

        return {
            "provider": "local_llama",
            "model": self.model,
            "summary": summary,
        }

    def _get_json(self, endpoint: str) -> dict:
        url = self._build_url(endpoint)
        request = Request(url, method="GET")

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)

        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Unable to connect to Local Llama: {error}") from error

    def _post_json(self, endpoint: str, payload: dict) -> dict:
        url = self._build_url(endpoint)
        body = json.dumps(payload).encode("utf-8")

        request = Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body)

        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Unable to generate Local Llama summary: {error}") from error

    def _build_url(self, endpoint: str) -> str:
        clean_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"{self.base_url}{clean_endpoint}"