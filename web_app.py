#!/usr/bin/env python3
"""Modern Web Application for Minimax 2.1 AI Assistant"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import secrets

from config import Config
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize AI components
client = MinimaxClient()
executor = ToolExecutor()

# Store workspaces in memory (later can move to DB)
workspaces: Dict[str, Dict] = {}

def load_workspaces():
    """Load workspaces from disk"""
    workspace_dir = Path("workspaces")
    workspace_dir.mkdir(exist_ok=True)
    
    for file in workspace_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                workspaces[data['id']] = data
        except Exception as e:
            logger.error(f"Failed to load workspace {file}: {e}")

def save_workspace(workspace: Dict):
    """Save workspace to disk"""
    workspace_dir = Path("workspaces")
    workspace_dir.mkdir(exist_ok=True)
    
    file_path = workspace_dir / f"{workspace['id']}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(workspace, f, indent=2)

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/workspaces', methods=['GET'])
def get_workspaces():
    """Get all workspaces"""
    return jsonify(list(workspaces.values()))

@app.route('/api/workspaces', methods=['POST'])
def create_workspace():
    """Create new workspace"""
    data = request.json
    
    workspace_id = secrets.token_hex(8)
    workspace = {
        'id': workspace_id,
        'name': data.get('name', 'Untitled Workspace'),
        'path': data.get('path', str(Config.WORKSPACE_DIR)),
        'messages': [],
        'created_at': datetime.now().isoformat()
    }
    
    workspaces[workspace_id] = workspace
    save_workspace(workspace)
    
    return jsonify(workspace)

@app.route('/api/workspaces/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """Get specific workspace"""
    workspace = workspaces.get(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    return jsonify(workspace)

@app.route('/api/workspaces/<workspace_id>', methods=['PUT'])
def update_workspace(workspace_id):
    """Update workspace"""
    workspace = workspaces.get(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    
    data = request.json
    workspace.update(data)
    save_workspace(workspace)
    
    return jsonify(workspace)

@app.route('/api/workspaces/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """Delete workspace"""
    if workspace_id in workspaces:
        del workspaces[workspace_id]
        
        # Delete file
        file_path = Path("workspaces") / f"{workspace_id}.json"
        if file_path.exists():
            file_path.unlink()
        
        return jsonify({'success': True})
    
    return jsonify({'error': 'Workspace not found'}), 404

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming chat message"""
    workspace_id = data.get('workspace_id')
    user_message = data.get('message')
    
    workspace = workspaces.get(workspace_id)
    if not workspace:
        emit('error', {'message': 'Workspace not found'})
        return
    
    # Add user message
    user_msg = {
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    }
    workspace['messages'].append(user_msg)
    
    # Send to client
    emit('message', user_msg)
    
    # Process AI response in background
    async def process():
        try:
            messages = [{'role': m['role'], 'content': m['content']} for m in workspace['messages']]
            response = await client.chat(messages, tools=executor.get_tool_definitions())
            
            # Execute tools if needed
            if response.get('tool_calls'):
                await executor.execute_tools(response['tool_calls'])
            
            ai_msg = {
                'role': 'assistant',
                'content': response.get('content', 'No response'),
                'timestamp': datetime.now().isoformat()
            }
            workspace['messages'].append(ai_msg)
            save_workspace(workspace)
            
            socketio.emit('message', ai_msg, room=request.sid)
        
        except Exception as e:
            logger.error(f"AI response error: {e}")
            socketio.emit('error', {'message': str(e)}, room=request.sid)
    
    # Run async task
    asyncio.run(process())

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

def main():
    """Run the web application"""
    load_workspaces()
    
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting web server on http://localhost:{port}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()
