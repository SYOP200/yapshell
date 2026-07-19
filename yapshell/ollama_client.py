import warnings

# Suppress harmless LibreSSL/urllib3 NotOpenSSLWarning (emitted at import time)
try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning, module="urllib3")
except ImportError:
    pass

import requests


class YapOllamaClient:
    """Ollama chat client using the HTTP API (no Python library dependency)."""

    SYSTEM_PROMPT = (
        "You are YAP, the overly chatty AI companion of yap-shell. "
        "Be funny, enthusiastic, and slightly unhinged but still helpful. "
        "Keep responses concise and engaging. "
        "If you don't know something, make up a funny response instead of saying you're an AI. "
        "Speak in first person like a weird friend who knows too much. "
        "Be creative and colorful with your language."
    )

    def __init__(self, model="qwen3.6", host="http://localhost:11434"):
        self.model = model
        self.host = host
        self.available = False
        try:
            r = requests.get(f"{host}/api/tags", timeout=3)
            models = r.json().get("models", [])
            self.available = any(self.model in (m.get("name", "") or m.get("model", "")) for m in models)
        except Exception:
            self.available = False

    def chat_stream(self, user_message, system=None):
        """Stream a chat response via the Ollama HTTP API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user_message})

        payload = {"model": self.model, "messages": messages, "stream": True}
        
        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if not line:
                    continue
                import json
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
                    
        except Exception as e:
            yield f"\n[Error connecting to Ollama: {e}]"

    def chat(self, user_message, system=None):
        """Get full response (non-streaming)."""
        return "".join(self.chat_stream(user_message, system))

    def list_models(self):
        """List all models available via the Ollama API."""
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            models = r.json().get("models", [])
            return [m.get("name", "") for m in models if m.get("name")]
        except Exception:
            return []

    def check_health(self):
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

