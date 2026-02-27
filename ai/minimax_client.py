import aiohttp
import json
from typing import Dict, List, Optional
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MinimaxClient:
    """Client for interacting with Minimax AI via Ollama"""
    
    def __init__(self):
        self.use_ollama = Config.USE_OLLAMA
        self.ollama_host = Config.OLLAMA_HOST
        self.ollama_model = Config.OLLAMA_MODEL
        self.api_key = Config.MINIMAX_API_KEY
        self.group_id = Config.MINIMAX_GROUP_ID
        logger.info(f"Using Ollama at {self.ollama_host}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> Dict:
        """Send chat request to AI"""
        if self.use_ollama:
            return await self._chat_ollama(messages, tools, temperature)
        else:
            return await self._chat_minimax_api(messages, tools, temperature)
    
    async def _chat_ollama(self, messages: List[Dict], tools: Optional[List[Dict]], temperature: float) -> Dict:
        """Chat via Ollama - FIXED ENDPOINT"""
        url = f"{self.ollama_host}/v1/chat/completions"
        
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    choice = data["choices"][0]
                    message = choice["message"]
                    
                    return {
                        "content": message.get("content", ""),
                        "tool_calls": message.get("tool_calls"),
                        "finish_reason": choice.get("finish_reason")
                    }
        
        except aiohttp.ClientResponseError as e:
            logger.error(f"Ollama API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def _chat_minimax_api(self, messages: List[Dict], tools: Optional[List[Dict]], temperature: float) -> Dict:
        """Chat via Minimax Cloud API"""
        url = Config.MINIMAX_API_URL
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": Config.MINIMAX_MODEL,
            "messages": messages,
            "temperature": temperature
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        
        except Exception as e:
            logger.error(f"Minimax API error: {e}")
            raise
