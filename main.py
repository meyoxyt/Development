#!/usr/bin/env python3
"""Main entry point for Minimax 2.1 AI Assistant"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from config import Config
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor
from utils.logger import setup_logger

console = Console()
logger = setup_logger(__name__)

class AIAssistant:
    """Main AI Assistant application"""
    
    def __init__(self):
        self.client = MinimaxClient()
        self.executor = ToolExecutor()
        self.conversation_history = []
        
    async def process_query(self, query: str) -> str:
        """Process user query and execute tools"""
        logger.info(f"Processing query: {query}")
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": query})
        
        iteration = 0
        while iteration < Config.MAX_TOOL_ITERATIONS:
            # Get AI response
            response = await self.client.chat(
                messages=self.conversation_history,
                tools=self.executor.get_tool_definitions()
            )
            
            # Check if AI wants to use tools
            if response.get("tool_calls"):
                console.print("[yellow]AI is using tools...[/yellow]")
                
                # Execute tools
                tool_results = await self.executor.execute_tools(response["tool_calls"])
                
                # Add tool results to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.get("content", ""),
                    "tool_calls": response["tool_calls"]
                })
                
                for result in tool_results:
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "content": result["output"]
                    })
                
                iteration += 1
            else:
                # No more tools needed, return final response
                final_response = response.get("content", "")
                self.conversation_history.append({"role": "assistant", "content": final_response})
                return final_response
        
        return "Maximum tool iterations reached."
    
    async def interactive_mode(self):
        """Run in interactive mode"""
        console.print("[bold green]Minimax 2.1 AI Assistant[/bold green]")
        console.print("Type 'exit' or 'quit' to end session\n")
        
        session = PromptSession(history=FileHistory(".ai_history"))
        
        while True:
            try:
                user_input = await session.prompt_async("You: ")
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Process query
                response = await self.process_query(user_input)
                
                # Display response
                console.print("\n[bold cyan]AI:[/bold cyan]")
                console.print(Markdown(response))
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Error in interactive mode")

@click.command()
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.option("--query", "-q", type=str, help="Single query to process")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(interactive: bool, query: Optional[str], verbose: bool):
    """Minimax 2.1 AI Assistant with comprehensive tool suite"""
    
    if verbose:
        Config.LOG_LEVEL = "DEBUG"
    
    # Create workspace directory
    Config.WORKSPACE_DIR.mkdir(exist_ok=True)
    
    assistant = AIAssistant()
    
    if interactive:
        # Interactive mode
        asyncio.run(assistant.interactive_mode())
    elif query:
        # Single query mode
        response = asyncio.run(assistant.process_query(query))
        console.print(Markdown(response))
    else:
        console.print("[yellow]Please specify --interactive or --query[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main()
