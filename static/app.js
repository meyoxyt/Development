// Socket.IO connection
const socket = io();

// State
let currentWorkspace = null;
let workspaces = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadWorkspaces();
    setupEventListeners();
    setupSocketListeners();
});

function setupEventListeners() {
    const messageInput = document.getElementById('messageInput');
    
    // Auto-resize textarea
    messageInput.addEventListener('input', (e) => {
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
    });
    
    // Ctrl+Enter to send
    messageInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            sendMessage();
        }
    });
}

function setupSocketListeners() {
    socket.on('message_received', (message) => {
        displayMessage(message);
    });
    
    socket.on('ai_thinking', (data) => {
        toggleAIThinking(data.status);
    });
    
    socket.on('ai_response', (message) => {
        displayMessage(message);
    });
    
    socket.on('error', (data) => {
        alert('Error: ' + data.message);
        toggleAIThinking(false);
    });
}

async function loadWorkspaces() {
    try {
        const response = await fetch('/api/workspaces');
        workspaces = await response.json();
        renderWorkspaces();
    } catch (error) {
        console.error('Failed to load workspaces:', error);
    }
}

function renderWorkspaces() {
    const list = document.getElementById('workspaceList');
    list.innerHTML = '';
    
    workspaces.forEach(workspace => {
        const item = document.createElement('div');
        item.className = 'workspace-item';
        if (currentWorkspace && workspace.id === currentWorkspace.id) {
            item.classList.add('active');
        }
        
        item.innerHTML = `
            <h4>${workspace.name}</h4>
            <p>${workspace.path}</p>
        `;
        
        item.onclick = () => selectWorkspace(workspace.id);
        list.appendChild(item);
    });
}

async function selectWorkspace(workspaceId) {
    try {
        const response = await fetch(`/api/workspaces/${workspaceId}`);
        currentWorkspace = await response.json();
        
        document.getElementById('workspaceName').textContent = currentWorkspace.name;
        document.getElementById('workspacePath').textContent = currentWorkspace.path;
        document.getElementById('emptyState').style.display = 'none';
        
        renderMessages();
        renderWorkspaces();
    } catch (error) {
        console.error('Failed to select workspace:', error);
    }
}

function renderMessages() {
    const container = document.getElementById('messagesContainer');
    const existingMessages = container.querySelectorAll('.message, .ai-thinking');
    existingMessages.forEach(el => el.remove());
    
    if (currentWorkspace && currentWorkspace.messages) {
        currentWorkspace.messages.forEach(message => {
            displayMessage(message, false);
        });
    }
}

function displayMessage(message, scroll = true) {
    const container = document.getElementById('messagesContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role}`;
    
    const roleDiv = document.createElement('div');
    roleDiv.className = 'message-role';
    roleDiv.textContent = message.role === 'user' ? 'You' : 'AI Assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (message.html) {
        contentDiv.innerHTML = message.html;
    } else {
        contentDiv.innerHTML = marked.parse(message.content);
    }
    
    const timestampDiv = document.createElement('div');
    timestampDiv.className = 'message-timestamp';
    timestampDiv.textContent = new Date(message.timestamp).toLocaleString();
    
    messageDiv.appendChild(roleDiv);
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timestampDiv);
    
    container.appendChild(messageDiv);
    
    if (scroll) {
        container.scrollTop = container.scrollHeight;
    }
}

function toggleAIThinking(show) {
    let thinkingDiv = document.querySelector('.ai-thinking');
    
    if (show) {
        if (!thinkingDiv) {
            thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'ai-thinking show';
            thinkingDiv.innerHTML = `
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span>AI is thinking...</span>
            `;
            document.getElementById('messagesContainer').appendChild(thinkingDiv);
        }
        thinkingDiv.classList.add('show');
    } else {
        if (thinkingDiv) {
            thinkingDiv.remove();
        }
    }
}

function sendMessage() {
    if (!currentWorkspace) {
        alert('Please select a workspace first');
        return;
    }
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    socket.emit('send_message', {
        workspace_id: currentWorkspace.id,
        message: message
    });
    
    input.value = '';
    input.style.height = 'auto';
    
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    document.getElementById('sendText').textContent = 'Sending...';
    
    setTimeout(() => {
        sendBtn.disabled = false;
        document.getElementById('sendText').textContent = 'Send';
    }, 2000);
}

function createWorkspace() {
    showModal(
        'New Workspace',
        `
        <div class="form-group">
            <label>Workspace Name</label>
            <input type="text" id="workspaceName" placeholder="My Workspace" />
        </div>
        <div class="form-group">
            <label>Workspace Path</label>
            <input type="text" id="workspacePath" placeholder="/path/to/workspace" value="./workspace" />
        </div>
        `,
        async () => {
            const name = document.getElementById('workspaceName').value;
            const path = document.getElementById('workspacePath').value;
            
            if (!name || !path) {
                alert('Please fill all fields');
                return;
            }
            
            try {
                const response = await fetch('/api/workspaces', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, path })
                });
                
                const workspace = await response.json();
                workspaces.push(workspace);
                selectWorkspace(workspace.id);
                closeModal();
            } catch (error) {
                alert('Failed to create workspace: ' + error.message);
            }
        }
    );
}

function changeWorkspacePath() {
    if (!currentWorkspace) return;
    
    showModal(
        'Change Workspace Location',
        `
        <div class="form-group">
            <label>New Path</label>
            <input type="text" id="newPath" value="${currentWorkspace.path}" />
        </div>
        `,
        async () => {
            const newPath = document.getElementById('newPath').value;
            if (newPath) {
                currentWorkspace.path = newPath;
                document.getElementById('workspacePath').textContent = newPath;
                closeModal();
            }
        }
    );
}

function openSettings() {
    showModal(
        'Settings',
        `
        <div class="form-group">
            <label>Ollama Host</label>
            <input type="text" value="http://localhost:11434" />
        </div>
        <div class="form-group">
            <label>Model</label>
            <input type="text" value="minimax-2.1:cloud" />
        </div>
        `,
        () => {
            alert('Settings saved!');
            closeModal();
        }
    );
}

function showModal(title, body, onConfirm) {
    const modal = document.getElementById('modal');
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = body;
    
    const confirmBtn = document.getElementById('modalConfirm');
    confirmBtn.onclick = onConfirm;
    
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}
