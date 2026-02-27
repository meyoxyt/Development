#!/usr/bin/env python3
"""Advanced usage examples showing powerful AI capabilities"""

import asyncio
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor

async def example_autonomous_project_setup():
    """Let AI autonomously set up a complete project"""
    print("\n=== Autonomous Project Setup ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    task = """
    Create a complete Python web scraper project with this structure:
    - Create directory 'web_scraper'
    - Inside it, create:
      - main.py with a basic web scraper using requests
      - requirements.txt with requests and beautifulsoup4
      - README.md explaining how to use it
      - .gitignore for Python projects
    
    Make the scraper extract all links from a given URL.
    """
    
    conversation = [{"role": "user", "content": task}]
    
    # Let AI work autonomously
    for iteration in range(10):
        response = await client.chat(conversation, tools=executor.get_tool_definitions())
        
        if response.get("tool_calls"):
            print(f"Iteration {iteration + 1}: Executing {len(response['tool_calls'])} tools...")
            results = await executor.execute_tools(response["tool_calls"])
            
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
            print(f"\nProject setup complete!")
            print(f"AI says: {response.get('content', '')}")
            break

async def example_code_analysis():
    """Analyze and improve code automatically"""
    print("\n=== Code Analysis & Improvement ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    # Create sample code with issues
    from tools.file_ops import FileOperations
    file_ops = FileOperations()
    
    bad_code = '''
import os,sys,json

def calculate(x,y):
    result=x+y
    print(result)
    return result

def unused_function():
    pass

calculate(5,10)
'''
    
    await file_ops.write_file("analyze_me.py", bad_code)
    
    task = """
    Analyze the file analyze_me.py:
    1. Check it with a linter
    2. Format it properly
    3. Read the formatted code and tell me what improvements were made
    """
    
    conversation = [{"role": "user", "content": task}]
    
    for _ in range(10):
        response = await client.chat(conversation, tools=executor.get_tool_definitions())
        
        if response.get("tool_calls"):
            results = await executor.execute_tools(response["tool_calls"])
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
            print(f"\nAnalysis complete: {response.get('content', '')}")
            break

async def example_data_processing():
    """Use AI to process and analyze data"""
    print("\n=== Data Processing ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    # Create sample data file
    from tools.file_ops import FileOperations
    file_ops = FileOperations()
    
    data = """name,age,city
John,25,New York
Alice,30,Los Angeles
Bob,35,Chicago
Carol,28,Houston
"""
    
    await file_ops.write_file("data.csv", data)
    
    task = """
    Process the data.csv file:
    1. Read the file
    2. Create a new file 'summary.txt' with statistics about the data
    3. Create a Python script 'process_data.py' that can parse and display this CSV
    """
    
    conversation = [{"role": "user", "content": task}]
    
    for _ in range(10):
        response = await client.chat(conversation, tools=executor.get_tool_definitions())
        
        if response.get("tool_calls"):
            results = await executor.execute_tools(response["tool_calls"])
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
            print(f"\nData processing complete: {response.get('content', '')}")
            break

async def example_git_workflow():
    """AI-assisted Git workflow"""
    print("\n=== Git Workflow Automation ===")
    
    client = MinimaxClient()
    executor = ToolExecutor()
    
    task = """
    Help me with Git:
    1. Show current git status
    2. Show the last 5 commits
    3. Show git branches
    """
    
    conversation = [{"role": "user", "content": task}]
    
    for _ in range(10):
        response = await client.chat(conversation, tools=executor.get_tool_definitions())
        
        if response.get("tool_calls"):
            results = await executor.execute_tools(response["tool_calls"])
            conversation.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": response["tool_calls"]
            })
            for result in results:
                print(f"Git info: {result['output'][:200]}...")  # Preview
                conversation.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["output"]
                })
        else:
            print(f"\n{response.get('content', '')}")
            break

async def main():
    print("Minimax 2.1 AI Assistant - Advanced Examples")
    print("="*60)
    
    await example_autonomous_project_setup()
    await example_code_analysis()
    await example_data_processing()
    await example_git_workflow()
    
    print("\n" + "="*60)
    print("Advanced examples completed!")

if __name__ == "__main__":
    asyncio.run(main())
