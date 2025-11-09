"""Ollama (Local LLM) Adapter"""
from app.config import Config


class OllamaAdapter:
    """Ollama local LLM adapter"""

    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL or "http://localhost:11434"
        self.model = Config.OLLAMA_MODEL or "llama2"

    def chat(self, messages, system_prompt=None, temperature=0.7):
        """Send chat and get response"""
        # In production with Ollama running:
        # import requests
        # payload = {
        #     "model": self.model,
        #     "messages": messages,
        #     "stream": False
        # }
        # response = requests.post(f"{self.base_url}/api/chat", json=payload)
        # return response.json()['message']['content']

        return "Ollama response (demo mode - start Ollama server to enable)"

    def stream_chat(self, messages, system_prompt=None):
        """Stream chat responses"""
        for chunk in ["Ollama ", "streaming ", "response"]:
            yield chunk
