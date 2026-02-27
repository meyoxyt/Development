"""Minimax 2.1 API Client"""

import aiohttp
import json
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MinimaxClient:
    """Client for Minimax 2.1 API"""
    
    def __init__(self):
        self.api_key = Config.MINIMAX_API_KEY
        self.group_id = Config.MINIMAX_GROUP_ID
        self.api_url = Config.MINIMAX_API_URL
        self.model = Config.MINIMAX_MODEL
        self.use_ollama = Config.USE_OLLAMA
        
        if self.use_ollama:
            self.ollama_host = Config.OLLAMA_HOST
            logger.info(f"Using Ollama at {self.ollama_host}")
        else:
            logger.info(f"Using Minimax API with model {self.model}")
    
    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send chat request to Minimax API"""
        
        if self.use_ollama:
            return await self._chat_ollama(messages, tools)
        else:
            return await self._chat_minimax(messages, tools)
    
    async def _chat_minimax(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Chat using Minimax Cloud API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.95,
            "stream": False,
            "tokens_to_generate": 2048
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}?GroupId={self.group_id}",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=Config.TIMEOUT_SECONDS)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    
                    result = {
                        "content": message.get("content", ""),
                        "tool_calls": message.get("tool_calls", [])
                    }
                    
                    logger.debug(f"Minimax response: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Minimax API error: {e}")
            raise
    
    async def _chat_ollama(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Chat using Ollama local endpoint"""
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.95
            }
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=Config.TIMEOUT_SECONDS)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    message = data.get("message", {})
                    
                    result = {
                        "content": message.get("content", ""),
                        "tool_calls": message.get("tool_calls", [])
                    }
                    
                    logger.debug(f"Ollama response: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
