"""Git integration tools"""

import subprocess
from pathlib import Path
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class GitTools:
    """Git repository operations"""
    
    def __init__(self):
        self.workspace = Config.WORKSPACE_DIR
    
    def _run_git(self, *args) -> str:
        """Run git command"""
        try:
            result = subprocess.run(
                ['git'] + list(args),
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += result.stderr
            
            return output.strip()
            
        except Exception as e:
            logger.error(f"Git command error: {e}")
            return f"Error: {str(e)}"
    
    async def git_status(self) -> str:
        """Get git repository status"""
        try:
            output = self._run_git('status', '--short')
            if not output:
                output = "Working tree clean"
            
            logger.info("Git status retrieved")
            return output
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def git_diff(self, file: str = None) -> str:
        """Show git diff"""
        try:
            if file:
                output = self._run_git('diff', file)
            else:
                output = self._run_git('diff')
            
            if not output:
                output = "No changes"
            
            # Limit output
            if len(output) > 5000:
                output = output[:5000] + f"\n... truncated ({len(output)} total chars)"
            
            logger.info(f"Git diff retrieved{' for ' + file if file else ''}")
            return output
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def git_log(self, n: int = 10) -> str:
        """Show git commit history"""
        try:
            output = self._run_git(
                'log',
                f'-{n}',
                '--pretty=format:%h - %an, %ar : %s'
            )
            
            if not output:
                output = "No commits"
            
            logger.info(f"Git log retrieved ({n} commits)")
            return output
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def git_commit(self, message: str) -> str:
        """Commit changes"""
        try:
            # Add all changes
            self._run_git('add', '-A')
            
            # Commit
            output = self._run_git('commit', '-m', message)
            
            logger.info(f"Git commit: {message}")
            return output
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def git_branch(self) -> str:
        """List git branches"""
        try:
            output = self._run_git('branch', '-a')
            
            logger.info("Git branches listed")
            return output
            
        except Exception as e:
            return f"Error: {str(e)}"
