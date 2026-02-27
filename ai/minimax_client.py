"""Minimax AI Client with Ollama and Cloud API support"""

import aiohttp
import json
from typing import List, Dict, Optional, Any
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MinimaxClient:
    """Client for Minimax AI via Ollama or Cloud API"""
    
    def __init__(self):
        self.use_ollama = Config.USE_OLLAMA
        self.ollama_host = Config.OLLAMA_HOST
        self.ollama_model = Config.OLLAMA_MODEL
        self.api_key = Config.MINIMAX_API_KEY
        self.group_id = Config.MINIMAX_GROUP_ID
        self.api_url = Config.MINIMAX_API_URL
        
        logger.info(f"Using {'Ollama' if self.use_ollama else 'Cloud API'}")
        if self.use_ollama:
            logger.info(f"Ollama host: {self.ollama_host}, model: {self.ollama_model}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Send chat request and get response"""
        if self.use_ollama:
            return await self._chat_ollama(messages, tools, temperature)
        else:
            return await self._chat_cloud(messages, tools, temperature)
    
    async def _chat_ollama(self, messages: List[Dict], tools: Optional[List], temperature: float) -> Dict:
        """Chat using Ollama - uses OpenAI-compatible API"""
        # Ollama uses /v1/chat/completions endpoint (OpenAI compatible)
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
                    
                    # Extract response
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    
                    result = {
                        "content": message.get("content", ""),
                        "role": "assistant"
                    }
                    
                    # Check for tool calls
                    if "tool_calls" in message:
                        result["tool_calls"] = message["tool_calls"]
                    
                    return result
        
        except aiohttp.ClientError as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def _chat_cloud(self, messages: List[Dict], tools: Optional[List], temperature: float) -> Dict:
        """Chat using Minimax Cloud API"""
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
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Extract response
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    
                    result = {
                        "content": message.get("content", ""),
                        "role": "assistant"
                    }
                    
                    if "tool_calls" in message:
                        result["tool_calls"] = message["tool_calls"]
                    
                    return result
        
        except aiohttp.ClientError as e:
            logger.error(f"Cloud API error: {e}")
            raise
