"""OpenAI LLM Adapter"""
from openai import OpenAI
from app.config import Config


class OpenAIAdapter:
    """OpenAI API adapter"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = "gpt-4o"

    def chat(self, messages, system_prompt=None, temperature=0.7):
        """Send chat messages and get response"""
        formatted_messages = []

        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        if isinstance(messages, str):
            formatted_messages.append({"role": "user", "content": messages})
        else:
            formatted_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature
        )

        return response.choices[0].message.content

    def stream_chat(self, messages, system_prompt=None):
        """Stream chat responses"""
        formatted_messages = []

        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        if isinstance(messages, str):
            formatted_messages.append({"role": "user", "content": messages})
        else:
            formatted_messages.extend(messages)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def generate_image(self, prompt):
        """Generate image from prompt"""
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        return response.data[0].url
