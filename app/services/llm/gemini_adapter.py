"""Google Gemini LLM Adapter"""
import google.generativeai as genai
from app.config import Config


class GeminiAdapter:
    """Google Gemini API adapter"""

    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def chat(self, messages, system_prompt=None, temperature=0.7):
        """Send chat messages and get response"""
        # Combine system prompt with messages
        prompt = ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n"

        if isinstance(messages, str):
            prompt += messages
        else:
            # Format conversation
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt += f"{role}: {content}\n"

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )

        return response.text

    def stream_chat(self, messages, system_prompt=None):
        """Stream chat responses"""
        prompt = ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n"

        if isinstance(messages, str):
            prompt += messages
        else:
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt += f"{role}: {content}\n"

        response = self.model.generate_content(prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text
