"""System management tools"""

import os
import platform
import subprocess
import psutil
from typing import List
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SystemTools:
    """System information and process management"""
    
    async def execute_command(self, command: str) -> str:
        """Execute shell command with safety checks"""
        try:
            if not Config.ENABLE_SHELL_COMMANDS:
                return "Error: Shell commands are disabled"
            
            # Safety checks
            for restricted in Config.RESTRICTED_COMMANDS:
                if restricted in command:
                    return f"Error: Command contains restricted pattern: {restricted}"
            
            logger.info(f"Executing command: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"
            
            output += f"\n[EXIT CODE: {result.returncode}]"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Error: Command timeout (30s)"
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return f"Error: {str(e)}"
    
    async def get_system_info(self) -> str:
        """Get system information"""
        try:
            info = [
                f"System: {platform.system()}",
                f"Release: {platform.release()}",
                f"Version: {platform.version()}",
                f"Machine: {platform.machine()}",
                f"Processor: {platform.processor()}",
                f"Python: {platform.python_version()}",
                f"CPU Cores: {psutil.cpu_count()}",
                f"CPU Usage: {psutil.cpu_percent()}%",
                f"Memory Total: {psutil.virtual_memory().total / (1024**3):.2f} GB",
                f"Memory Available: {psutil.virtual_memory().available / (1024**3):.2f} GB",
                f"Memory Usage: {psutil.virtual_memory().percent}%",
                f"Disk Usage: {psutil.disk_usage('/').percent}%"
            ]
            
            return "\n".join(info)
            
        except Exception as e:
            logger.error(f"System info error: {e}")
            return f"Error: {str(e)}"
    
    async def list_processes(self) -> str:
        """List running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append(
                        f"{info['pid']:>6} {info['cpu_percent']:>6.1f}% {info['memory_percent']:>6.1f}% {info['name']}"
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by PID
            processes.sort()
            
            header = f"{'PID':>6} {'CPU%':>6} {'MEM%':>6} NAME\n" + "-" * 50
            output = header + "\n" + "\n".join(processes[:50])
            
            if len(processes) > 50:
                output += f"\n... and {len(processes) - 50} more processes"
            
            return output
            
        except Exception as e:
            logger.error(f"List processes error: {e}")
            return f"Error: {str(e)}"
    
    async def kill_process(self, pid: int) -> str:
        """Terminate a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()
            
            logger.info(f"Killed process {pid} ({proc_name})")
            return f"Successfully terminated process {pid} ({proc_name})"
            
        except psutil.NoSuchProcess:
            return f"Error: No process with PID {pid}"
        except psutil.AccessDenied:
            return f"Error: Access denied to process {pid}"
        except Exception as e:
            logger.error(f"Kill process error: {e}")
            return f"Error: {str(e)}"
    
    async def get_environment_variables(self) -> str:
        """Get environment variables"""
        try:
            env_vars = []
            for key, value in sorted(os.environ.items()):
                # Redact sensitive values
                if any(s in key.upper() for s in ['KEY', 'TOKEN', 'SECRET', 'PASSWORD']):
                    value = '***REDACTED***'
                env_vars.append(f"{key}={value}")
            
            return "\n".join(env_vars[:100])
            
        except Exception as e:
            logger.error(f"Get env vars error: {e}")
            return f"Error: {str(e)}"
