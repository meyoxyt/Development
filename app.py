#!/usr/bin/env python3
"""Flask Web Application for Minimax 2.1 AI Assistant"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from config import Config
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'minimax-ai-assistant-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize AI components
client = MinimaxClient()
executor = ToolExecutor()

# Workspaces storage
WORKSPACES_DIR = Path("workspaces")
WORKSPACES_DIR.mkdir(exist_ok=True)

class WorkspaceManager:
    """Manage workspaces and their data"""
    
    @staticmethod
    def list_workspaces() -> List[Dict]:
        """List all workspaces"""
        workspaces = []
        for file in WORKSPACES_DIR.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    workspaces.append({
                        "id": file.stem,
                        "name": data["name"],
                        "path": data["path"],
                        "created_at": data["created_at"],
                        "message_count": len(data.get("messages", []))
                    })
            except Exception as e:
                logger.error(f"Failed to load workspace {file}: {e}")
        return sorted(workspaces, key=lambda x: x["created_at"], reverse=True)
    
    @staticmethod
    def create_workspace(name: str, path: str) -> Dict:
        """Create a new workspace"""
        workspace_id = name.lower().replace(" ", "-")
        workspace_data = {
            "name": name,
            "path": path,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        workspace_file = WORKSPACES_DIR / f"{workspace_id}.json"
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(workspace_data, f, indent=2)
        
        return {
            "id": workspace_id,
            "name": name,
            "path": path,
            "created_at": workspace_data["created_at"],
            "message_count": 0
        }
    
    @staticmethod
    def get_workspace(workspace_id: str) -> Optional[Dict]:
        """Get workspace data"""
        workspace_file = WORKSPACES_DIR / f"{workspace_id}.json"
        if not workspace_file.exists():
            return None
        
        with open(workspace_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_workspace(workspace_id: str, data: Dict):
        """Save workspace data"""
        workspace_file = WORKSPACES_DIR / f"{workspace_id}.json"
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def delete_workspace(workspace_id: str):
        """Delete a workspace"""
        workspace_file = WORKSPACES_DIR / f"{workspace_id}.json"
        if workspace_file.exists():
            workspace_file.unlink()

manager = WorkspaceManager()

# Routes
@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/workspaces', methods=['GET'])
def get_workspaces():
    """Get all workspaces"""
    return jsonify(manager.list_workspaces())

@app.route('/api/workspaces', methods=['POST'])
def create_workspace():
    """Create a new workspace"""
    data = request.json
    workspace = manager.create_workspace(data['name'], data['path'])
    return jsonify(workspace)

@app.route('/api/workspaces/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """Get workspace details"""
    workspace = manager.get_workspace(workspace_id)
    if not workspace:
        return jsonify({"error": "Workspace not found"}), 404
    return jsonify(workspace)

@app.route('/api/workspaces/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """Delete a workspace"""
    manager.delete_workspace(workspace_id)
    return jsonify({"success": True})

@app.route('/api/workspaces/<workspace_id>/path', methods=['PUT'])
def update_workspace_path(workspace_id):
    """Update workspace path"""
    workspace = manager.get_workspace(workspace_id)
    if not workspace:
        return jsonify({"error": "Workspace not found"}), 404
    
    data = request.json
    workspace['path'] = data['path']
    manager.save_workspace(workspace_id, workspace)
    return jsonify({"success": True})

# WebSocket events
@socketio.on('send_message')
def handle_message(data):
    """Handle incoming chat message"""
    workspace_id = data['workspace_id']
    user_message = data['message']
    
    # Load workspace
    workspace = manager.get_workspace(workspace_id)
    if not workspace:
        emit('error', {"message": "Workspace not found"})
        return
    
    # Add user message
    message_data = {
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    }
    workspace['messages'].append(message_data)
    manager.save_workspace(workspace_id, workspace)
    
    # Emit user message
    emit('message', message_data)
    
    # Process AI response
    try:
        # Get conversation history
        messages = [{"role": m["role"], "content": m["content"]} 
                   for m in workspace['messages']]
        
        # Run async chat in thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get AI response
        response = loop.run_until_complete(
            client.chat(messages, tools=executor.get_tool_definitions())
        )
        
        # Execute tools if needed
        if response.get("tool_calls"):
            tool_results = loop.run_until_complete(
                executor.execute_tools(response["tool_calls"])
            )
            # Emit tool execution updates
            for result in tool_results:
                emit('tool_execution', result)
        
        loop.close()
        
        # Add AI response
        ai_message = {
            "role": "assistant",
            "content": response.get("content", "No response"),
            "timestamp": datetime.now().isoformat()
        }
        workspace['messages'].append(ai_message)
        manager.save_workspace(workspace_id, workspace)
        
        # Emit AI message
        emit('message', ai_message)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        emit('error', {"message": str(e)})

@socketio.on('edit_message')
def handle_edit_message(data):
    """Handle message edit"""
    workspace_id = data['workspace_id']
    message_index = data['message_index']
    new_content = data['content']
    
    workspace = manager.get_workspace(workspace_id)
    if not workspace:
        emit('error', {"message": "Workspace not found"})
        return
    
    if message_index < len(workspace['messages']):
        workspace['messages'][message_index]['content'] = new_content
        workspace['messages'][message_index]['edited'] = True
        workspace['messages'][message_index]['edited_at'] = datetime.now().isoformat()
        manager.save_workspace(workspace_id, workspace)
        emit('message_edited', {
            "message_index": message_index,
            "content": new_content
        })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Minimax 2.1 AI Assistant - Web Interface")
    print("="*50)
    print(f"\nUsing Ollama: {Config.USE_OLLAMA}")
    print(f"Model: {Config.OLLAMA_MODEL}")
    print(f"Host: {Config.OLLAMA_HOST}")
    print("\nStarting web server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
