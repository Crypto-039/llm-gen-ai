# LLM provider abstraction for easy model swapping
import openai
import asyncio
from typing import Optional, Dict, Any
import os

class LLMProvider:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Generate response asynchronously"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def health_check(self) -> bool:
        """Check if LLM provider is healthy"""
        try:
            await self.generate_async("test", max_tokens=1)
            return True
        except:
            return False
