#!/usr/bin/env python3
"""Modern Web Application for Minimax 2.1 AI Assistant"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import markdown
import threading

from config import Config
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'minimax-dev-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize AI components
client = MinimaxClient()
executor = ToolExecutor()

# Workspaces storage
WORKSPACES_DIR = Path("workspaces")
WORKSPACES_DIR.mkdir(exist_ok=True)

class Workspace:
    def __init__(self, id: str, name: str, path: str):
        self.id = id
        self.name = name
        self.path = path
        self.messages: List[Dict] = []
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "messages": self.messages,
            "created_at": self.created_at
        }
    
    def save(self):
        file_path = WORKSPACES_DIR / f"{self.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load(workspace_id: str) -> Optional['Workspace']:
        file_path = WORKSPACES_DIR / f"{workspace_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        workspace = Workspace(data['id'], data['name'], data['path'])
        workspace.messages = data.get('messages', [])
        workspace.created_at = data.get('created_at', datetime.now().isoformat())
        return workspace
    
    @staticmethod
    def list_all() -> List['Workspace']:
        workspaces = []
        for file in WORKSPACES_DIR.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                workspace = Workspace(data['id'], data['name'], data['path'])
                workspace.messages = data.get('messages', [])
                workspaces.append(workspace)
            except Exception as e:
                logger.error(f"Failed to load workspace {file}: {e}")
        return workspaces

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/workspaces', methods=['GET'])
def get_workspaces():
    workspaces = Workspace.list_all()
    return jsonify([w.to_dict() for w in workspaces])

@app.route('/api/workspaces', methods=['POST'])
def create_workspace():
    data = request.json
    workspace_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = Workspace(workspace_id, data['name'], data['path'])
    workspace.save()
    return jsonify(workspace.to_dict())

@app.route('/api/workspaces/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    workspace = Workspace.load(workspace_id)
    if workspace:
        return jsonify(workspace.to_dict())
    return jsonify({'error': 'Workspace not found'}), 404

@app.route('/api/workspaces/<workspace_id>/messages', methods=['POST'])
def add_message(workspace_id):
    workspace = Workspace.load(workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    
    data = request.json
    message = {
        'role': data['role'],
        'content': data['content'],
        'timestamp': datetime.now().isoformat()
    }
    workspace.messages.append(message)
    workspace.save()
    return jsonify(message)

@socketio.on('send_message')
def handle_message(data):
    workspace_id = data['workspace_id']
    user_message = data['message']
    
    workspace = Workspace.load(workspace_id)
    if not workspace:
        emit('error', {'message': 'Workspace not found'})
        return
    
    # Add user message
    user_msg = {
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    }
    workspace.messages.append(user_msg)
    workspace.save()
    
    emit('message_received', user_msg)
    emit('ai_thinking', {'status': True})
    
    # Process AI response in background
    def process_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Prepare conversation history
            messages = [{'role': m['role'], 'content': m['content']} for m in workspace.messages]
            
            # Get AI response
            response = loop.run_until_complete(
                client.chat(messages, tools=executor.get_tool_definitions())
            )
            
            ai_content = response.get('content', 'No response')
            
            # Render markdown
            ai_html = markdown.markdown(ai_content, extensions=['fenced_code', 'codehilite', 'tables'])
            
            ai_msg = {
                'role': 'assistant',
                'content': ai_content,
                'html': ai_html,
                'timestamp': datetime.now().isoformat()
            }
            
            workspace.messages.append(ai_msg)
            workspace.save()
            
            socketio.emit('ai_response', ai_msg)
            socketio.emit('ai_thinking', {'status': False})
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            socketio.emit('error', {'message': str(e)})
            socketio.emit('ai_thinking', {'status': False})
        finally:
            loop.close()
    
    thread = threading.Thread(target=process_async)
    thread.start()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Minimax 2.1 AI Assistant - Web Interface")
    print("="*50)
    print(f"Open your browser at: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
