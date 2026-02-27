#!/usr/bin/env python3
"""Basic usage examples for Minimax AI Assistant"""

import asyncio
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor
from config import Config

async def example_file_operations():
    """Example: File operations with AI"""
    print("\n=== Example 1: File Operations ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    messages = [{
        "role": "user",
        "content": "Create a file called hello.txt with the content 'Hello from Minimax AI!'"
    }]
    
    # Get AI response with tools
    response = await client.chat(messages, tools=executor.get_tool_definitions())
    
    if response.get("tool_calls"):
        print("AI is using tools...")
        results = await executor.execute_tools(response["tool_calls"])
        for result in results:
            print(f"Tool result: {result['output']}")

async def example_search():
    """Example: Search files"""
    print("\n=== Example 2: Search Files ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    messages = [{
        "role": "user",
        "content": "Find all Python files in the current directory"
    }]
    
    response = await client.chat(messages, tools=executor.get_tool_definitions())
    
    if response.get("tool_calls"):
        results = await executor.execute_tools(response["tool_calls"])
        for result in results:
            print(f"Found files:\n{result['output']}")

async def example_system_info():
    """Example: Get system information"""
    print("\n=== Example 3: System Information ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    messages = [{
        "role": "user",
        "content": "Show me system information including CPU and memory usage"
    }]
    
    response = await client.chat(messages, tools=executor.get_tool_definitions())
    
    if response.get("tool_calls"):
        results = await executor.execute_tools(response["tool_calls"])
        for result in results:
            print(result['output'])

async def example_multi_step():
    """Example: Multi-step task with AI deciding what to do"""
    print("\n=== Example 4: Multi-Step Task ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    conversation = [{
        "role": "user",
        "content": "Create a project structure: make a directory called 'myproject', then create files README.md and main.py inside it"
    }]
    
    # AI will make multiple tool calls
    for i in range(5):
        response = await client.chat(conversation, tools=executor.get_tool_definitions())
        
        if response.get("tool_calls"):
            print(f"\nStep {i+1}: AI is executing tools...")
            results = await executor.execute_tools(response["tool_calls"])
            
            # Add to conversation
            conversation.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": response["tool_calls"]
            })
            
            for result in results:
                conversation.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["output"]
                })
        else:
            print(f"\nFinal response: {response.get('content', '')}")
            break

async def example_code_formatting():
    """Example: Code analysis and formatting"""
    print("\n=== Example 5: Code Tools ===")
    
    # First create a messy Python file
    from tools.file_ops import FileOperations
    file_ops = FileOperations()
    
    messy_code = '''
def hello(  ):
  print( "hello"  )
  return   42

if __name__=="__main__":
    hello()
'''
    
    await file_ops.write_file("messy.py", messy_code)
    print("Created messy.py")
    
    # Ask AI to format it
    client = MinimaxClient()
    executor = ToolExecutor()
    
    messages = [{
        "role": "user",
        "content": "Format the file messy.py using Black formatter"
    }]
    
    response = await client.chat(messages, tools=executor.get_tool_definitions())
    
    if response.get("tool_calls"):
        results = await executor.execute_tools(response["tool_calls"])
        for result in results:
            print(result['output'])

async def main():
    """Run all examples"""
    print("Minimax 2.1 AI Assistant - Usage Examples")
    print("="*50)
    
    # Ensure workspace exists
    Config.WORKSPACE_DIR.mkdir(exist_ok=True)
    
    await example_file_operations()
    await example_search()
    await example_system_info()
    await example_multi_step()
    await example_code_formatting()
    
    print("\n" + "="*50)
    print("Examples completed!")

if __name__ == "__main__":
    asyncio.run(main())
