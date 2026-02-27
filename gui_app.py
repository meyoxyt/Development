#!/usr/bin/env python3
"""Modern GUI Application for Minimax 2.1 AI Assistant"""

import customtkinter as ctk
import asyncio
import threading
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import markdown
from tkinter import filedialog

from config import Config
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatMessage:
    """Represents a single chat message"""
    def __init__(self, role: str, content: str, timestamp: datetime):
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.editing = False

class Workspace:
    """Represents a chat workspace"""
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        
    def add_message(self, role: str, content: str):
        self.messages.append(ChatMessage(role, content, datetime.now()))
    
    def save(self):
        """Save workspace to disk"""
        data = {
            "name": self.name,
            "path": str(self.path),
            "created_at": self.created_at.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.messages
            ]
        }
        
        workspace_file = Path("workspaces") / f"{self.name}.json"
        workspace_file.parent.mkdir(exist_ok=True)
        
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load(workspace_file: Path) -> 'Workspace':
        """Load workspace from disk"""
        with open(workspace_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        workspace = Workspace(data["name"], Path(data["path"]))
        workspace.created_at = datetime.fromisoformat(data["created_at"])
        
        for msg_data in data["messages"]:
            msg = ChatMessage(
                msg_data["role"],
                msg_data["content"],
                datetime.fromisoformat(msg_data["timestamp"])
            )
            workspace.messages.append(msg)
        
        return workspace

class MinimaxGUI(ctk.CTk):
    """Main GUI Application"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Minimax 2.1 AI Assistant")
        self.geometry("1400x900")
        
        # Set DM Sans font
        self.default_font = ("DM Sans", 14)
        self.heading_font = ("DM Sans", 18, "bold")
        self.title_font = ("DM Sans", 24, "bold")
        
        # Colors (Black & White theme)
        self.bg_color = "#000000"
        self.fg_color = "#FFFFFF"
        self.sidebar_color = "#0A0A0A"
        self.message_bg_user = "#1A1A1A"
        self.message_bg_ai = "#0F0F0F"
        self.border_color = "#2A2A2A"
        self.hover_color = "#1F1F1F"
        
        # Initialize AI components
        self.client = MinimaxClient()
        self.executor = ToolExecutor()
        
        # Current workspace
        self.current_workspace: Optional[Workspace] = None
        self.workspaces: List[Workspace] = []
        
        # Load existing workspaces
        self.load_workspaces()
        
        # Build UI
        self.build_ui()
        
        # Event loop for async operations
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_event_loop, daemon=True)
        self.thread.start()
    
    def start_event_loop(self):
        """Start async event loop in background thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def build_ui(self):
        """Build the main UI"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.build_sidebar()
        
        # Main chat area
        self.build_chat_area()
    
    def build_sidebar(self):
        """Build left sidebar with workspaces"""
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            self.sidebar,
            text="Workspaces",
            font=self.heading_font,
            text_color=self.fg_color
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Workspace list
        self.workspace_list = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color=self.sidebar_color,
            corner_radius=0
        )
        self.workspace_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # New workspace button
        new_workspace_btn = ctk.CTkButton(
            self.sidebar,
            text="+ New Workspace",
            command=self.create_new_workspace,
            font=self.default_font,
            fg_color=self.fg_color,
            text_color=self.bg_color,
            hover_color="#E0E0E0",
            corner_radius=8,
            height=40
        )
        new_workspace_btn.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        # Settings button
        settings_btn = ctk.CTkButton(
            self.sidebar,
            text="⚙ Settings",
            command=self.open_settings,
            font=self.default_font,
            fg_color=self.sidebar_color,
            text_color=self.fg_color,
            hover_color=self.hover_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=8,
            height=40
        )
        settings_btn.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Refresh workspace list
        self.refresh_workspace_list()
    
    def build_chat_area(self):
        """Build main chat area"""
        self.chat_container = ctk.CTkFrame(self, fg_color=self.bg_color, corner_radius=0)
        self.chat_container.grid(row=0, column=1, sticky="nsew")
        self.chat_container.grid_columnconfigure(0, weight=1)
        self.chat_container.grid_rowconfigure(1, weight=1)
        
        # Top bar with workspace info
        self.build_top_bar()
        
        # Messages area
        self.messages_frame = ctk.CTkScrollableFrame(
            self.chat_container,
            fg_color=self.bg_color,
            corner_radius=0
        )
        self.messages_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.messages_frame.grid_columnconfigure(0, weight=1)
        
        # Input area
        self.build_input_area()
    
    def build_top_bar(self):
        """Build top bar with workspace name and path"""
        top_bar = ctk.CTkFrame(self.chat_container, fg_color=self.sidebar_color, height=70, corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)
        
        # Workspace name
        self.workspace_title = ctk.CTkLabel(
            top_bar,
            text="No Workspace Selected",
            font=self.title_font,
            text_color=self.fg_color
        )
        self.workspace_title.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="w")
        
        # Workspace path
        self.workspace_path_label = ctk.CTkLabel(
            top_bar,
            text="",
            font=("DM Sans", 12),
            text_color="#888888"
        )
        self.workspace_path_label.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="w")
        
        # Change path button
        self.change_path_btn = ctk.CTkButton(
            top_bar,
            text="📁 Change Location",
            command=self.change_workspace_path,
            font=self.default_font,
            fg_color=self.sidebar_color,
            text_color=self.fg_color,
            hover_color=self.hover_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=8,
            width=150,
            height=35
        )
        self.change_path_btn.grid(row=0, column=1, rowspan=2, padx=30, pady=15)
    
    def build_input_area(self):
        """Build message input area"""
        input_container = ctk.CTkFrame(self.chat_container, fg_color=self.bg_color, height=120, corner_radius=0)
        input_container.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        input_container.grid_columnconfigure(0, weight=1)
        
        # Input textbox
        self.input_text = ctk.CTkTextbox(
            input_container,
            height=80,
            font=self.default_font,
            fg_color=self.message_bg_user,
            text_color=self.fg_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=12,
            wrap="word"
        )
        self.input_text.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
        
        # Send button
        self.send_btn = ctk.CTkButton(
            input_container,
            text="Send",
            command=self.send_message,
            font=self.heading_font,
            fg_color=self.fg_color,
            text_color=self.bg_color,
            hover_color="#E0E0E0",
            corner_radius=12,
            width=120,
            height=80
        )
        self.send_btn.grid(row=0, column=1)
    
    def create_new_workspace(self):
        """Create a new workspace"""
        dialog = ctk.CTkInputDialog(
            text="Enter workspace name:",
            title="New Workspace",
            font=self.default_font
        )
        name = dialog.get_input()
        
        if name:
            # Ask for workspace path
            path = filedialog.askdirectory(title="Select Workspace Location")
            if path:
                workspace = Workspace(name, Path(path))
                workspace.save()
                self.workspaces.append(workspace)
                self.switch_workspace(workspace)
                self.refresh_workspace_list()
    
    def switch_workspace(self, workspace: Workspace):
        """Switch to a different workspace"""
        self.current_workspace = workspace
        self.workspace_title.configure(text=workspace.name)
        self.workspace_path_label.configure(text=str(workspace.path))
        self.refresh_messages()
    
    def change_workspace_path(self):
        """Change current workspace path"""
        if not self.current_workspace:
            return
        
        path = filedialog.askdirectory(title="Select New Workspace Location")
        if path:
            self.current_workspace.path = Path(path)
            self.current_workspace.save()
            self.workspace_path_label.configure(text=path)
            Config.WORKSPACE_DIR = Path(path)
    
    def send_message(self):
        """Send user message and get AI response"""
        if not self.current_workspace:
            self.show_error("Please create or select a workspace first")
            return
        
        user_message = self.input_text.get("1.0", "end-1c").strip()
        if not user_message:
            return
        
        # Clear input
        self.input_text.delete("1.0", "end")
        
        # Add user message
        self.current_workspace.add_message("user", user_message)
        self.add_message_to_ui("user", user_message)
        
        # Disable send button
        self.send_btn.configure(state="disabled", text="Thinking...")
        
        # Process in background
        future = asyncio.run_coroutine_threadsafe(
            self.process_ai_response(user_message),
            self.loop
        )
        future.add_done_callback(lambda f: self.after(0, self.handle_ai_response, f))
    
    async def process_ai_response(self, user_message: str) -> str:
        """Process AI response asynchronously"""
        try:
            messages = []
            for msg in self.current_workspace.messages:
                messages.append({"role": msg.role, "content": msg.content})
            
            # Get AI response with tools
            response = await self.client.chat(messages, tools=self.executor.get_tool_definitions())
            
            # Execute tools if needed
            if response.get("tool_calls"):
                await self.executor.execute_tools(response["tool_calls"])
            
            return response.get("content", "No response")
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return f"Error: {str(e)}"
    
    def handle_ai_response(self, future):
        """Handle AI response in main thread"""
        try:
            ai_response = future.result()
            self.current_workspace.add_message("assistant", ai_response)
            self.add_message_to_ui("assistant", ai_response)
            self.current_workspace.save()
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.send_btn.configure(state="normal", text="Send")
    
    def add_message_to_ui(self, role: str, content: str):
        """Add message bubble to UI"""
        # Message container
        msg_frame = ctk.CTkFrame(
            self.messages_frame,
            fg_color=self.message_bg_user if role == "user" else self.message_bg_ai,
            corner_radius=16,
            border_width=1,
            border_color=self.border_color
        )
        msg_frame.grid(sticky="ew", pady=10, padx=20 if role == "assistant" else 100)
        
        # Role label
        role_label = ctk.CTkLabel(
            msg_frame,
            text="You" if role == "user" else "AI Assistant",
            font=("DM Sans", 12, "bold"),
            text_color="#AAAAAA"
        )
        role_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        # Render markdown content
        html_content = markdown.markdown(content)
        
        # Content label
        content_label = ctk.CTkLabel(
            msg_frame,
            text=content,
            font=self.default_font,
            text_color=self.fg_color,
            wraplength=800,
            justify="left"
        )
        content_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    def refresh_messages(self):
        """Refresh all messages in current workspace"""
        # Clear messages frame
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        if self.current_workspace:
            for msg in self.current_workspace.messages:
                self.add_message_to_ui(msg.role, msg.content)
    
    def refresh_workspace_list(self):
        """Refresh sidebar workspace list"""
        for widget in self.workspace_list.winfo_children():
            widget.destroy()
        
        for workspace in self.workspaces:
            btn = ctk.CTkButton(
                self.workspace_list,
                text=workspace.name,
                command=lambda w=workspace: self.switch_workspace(w),
                font=self.default_font,
                fg_color=self.sidebar_color if workspace != self.current_workspace else self.hover_color,
                text_color=self.fg_color,
                hover_color=self.hover_color,
                anchor="w",
                corner_radius=8,
                height=45
            )
            btn.pack(fill="x", pady=5, padx=5)
    
    def load_workspaces(self):
        """Load existing workspaces from disk"""
        workspace_dir = Path("workspaces")
        if workspace_dir.exists():
            for file in workspace_dir.glob("*.json"):
                try:
                    workspace = Workspace.load(file)
                    self.workspaces.append(workspace)
                except Exception as e:
                    logger.error(f"Failed to load workspace {file}: {e}")
    
    def open_settings(self):
        """Open settings window"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("600x400")
        settings_window.transient(self)
        
        label = ctk.CTkLabel(
            settings_window,
            text="Settings",
            font=self.title_font
        )
        label.pack(pady=20)
        
        # Add settings options here
    
    def show_error(self, message: str):
        """Show error dialog"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("400x150")
        error_dialog.transient(self)
        
        label = ctk.CTkLabel(
            error_dialog,
            text=message,
            font=self.default_font,
            wraplength=350
        )
        label.pack(pady=30)
        
        ok_btn = ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy,
            width=100
        )
        ok_btn.pack(pady=10)

def main():
    """Run the GUI application"""
    app = MinimaxGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
