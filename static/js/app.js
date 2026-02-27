// Initialize Socket.IO
const socket = io();

// State
let currentWorkspace = null;
const workspaces = [];

// DOM Elements
const workspaceList = document.getElementById('workspaceList');
const workspaceName = document.getElementById('workspaceName');
const workspacePath = document.getElementById('workspacePath');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newWorkspaceBtn = document.getElementById('newWorkspaceBtn');
const newWorkspaceModal = document.getElementById('newWorkspaceModal');
const workspaceNameInput = document.getElementById('workspaceNameInput');
const workspacePathInput = document.getElementById('workspacePathInput');
const createWorkspaceBtn = document.getElementById('createWorkspaceBtn');
const cancelWorkspaceBtn = document.getElementById('cancelWorkspaceBtn');
const changePathBtn = document.getElementById('changePathBtn');

// Load workspaces on startup
loadWorkspaces();

// Socket.IO Events
socket.on('connected', (data) => {
    console.log('Connected to server:', data);
});

socket.on('message', (message) => {
    addMessageToUI(message);
    sendBtn.disabled = false;
    sendBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Send
    `;
});

socket.on('error', (error) => {
    console.error('Error:', error);
    alert(`Error: ${error.message}`);
    sendBtn.disabled = false;
    sendBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Send
    `;
});

// Load workspaces
async function loadWorkspaces() {
    try {
        const response = await fetch('/api/workspaces');
        const data = await response.json();
        
        workspaces.length = 0;
        workspaces.push(...data);
        
        renderWorkspaceList();
        
        // Select first workspace if available
        if (workspaces.length > 0) {
            selectWorkspace(workspaces[0]);
        }
    } catch (error) {
        console.error('Failed to load workspaces:', error);
    }
}

// Render workspace list
function renderWorkspaceList() {
    workspaceList.innerHTML = '';
    
    workspaces.forEach(workspace => {
        const item = document.createElement('div');
        item.className = 'workspace-item';
        if (currentWorkspace && workspace.id === currentWorkspace.id) {
            item.classList.add('active');
        }
        item.textContent = workspace.name;
        item.onclick = () => selectWorkspace(workspace);
        
        workspaceList.appendChild(item);
    });
}

// Select workspace
function selectWorkspace(workspace) {
    currentWorkspace = workspace;
    workspaceName.textContent = workspace.name;
    workspacePath.textContent = workspace.path;
    
    // Clear and render messages
    chatMessages.innerHTML = '';
    workspace.messages.forEach(message => addMessageToUI(message));
    
    renderWorkspaceList();
}

// Add message to UI
function addMessageToUI(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role}`;
    
    const time = new Date(message.timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const roleName = message.role === 'user' ? 'You' : 'AI Assistant';
    
    // Convert markdown to HTML
    const contentHTML = marked.parse(message.content);
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">${roleName}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${contentHTML}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message
function sendMessage() {
    if (!currentWorkspace) {
        alert('Please select or create a workspace first');
        return;
    }
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Clear input
    messageInput.value = '';
    
    // Disable send button
    sendBtn.disabled = true;
    sendBtn.innerHTML = `
        <svg class="spinner" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="15 50"/>
        </svg>
        Thinking...
    `;
    
    // Send via socket
    socket.emit('send_message', {
        workspace_id: currentWorkspace.id,
        message: message
    });
}

// Create new workspace
async function createNewWorkspace() {
    const name = workspaceNameInput.value.trim();
    if (!name) {
        alert('Please enter a workspace name');
        return;
    }
    
    const path = workspacePathInput.value.trim() || './workspace';
    
    try {
        const response = await fetch('/api/workspaces', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, path })
        });
        
        const workspace = await response.json();
        workspaces.push(workspace);
        
        selectWorkspace(workspace);
        renderWorkspaceList();
        
        closeModal();
    } catch (error) {
        console.error('Failed to create workspace:', error);
        alert('Failed to create workspace');
    }
}

// Modal functions
function openModal() {
    newWorkspaceModal.classList.add('active');
    workspaceNameInput.value = '';
    workspacePathInput.value = '';
    workspaceNameInput.focus();
}

function closeModal() {
    newWorkspaceModal.classList.remove('active');
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);

messageInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        sendMessage();
    }
});

newWorkspaceBtn.addEventListener('click', openModal);
createWorkspaceBtn.addEventListener('click', createNewWorkspace);
cancelWorkspaceBtn.addEventListener('click', closeModal);

// Close modal on background click
newWorkspaceModal.addEventListener('click', (e) => {
    if (e.target === newWorkspaceModal) {
        closeModal();
    }
});

// Change workspace path
changePathBtn.addEventListener('click', async () => {
    if (!currentWorkspace) return;
    
    const newPath = prompt('Enter new workspace path:', currentWorkspace.path);
    if (newPath && newPath !== currentWorkspace.path) {
        try {
            const response = await fetch(`/api/workspaces/${currentWorkspace.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...currentWorkspace, path: newPath })
            });
            
            const updated = await response.json();
            currentWorkspace.path = updated.path;
            workspacePath.textContent = updated.path;
        } catch (error) {
            console.error('Failed to update workspace:', error);
            alert('Failed to update workspace path');
        }
    }
});

// Add CSS for spinner animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spinner {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
