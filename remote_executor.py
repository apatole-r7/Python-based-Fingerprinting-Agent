"""
Remote Executor Module
Executes fingerprinting commands on remote systems via SSH using subprocess.
Provides secure, production-ready SSH execution without external dependencies.
"""

import os
from typing import Dict, Optional, Tuple
from utils import log_message, get_timestamp, execute_ssh_command, Evidence


class RemoteExecutor:
    """Executes commands on remote systems via SSH."""
    
    def __init__(self, host: str, username: str = None, key_file: str = None, 
                 port: int = 22, timeout: int = 30):
        """
        Initialize remote executor using subprocess-based SSH.
        
        Args:
            host: Remote host IP or hostname
            username: SSH username (optional, uses current user if not provided)
            key_file: Path to SSH private key file (optional)
            port: SSH port (default: 22)
            timeout: Connection timeout in seconds
        
        Note:
            Requires OpenSSH client installed on the system.
            For key-based auth, ensure proper permissions: chmod 600 key_file
        """
        self.host = host
        self.username = username
        self.key_file = key_file
        self.port = port
        self.timeout = timeout
        self.connected = False
    
    def connect(self) -> bool:
        """
        Test SSH connection to remote host.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            user_host = f"{self.username}@{self.host}" if self.username else self.host
            log_message(f"Testing SSH connection to {user_host}:{self.port}...")
            
            # Test connection with a simple command
            success, output, ssh_cmd = execute_ssh_command(
                host=self.host,
                command='echo "SSH_TEST_OK"',
                username=self.username,
                port=self.port,
                key_file=self.key_file,
                timeout=self.timeout
            )
            
            if success and "SSH_TEST_OK" in output:
                self.connected = True
                log_message(f"Successfully connected to {self.host}", "INFO")
                return True
            else:
                log_message(f"SSH connection test failed: {output}", "ERROR")
                return False
                
        except Exception as e:
            log_message(f"Error connecting to remote host: {str(e)}", "ERROR")
            return False
    
    def execute_command(self, command: str, timeout: int = None) -> Tuple[bool, str, str]:
        """
        Execute a command on the remote system via SSH.
        
        Args:
            command: Shell command to execute on remote host
            timeout: Command timeout in seconds (uses instance timeout if not provided)
            
        Returns:
            Tuple of (success: bool, output: str, ssh_command: str)
        """
        if not self.connected:
            log_message("Not connected to remote host", "WARNING")
            # Try to connect automatically
            if not self.connect():
                return (False, "Cannot connect to remote host", "")
        
        if timeout is None:
            timeout = self.timeout
        
        try:
            success, output, ssh_cmd = execute_ssh_command(
                host=self.host,
                command=command,
                username=self.username,
                port=self.port,
                key_file=self.key_file,
                timeout=timeout
            )
            
            return (success, output, ssh_cmd)
                
        except Exception as e:
            log_message(f"Error executing remote command: {str(e)}", "ERROR")
            return (False, f"Error: {str(e)}", "")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Mark connection as closed."""
        self.connected = False


