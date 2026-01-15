"""
Utility functions for the Fingerprinting Agent.
Provides helpers for command execution, evidence tracking, and data formatting.
"""

import subprocess
import platform
import uuid
from enum import Enum
from typing import Dict, Tuple, Optional
from datetime import datetime


class ProductFamily(Enum):
    """Standardized product family categories."""
    IDE = "IDE"
    BROWSER = "Browser"
    VIRTUALIZATION = "Virtualization"
    COMMUNICATION = "Communication"
    PROGRAMMING_LANGUAGE = "Programming Language"
    VERSION_CONTROL = "Version Control"
    DATABASE = "Database"
    RUNTIME = "Runtime"
    CONTAINER = "Container"
    CLOUD_TOOLS = "Cloud Tools"
    SECURITY = "Security"
    MONITORING = "Monitoring"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class Evidence:
    """Tracks evidence for data collection."""
    
    def __init__(self, command: str, raw_output: str):
        self.command = command
        self.raw_output = raw_output
    
    def to_dict(self) -> Dict[str, str]:
        """Convert evidence to dictionary format."""
        return {
            "command_run": self.command,
            "raw_output": self.raw_output
        }


def execute_command(command: str, timeout: int = 30) -> Tuple[bool, str]:
    """
    Execute a shell command and return success status and output.
    
    Args:
        command: Shell command to execute
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Combine stdout and stderr
        output = result.stdout.strip()
        if not output and result.stderr:
            output = result.stderr.strip()
            
        return (result.returncode == 0, output)
    except subprocess.TimeoutExpired:
        return (False, f"Command timed out after {timeout} seconds")
    except Exception as e:
        return (False, f"Error executing command: {str(e)}")


def execute_ssh_command(host: str, command: str, username: str = None, 
                       port: int = 22, key_file: str = None, 
                       timeout: int = 30) -> Tuple[bool, str, str]:
    """
    Execute a command on a remote host via SSH using subprocess.
    
    Args:
        host: Remote host IP or hostname
        command: Command to execute on remote host
        username: SSH username (optional, defaults to current user)
        port: SSH port (default: 22)
        key_file: Path to SSH private key (optional)
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (success: bool, output: str, ssh_command: str)
    """
    # Build SSH command
    ssh_parts = ['ssh']
    
    # Add SSH options for non-interactive execution
    ssh_parts.extend([
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', f'ConnectTimeout={timeout}'
    ])
    
    # Add port if non-standard
    if port != 22:
        ssh_parts.extend(['-p', str(port)])
    
    # Add key file if provided
    if key_file:
        ssh_parts.extend(['-i', key_file])
    
    # Add user@host
    if username:
        ssh_parts.append(f'{username}@{host}')
    else:
        ssh_parts.append(host)
    
    # Add the remote command
    ssh_parts.append(command)
    
    # Join into single command
    ssh_command = ' '.join(ssh_parts)
    
    try:
        result = subprocess.run(
            ssh_parts,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Get output
        output = result.stdout.strip()
        if not output and result.stderr:
            # Check if stderr contains actual output or just SSH warnings
            stderr = result.stderr.strip()
            # Filter out SSH warnings
            error_lines = [line for line in stderr.split('\n') 
                          if not line.startswith('Warning:')]
            if error_lines:
                output = '\n'.join(error_lines)
        
        return (result.returncode == 0, output, ssh_command)
        
    except subprocess.TimeoutExpired:
        return (False, f"SSH command timed out after {timeout} seconds", ssh_command)
    except FileNotFoundError:
        return (False, "SSH client not found. Install OpenSSH.", ssh_command)
    except Exception as e:
        return (False, f"SSH error: {str(e)}", ssh_command)


def get_platform_key() -> str:
    """
    Get the platform key for the current system.
    
    Returns:
        'darwin' for macOS, 'linux' for Linux, 'windows' for Windows
    """
    system = platform.system().lower()
    if system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'  # Default fallback


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def generate_agent_id() -> str:
    """
    Generate a unique agent/scan ID.
    
    Returns:
        UUID string for this scan session
    """
    return str(uuid.uuid4())


def clean_output(output: str) -> str:
    """
    Clean command output by removing extra whitespace and newlines.
    
    Args:
        output: Raw command output
        
    Returns:
        Cleaned output string
    """
    return ' '.join(output.split())


def extract_version(output: str) -> Optional[str]:
    """
    Extract version number from command output.
    
    Args:
        output: Command output containing version info
        
    Returns:
        Extracted version string or None
    """
    import re
    
    # Common version patterns
    patterns = [
        r'(\d+\.\d+\.\d+\.\d+)',  # x.x.x.x
        r'(\d+\.\d+\.\d+)',        # x.x.x
        r'(\d+\.\d+)',             # x.x
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1)
    
    return None


def format_report(agent_metadata: Dict, system_info: Dict, software_inventory: list) -> Dict:
    """
    Format the final fingerprinting report.
    
    Args:
        agent_metadata: Metadata about the scan
        system_info: System information
        software_inventory: List of detected software
        
    Returns:
        Formatted report dictionary
    """
    return {
        "agent_metadata": agent_metadata,
        "system_info": system_info,
        "software_inventory": software_inventory
    }


def log_message(message: str, level: str = "INFO"):
    """
    Log a message with timestamp.
    
    Args:
        message: Message to log
        level: Log level (INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")
