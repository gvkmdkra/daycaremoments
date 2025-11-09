"""Claude (Anthropic) LLM Adapter"""
from app.config import Config


class ClaudeAdapter:
    """Anthropic Claude adapter"""

    def __init__(self):
        # from anthropic import Anthropic
        # self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20240229"

    def chat(self, messages, system_prompt=None, temperature=0.7):
        """Send chat and get response"""
        # In production with actual API:
        # response = self.client.messages.create(
        #     model=self.model,
        #     system=system_prompt,
        #     messages=messages,
        #     temperature=temperature,
        #     max_tokens=1024
        # )
        # return response.content[0].text

        return "Claude response (demo mode - add ANTHROPIC_API_KEY to enable)"

    def stream_chat(self, messages, system_prompt=None):
        """Stream chat responses"""
        for chunk in ["Claude ", "streaming ", "response"]:
            yield chunk
