"""
System Detector Module
Detects operating system, version, kernel, and CPU architecture.
Cross-platform support for macOS, Linux, and Windows.
"""

import platform
import subprocess
from typing import Dict, Optional
from utils import execute_command, Evidence, log_message


class SystemDetector:
    """Detects system-level information with cross-platform support."""
    
    def __init__(self):
        self.platform_system = platform.system()
        self.evidences = {}
        
        # Determine platform early for routing
        self.is_darwin = self.platform_system == 'Darwin'
        self.is_linux = self.platform_system == 'Linux'
        self.is_windows = self.platform_system == 'Windows'
    
    def detect_all(self) -> Dict:
        """
        Detect all system information.
        
        Returns:
            Dictionary containing OS, version, kernel, CPU, and architecture info
        """
        log_message("Starting system detection...")
        
        system_info = {
            "os": self.detect_os(),
            "version": self.detect_os_version(),
            "kernel": self.detect_kernel_version(),
            "cpu": self.detect_cpu(),
            "architecture": self.detect_architecture(),
            "hostname": self.detect_hostname(),
            "evidence": {}
        }
        
        # Add all collected evidences
        for key, evidence in self.evidences.items():
            system_info["evidence"][key] = evidence.to_dict()
        
        log_message(f"System detection complete: {system_info['os']} {system_info['version']}")
        return system_info
    
    def detect_os(self) -> str:
        """Detect operating system name with platform-specific methods."""
        if self.is_darwin:
            return 'macOS'
        elif self.is_linux:
            return self._detect_linux_distro()
        elif self.is_windows:
            return 'Windows'
        else:
            return self.platform_system
    
    def _detect_linux_distro(self) -> str:
        """
        Detect specific Linux distribution using multiple methods.
        Prioritizes /etc/os-release (standard), then lsb_release, then /etc/issue.
        """
        # Method 1: /etc/os-release (most reliable, FreeDesktop standard)
        cmd = "cat /etc/os-release 2>/dev/null | grep '^NAME=' | cut -d'=' -f2 | tr -d '\"'"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['linux_distro'] = Evidence(cmd, output)
            return output.split()[0]  # Get first word (e.g., "Ubuntu" from "Ubuntu 20.04")
        
        # Method 2: lsb_release (LSB standard)
        cmd = "lsb_release -si 2>/dev/null"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['linux_distro'] = Evidence(cmd, output)
            return output.strip()
        
        # Method 3: /etc/issue (fallback)
        cmd = "cat /etc/issue 2>/dev/null | head -n 1"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['linux_distro'] = Evidence(cmd, output)
            return output.split()[0]
        
        return 'Linux'
    
    def detect_os_version(self) -> str:
        """
        Detect OS version using platform-appropriate commands.
        Routes to specific detection methods based on OS.
        """
        if self.is_darwin:
            return self._detect_darwin_version()
        elif self.is_linux:
            return self._detect_linux_version()
        elif self.is_windows:
            return self._detect_windows_version()
        else:
            # Fallback to platform module
            version = platform.version()
            self.evidences['os_version'] = Evidence("platform.version()", version)
            return version
    
    def _detect_darwin_version(self) -> str:
        """Detect macOS version."""
        cmd = "sw_vers -productVersion"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['os_version'] = Evidence(cmd, output)
            return output
        
        # Fallback
        version = platform.mac_ver()[0]
        self.evidences['os_version'] = Evidence("platform.mac_ver()", version)
        return version
    
    def _detect_linux_version(self) -> str:
        """Detect Linux distribution version."""
        # Method 1: /etc/os-release
        cmd = "cat /etc/os-release 2>/dev/null | grep '^VERSION_ID=' | cut -d'=' -f2 | tr -d '\"'"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['os_version'] = Evidence(cmd, output)
            return output
        
        # Method 2: lsb_release
        cmd = "lsb_release -sr 2>/dev/null"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['os_version'] = Evidence(cmd, output)
            return output
        
        # Method 3: uname
        cmd = "uname -r"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['os_version'] = Evidence(cmd, output)
            return output
        
        # Fallback
        version = platform.version()
        self.evidences['os_version'] = Evidence("platform.version()", version)
        return version
    
    def _detect_windows_version(self) -> str:
        """Detect Windows version."""
        # Try ver command
        cmd = "ver"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['os_version'] = Evidence(cmd, output)
            return output
        
        # Fallback to platform module
        version = platform.version()
        self.evidences['os_version'] = Evidence("platform.version()", version)
        return version
    
    def detect_kernel_version(self) -> str:
        """
        Detect kernel version with cross-platform support.
        Uses uname on Unix-like systems, ver on Windows.
        """
        if self.is_darwin or self.is_linux:
            cmd = "uname -r"
            success, output = execute_command(cmd)
            if success and output:
                self.evidences['kernel'] = Evidence(cmd, output)
                return output
        
        elif self.is_windows:
            cmd = "ver"
            success, output = execute_command(cmd)
            if success and output:
                self.evidences['kernel'] = Evidence(cmd, output)
                return output
        
        # Fallback
        release = platform.release()
        self.evidences['kernel'] = Evidence("platform.release()", release)
        return release
    
    def detect_cpu(self) -> str:
        """
        Detect CPU model/name using platform-specific commands.
        Routes to appropriate method based on OS.
        """
        if self.is_darwin:
            return self._detect_darwin_cpu()
        elif self.is_linux:
            return self._detect_linux_cpu()
        elif self.is_windows:
            return self._detect_windows_cpu()
        else:
            # Fallback to processor
            processor = platform.processor()
            self.evidences['cpu'] = Evidence("platform.processor()", processor)
            return processor if processor else "Unknown"
    
    def _detect_darwin_cpu(self) -> str:
        """Detect macOS CPU information."""
        cmd = "sysctl -n machdep.cpu.brand_string"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['cpu'] = Evidence(cmd, output)
            return output
        
        # Fallback
        processor = platform.processor()
        self.evidences['cpu'] = Evidence("platform.processor()", processor)
        return processor if processor else "Unknown"
    
    def _detect_linux_cpu(self) -> str:
        """Detect Linux CPU information."""
        cmd = "cat /proc/cpuinfo | grep 'model name' | head -n 1 | cut -d':' -f2"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['cpu'] = Evidence(cmd, output)
            return output.strip()
        
        # Try lscpu as fallback
        cmd = "lscpu | grep 'Model name' | cut -d':' -f2"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['cpu'] = Evidence(cmd, output)
            return output.strip()
        
        # Fallback
        processor = platform.processor()
        self.evidences['cpu'] = Evidence("platform.processor()", processor)
        return processor if processor else "Unknown"
    
    def _detect_windows_cpu(self) -> str:
        """Detect Windows CPU information."""
        cmd = "wmic cpu get name"
        success, output = execute_command(cmd)
        if success and output:
            self.evidences['cpu'] = Evidence(cmd, output)
            lines = output.split('\n')
            if len(lines) > 1:
                return lines[1].strip()
        
        # Fallback
        processor = platform.processor()
        self.evidences['cpu'] = Evidence("platform.processor()", processor)
        return processor if processor else "Unknown"
    
    def detect_architecture(self) -> str:
        """
        Detect CPU architecture with cross-platform support.
        Uses uname -m on Unix-like, environment variable on Windows.
        """
        if self.is_darwin or self.is_linux:
            cmd = "uname -m"
        elif self.is_windows:
            cmd = "echo %PROCESSOR_ARCHITECTURE%"
        else:
            cmd = "uname -m"
        
        success, output = execute_command(cmd)
        
        if success and output:
            self.evidences['architecture'] = Evidence(cmd, output)
            return output
        
        # Fallback
        arch = platform.machine()
        self.evidences['architecture'] = Evidence("platform.machine()", arch)
        return arch
    
    def detect_hostname(self) -> str:
        """Detect system hostname."""
        cmd = "hostname"
        success, output = execute_command(cmd)
        
        if success and output:
            self.evidences['hostname'] = Evidence(cmd, output)
            return output
        
        # Fallback
        hostname = platform.node()
        self.evidences['hostname'] = Evidence("platform.node()", hostname)
        return hostname


def detect_system_info() -> Dict:
    """
    Convenience function to detect system information.
    
    Returns:
        System information dictionary
    """
    detector = SystemDetector()
    return detector.detect_all()
