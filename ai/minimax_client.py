"""Minimax AI Client - supports both Ollama and Cloud API"""

import aiohttp
import json
from typing import List, Dict, Optional
from utils.logger import setup_logger
from config import Config

logger = setup_logger(__name__)

class MinimaxClient:
    """Client for interacting with Minimax AI (Ollama or Cloud)"""
    
    def __init__(self):
        self.use_ollama = Config.USE_OLLAMA
        self.ollama_host = Config.OLLAMA_HOST
        self.ollama_model = Config.OLLAMA_MODEL
        
        if self.use_ollama:
            logger.info(f"Using Ollama at {self.ollama_host}")
        else:
            self.api_key = Config.MINIMAX_API_KEY
            self.group_id = Config.MINIMAX_GROUP_ID
            self.api_url = Config.MINIMAX_API_URL
            logger.info("Using Minimax Cloud API")
    
    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict:
        """Send chat request to AI"""
        if self.use_ollama:
            return await self._chat_ollama(messages, tools)
        else:
            return await self._chat_cloud(messages, tools)
    
    async def _chat_ollama(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict:
        """Chat using Ollama (correct endpoint)"""
        url = f"{self.ollama_host}/v1/chat/completions"
        
        payload = {
            "model": self.ollama_model,
            "messages": messages,
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
                    
                    result = {
                        "content": message.get("content", ""),
                        "role": "assistant"
                    }
                    
                    if "tool_calls" in message:
                        result["tool_calls"] = message["tool_calls"]
                    
                    return result
        
        except aiohttp.ClientError as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def _chat_cloud(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict:
        """Chat using Minimax Cloud API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": Config.MINIMAX_MODEL,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    choice = data["choices"][0]
                    message = choice["message"]
                    
                    result = {
                        "content": message.get("content", ""),
                        "role": "assistant"
                    }
                    
                    if "tool_calls" in message:
                        result["tool_calls"] = message["tool_calls"]
                    
                    return result
        
        except aiohttp.ClientError as e:
            logger.error(f"Minimax Cloud API error: {e}")
            raise
