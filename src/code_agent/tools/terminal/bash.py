import os
import re
from typing import Optional

import pexpect
from langchain.tools import tool

from src.code_agent.project import project


class BashTerminal:
    """A keep-alive terminal for executing bash commands."""

    def __init__(self, cwd=None):
        """
        Initialize BashTerminal

        Args:
            cwd: Initial working directory, defaults to current directory
        """
        self.cwd = cwd or os.getcwd()

        # Start bash shell
        self.shell = pexpect.spawn("/bin/bash", encoding="utf-8", echo=False)

        # Set custom prompt for easy command completion detection
        self.prompt = "BASH_TERMINAL_PROMPT> "
        self.shell.sendline(f'PS1="{self.prompt}"')
        self.shell.expect(self.prompt, timeout=5)

        # Change to specified directory
        if cwd:
            self.execute(f'cd "{self.cwd}"')

    def execute(self, command):
        """
        Execute bash command and return output

        Args:
            command: Command to execute

        Returns:
            Command output result (string)
        """
        # Send command
        self.shell.sendline(command)

        # Wait for prompt to appear, indicating command completion
        self.shell.expect(self.prompt, timeout=30)

        # Get output, removing command itself and prompt
        output = self.shell.before

        # Clean output: remove command echo
        lines = output.split("\n")
        if lines and lines[0].strip() == command.strip():
            lines = lines[1:]

        result = "\n".join([line.strip() for line in lines]).strip()
        # Remove terminal control characters
        result = re.sub(r"\x1b\[[0-9;]*m", "", result)
        return result

    def getcwd(self):
        """
        Get current working directory

        Returns:
            Absolute path of current working directory
        """
        result = self.execute("pwd")
        return result.strip()

    def close(self):
        """Close shell session"""
        if self.shell.isalive():
            self.shell.sendline("exit")
            self.shell.close()

    def __del__(self):
        """Destructor, ensure shell is closed"""
        self.close()

    def __enter__(self):
        """Support with statement"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support with statement"""
        self.close()


keep_alive_terminal: BashTerminal | None = None


@tool("bash", parse_docstring=True)
def bash_tool(command: str, reset_cwd: Optional[bool] = False):
    """Execute a standard bash command in a keep-alive shell, and return the output if successful or error message if failed.

    Use this tool to perform:
    - Create directories
    - Install dependencies
    - Start development server
    - Run tests and linting
    - Git operations

    Never use this tool to perform any harmful or dangerous operations.

    Use `ls`, `grep` and `tree` tools for file system operations instead of this tool.

    Args:
        command: The command to execute.
        reset_cwd: Whether to reset the current working directory to the project root directory.
    """
    global keep_alive_terminal
    if keep_alive_terminal is None:
        keep_alive_terminal = BashTerminal(project.root_dir)
    elif reset_cwd:
        keep_alive_terminal.close()
        keep_alive_terminal = BashTerminal(project.root_dir)
    return f"```\n{keep_alive_terminal.execute(command)}\n```"


if __name__ == '__main__':
    print(bash_tool.invoke(
        {"command": "pwd"}
    ))