class RemoteFingerprinter:
    """Performs fingerprinting on remote systems."""
    
    def __init__(self, executor: RemoteExecutor):
        """
        Initialize remote fingerprinter.
        
        Args:
            executor: RemoteExecutor instance
        """
        self.executor = executor
    
    def detect_system_info(self) -> Dict:
        """
        Detect system information on remote host.
        Uses cross-platform detection methods.
        
        Returns:
            System information dictionary with evidence
        """
        log_message("Detecting remote system information...")
        
        system_info = {
            "os": "Unknown",
            "version": "Unknown",
            "kernel": "Unknown",
            "cpu": "Unknown",
            "architecture": "Unknown",
            "hostname": "Unknown",
            "evidence": {}
        }
        
        # First, detect OS type to route to appropriate commands
        success, os_output, ssh_cmd = self.executor.execute_command("uname -s")
        if success and os_output:
            os_type = os_output.strip().lower()
            system_info["evidence"]["os_type"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "uname -s",
                "raw_output": os_output
            }
            
            # Route to OS-specific detection
            if os_type == "darwin":
                self._detect_darwin_system(system_info)
            elif os_type == "linux":
                self._detect_linux_system(system_info)
            else:
                # Generic Unix detection
                self._detect_generic_unix_system(system_info)
        else:
            # Try Windows detection
            self._detect_windows_system(system_info)
        
        # Get kernel version (works on Unix-like systems)
        success, kernel, ssh_cmd = self.executor.execute_command("uname -r")
        if success and kernel:
            system_info["kernel"] = kernel
            system_info["evidence"]["kernel"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "uname -r",
                "raw_output": kernel
            }
        
        # Get architecture (cross-platform)
        success, arch, ssh_cmd = self.executor.execute_command("uname -m")
        if success and arch:
            system_info["architecture"] = arch
            system_info["evidence"]["architecture"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "uname -m",
                "raw_output": arch
            }
        
        # Get hostname
        success, hostname, ssh_cmd = self.executor.execute_command("hostname")
        if success and hostname:
            system_info["hostname"] = hostname
            system_info["evidence"]["hostname"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "hostname",
                "raw_output": hostname
            }
        
        return system_info
    
    def _detect_darwin_system(self, system_info: Dict):
        """Detect macOS-specific information."""
        system_info["os"] = "macOS"
        
        # Get macOS version
        success, version, ssh_cmd = self.executor.execute_command("sw_vers -productVersion")
        if success and version:
            system_info["version"] = version
            system_info["evidence"]["version"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "sw_vers -productVersion",
                "raw_output": version
            }
        
        # Get CPU info
        success, cpu, ssh_cmd = self.executor.execute_command("sysctl -n machdep.cpu.brand_string")
        if success and cpu:
            system_info["cpu"] = cpu
            system_info["evidence"]["cpu"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "sysctl -n machdep.cpu.brand_string",
                "raw_output": cpu
            }
    
    def _detect_linux_system(self, system_info: Dict):
        """Detect Linux-specific information."""
        system_info["os"] = "Linux"
        
        # Get distribution name
        dist_cmds = [
            ("cat /etc/os-release | grep '^NAME=' | cut -d'=' -f2 | tr -d '\"'", "os-release"),
            ("lsb_release -si 2>/dev/null", "lsb_release"),
        ]
        
        for cmd, method in dist_cmds:
            success, dist_name, ssh_cmd = self.executor.execute_command(cmd)
            if success and dist_name:
                system_info["os"] = dist_name.strip()
                system_info["evidence"]["os_name"] = {
                    "ssh_command": ssh_cmd,
                    "remote_command": cmd,
                    "raw_output": dist_name,
                    "method": method
                }
                break
        
        # Get version
        version_cmds = [
            ("cat /etc/os-release | grep '^VERSION_ID=' | cut -d'=' -f2 | tr -d '\"'", "os-release"),
            ("lsb_release -sr 2>/dev/null", "lsb_release"),
        ]
        
        for cmd, method in version_cmds:
            success, version, ssh_cmd = self.executor.execute_command(cmd)
            if success and version:
                system_info["version"] = version
                system_info["evidence"]["version"] = {
                    "ssh_command": ssh_cmd,
                    "remote_command": cmd,
                    "raw_output": version,
                    "method": method
                }
                break
        
        # Get CPU info
        cpu_cmd = "cat /proc/cpuinfo | grep 'model name' | head -n 1 | cut -d':' -f2 | xargs"
        success, cpu, ssh_cmd = self.executor.execute_command(cpu_cmd)
        if success and cpu:
            system_info["cpu"] = cpu
            system_info["evidence"]["cpu"] = {
                "ssh_command": ssh_cmd,
                "remote_command": cpu_cmd,
                "raw_output": cpu
            }
    
    def _detect_generic_unix_system(self, system_info: Dict):
        """Detect generic Unix system information."""
        system_info["os"] = "Unix"
        
        # Try uname -v for version
        success, version, ssh_cmd = self.executor.execute_command("uname -v")
        if success and version:
            system_info["version"] = version
            system_info["evidence"]["version"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "uname -v",
                "raw_output": version
            }
    
    def _detect_windows_system(self, system_info: Dict):
        """Detect Windows system information."""
        # Try systeminfo command (Windows)
        success, output, ssh_cmd = self.executor.execute_command("systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"")
        if success and output:
            lines = output.split('\n')
            for line in lines:
                if 'OS Name' in line:
                    system_info["os"] = line.split(':', 1)[1].strip()
                elif 'OS Version' in line:
                    system_info["version"] = line.split(':', 1)[1].strip()
            
            system_info["evidence"]["os_info"] = {
                "ssh_command": ssh_cmd,
                "remote_command": "systeminfo",
                "raw_output": output
            }
    
    def detect_software(self, detection_cmd: str, version_cmd: str = None) -> Tuple[bool, str, Optional[str], Dict]:
        """
        Detect software on remote host with full evidence tracking.
        
        Args:
            detection_cmd: Command to detect software
            version_cmd: Command to get version (optional)
            
        Returns:
            Tuple of (found: bool, detection_output: str, version: str or None, evidence: dict)
        """
        evidence = {}
        
        # Execute detection command
        success, output, ssh_cmd = self.executor.execute_command(detection_cmd)
        
        evidence["detection"] = {
            "ssh_command": ssh_cmd,
            "remote_command": detection_cmd,
            "raw_output": output,
            "success": success
        }
        
        if not success or not output:
            return (False, "", None, evidence)
        
        version = None
        if version_cmd:
            # Replace {app_path} if present
            if '{app_path}' in version_cmd:
                app_path = output.strip().split('\n')[0]
                version_cmd = version_cmd.replace('{app_path}', app_path)
            
            v_success, v_output, v_ssh_cmd = self.executor.execute_command(version_cmd)
            
            evidence["version"] = {
                "ssh_command": v_ssh_cmd,
                "remote_command": version_cmd,
                "raw_output": v_output,
                "success": v_success
            }
            
            if v_success and v_output:
                version = v_output.strip()
        
        return (True, output, version, evidence)


def create_remote_executor(host: str, username: str = None, key_file: str = None, 
                           port: int = 22) -> Optional[RemoteExecutor]:
    """
    Create and connect a remote executor using subprocess SSH.
    
    Args:
        host: Remote host IP or hostname
        username: SSH username (optional)
        key_file: Path to SSH private key (optional)
        port: SSH port (default: 22)
        
    Returns:
        Connected RemoteExecutor or None if connection failed
    """
    executor = RemoteExecutor(host, username, key_file, port)
    
    if executor.connect():
        return executor
    else:
        return None



#RemoteExecutor securely executes SSH commands using the system’s OpenSSH client with key/username auth, custom ports, timeouts, and full command evidence.
#RemoteFingerprinter builds on this to accurately detect remote OS, hardware, and software using OS-specific logic with audit-ready evidence