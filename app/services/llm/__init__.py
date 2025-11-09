"""LLM Service - Swappable AI providers"""
from app.config import Config


class LLMService:
    """Swappable LLM service supporting multiple providers"""

    def __init__(self):
        provider = Config.LLM_PROVIDER

        if provider == "openai":
            from .openai_adapter import OpenAIAdapter
            self.adapter = OpenAIAdapter()
        elif provider == "gemini":
            from .gemini_adapter import GeminiAdapter
            self.adapter = GeminiAdapter()
        elif provider == "claude":
            from .claude_adapter import ClaudeAdapter
            self.adapter = ClaudeAdapter()
        else:
            from .ollama_adapter import OllamaAdapter
            self.adapter = OllamaAdapter()

        self.provider = provider

    def chat(self, messages, system_prompt=None, temperature=0.7):
        """Send chat messages and get response"""
        return self.adapter.chat(messages, system_prompt, temperature)

    def stream_chat(self, messages, system_prompt=None):
        """Stream chat responses"""
        return self.adapter.stream_chat(messages, system_prompt)

    def generate_image(self, prompt):
        """Generate image from prompt (if supported)"""
        if hasattr(self.adapter, 'generate_image'):
            return self.adapter.generate_image(prompt)
        raise NotImplementedError(f"{self.provider} doesn't support image generation")


# Singleton instance
_llm_service = None


def get_llm_service():
    """Get LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
