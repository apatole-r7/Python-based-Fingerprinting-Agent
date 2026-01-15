#!/usr/bin/env python3
"""
System & Software Fingerprinting Agent
Main entry point for the fingerprinting agent.

Supports both local and remote (SSH) fingerprinting of systems.
Exports results to JSON format with evidence tracking.
Production-ready with cross-platform support and robust error handling.
"""

import argparse
import json
import sys
import os
import time
from typing import Dict, Optional

from utils import get_timestamp, log_message, format_report, generate_agent_id
from system_detector import detect_system_info
from software_detector import SoftwareDetector
from remote_executor import RemoteExecutor, RemoteFingerprinter


class FingerprintAgent:
    """Main fingerprinting agent orchestrator."""
    
    def __init__(self, mode: str = "local", config_path: str = "software_config.json"):
        """
        Initialize the fingerprinting agent.
        
        Args:
            mode: Operation mode ('local' or 'remote')
            config_path: Path to software configuration file
        """
        self.mode = mode
        self.config_path = config_path
        self.remote_executor = None
    
    def run_local_scan(self) -> Dict:
        """
        Run fingerprinting scan on local machine.
        Tracks scan duration and generates unique agent ID.
        
        Returns:
            Complete fingerprint report
        """
        start_time = time.time()
        
        log_message("=" * 60)
        log_message("Starting LOCAL fingerprinting scan")
        log_message("=" * 60)
        
        # Collect system information
        system_info = detect_system_info()
        
        # Collect software inventory
        software_detector = SoftwareDetector(self.config_path)
        software_inventory = software_detector.detect_all()
        
        # Calculate scan duration
        scan_duration_ms = int((time.time() - start_time) * 1000)
        
        # Build agent metadata
        agent_metadata = {
            "agent_id": generate_agent_id(),
            "timestamp": get_timestamp(),
            "scan_type": "local",
            "target_host": system_info.get("hostname", "localhost"),
            "agent_version": "2.0.0",
            "scan_duration_ms": scan_duration_ms
        }
        
        # Format final report
        report = format_report(agent_metadata, system_info, software_inventory)
        
        log_message("=" * 60)
        log_message("LOCAL scan completed successfully")
        log_message(f"Duration: {scan_duration_ms}ms")
        log_message(f"Agent ID: {agent_metadata['agent_id']}")
        log_message("=" * 60)
        
        return report
    
    def run_remote_scan(self, host: str, username: str = None, key_file: str = None,
                       port: int = 22) -> Optional[Dict]:
        """
        Run fingerprinting scan on remote machine via SSH (subprocess-based).
        
        Args:
            host: Remote host IP or hostname
            username: SSH username (optional, uses current user if not provided)
            key_file: Path to SSH private key (optional)
            port: SSH port
            
        Returns:
            Complete fingerprint report or None if connection failed
        """
        start_time = time.time()
        
        log_message("=" * 60)
        log_message(f"Starting REMOTE fingerprinting scan on {host}")
        log_message("=" * 60)
        
        # Create remote executor (subprocess-based, no paramiko needed)
        self.remote_executor = RemoteExecutor(host, username, key_file, port)
        
        if not self.remote_executor.connect():
            log_message("Failed to connect to remote host", "ERROR")
            return None
        
        try:
            # Create remote fingerprinter
            fingerprinter = RemoteFingerprinter(self.remote_executor)
            
            # Detect system information
            system_info = fingerprinter.detect_system_info()
            
            # Detect software
            software_inventory = self._detect_remote_software(fingerprinter)
            
            # Calculate scan duration
            scan_duration_ms = int((time.time() - start_time) * 1000)
            
            # Build agent metadata
            agent_metadata = {
                "agent_id": generate_agent_id(),
                "timestamp": get_timestamp(),
                "scan_type": "remote",
                "target_host": host,
                "agent_version": "2.0.0",
                "scan_duration_ms": scan_duration_ms
            }
            
            # Format final report
            report = format_report(agent_metadata, system_info, software_inventory)
            
            log_message("=" * 60)
            log_message("REMOTE scan completed successfully")
            log_message(f"Duration: {scan_duration_ms}ms")
            log_message(f"Agent ID: {agent_metadata['agent_id']}")
            log_message("=" * 60)
            
            return report
            
        except Exception as e:
            log_message(f"Error during remote scan: {str(e)}", "ERROR")
            return None
    
    def _detect_remote_software(self, fingerprinter: RemoteFingerprinter) -> list:
        """
        Detect software on remote host using configuration.
        
        Args:
            fingerprinter: RemoteFingerprinter instance
            
        Returns:
            List of detected software with metadata
        """
        import json
        
        # Load software configuration
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                software_targets = config.get('software_targets', [])
        except Exception as e:
            log_message(f"Error loading software config: {e}", "WARNING")
            return []
        
        detected_software = []
        
        for target in software_targets:
            try:
                name = target.get('name', 'Unknown')
                detection_config = target.get('detection', {})
                
                # Get platform-specific configuration
                # For remote, try multiple platforms
                for platform_key in ['darwin', 'linux', 'windows']:
                    platform_config = detection_config.get(platform_key)
                    if not platform_config:
                        continue
                    
                    detection_cmd = platform_config.get('command', '')
                    version_cmd = platform_config.get('version_command', '')
                    
                    if not detection_cmd:
                        continue
                    
                    # Attempt detection
                    found, output, version, evidence = fingerprinter.detect_software(
                        detection_cmd, version_cmd if version_cmd else None
                    )
                    
                    if found:
                        # Get architecture from remote system
                        arch_success, arch_output, _ = self.remote_executor.execute_command("uname -m")
                        architecture = arch_output.strip() if arch_success else "Unknown"
                        
                        software_info = {
                            "productName": name,
                            "versionNumber": version if version else "Unknown",
                            "architecture": architecture,
                            "productFamily": target.get('family', 'Unknown'),
                            "vendor": target.get('vendor', 'Unknown'),
                            "installPath": output.strip().split('\n')[0],
                            "evidence": evidence
                        }
                        
                        detected_software.append(software_info)
                        log_message(f"Detected {name} on remote host", "INFO")
                        break  # Found on this platform, stop trying others
                        
            except Exception as e:
                log_message(f"Error detecting {target.get('name', 'Unknown')}: {str(e)}", "WARNING")
                continue
        
        return detected_software
    
    def export_report(self, report: Dict, output_file: str = None) -> str:
        """
        Export fingerprint report to JSON file.
        
        Args:
            report: Fingerprint report dictionary
            output_file: Output file path (optional, generates default if not provided)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            # Generate default filename with timestamp
            timestamp = report["agent_metadata"]["timestamp"].replace(":", "-").replace(" ", "_")
            output_file = f"fingerprint_{timestamp}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            log_message(f"Report exported to: {output_file}", "INFO")
            return output_file
            
        except Exception as e:
            log_message(f"Error exporting report: {str(e)}", "ERROR")
            return None


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="System & Software Fingerprinting Agent v2.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Local scan:
    %(prog)s --mode local --output my_scan.json
  
  Remote scan with SSH key:
    %(prog)s --mode remote --host 192.168.1.100 --username admin --key-file ~/.ssh/id_rsa
  
  Remote scan (uses current user):
    %(prog)s --mode remote --host server.example.com
        """
    )
    
    # Mode selection
    parser.add_argument(
        '--mode',
        choices=['local', 'remote'],
        default='local',
        help='Scan mode: local or remote (default: local)'
    )
    
    # Output file
    parser.add_argument(
        '--output',
        '-o',
        help='Output JSON file path (default: auto-generated)'
    )
    
    # Software configuration
    parser.add_argument(
        '--config',
        default='software_config.json',
        help='Software configuration file (default: software_config.json)'
    )
    
    # Remote scan arguments
    remote_group = parser.add_argument_group('remote scan options')
    remote_group.add_argument(
        '--host',
        help='Remote host IP or hostname (required for remote mode)'
    )
    remote_group.add_argument(
        '--username',
        '-u',
        help='SSH username (optional, uses current user if not provided)'
    )
    remote_group.add_argument(
        '--key-file',
        '-k',
        help='Path to SSH private key file (optional)'
    )
    remote_group.add_argument(
        '--port',
        '-p',
        type=int,
        default=22,
        help='SSH port (default: 22)'
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.mode == 'remote' and not args.host:
        parser.error("--host is required for remote mode")
    
    # Create agent
    agent = FingerprintAgent(mode=args.mode, config_path=args.config)
    
    # Run scan
    try:
        if args.mode == 'local':
            report = agent.run_local_scan()
        else:
            report = agent.run_remote_scan(
                host=args.host,
                username=args.username,
                key_file=args.key_file,
                port=args.port
            )
        
        if report is None:
            log_message("Scan failed", "ERROR")
            return 1
        
        # Export report
        output_file = agent.export_report(report, args.output)
        
        if output_file:
            # Also print to stdout
            print(json.dumps(report, indent=2))
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        log_message("\nScan interrupted by user", "WARNING")
        return 130
    except Exception as e:
        log_message(f"Fatal error: {str(e)}", "ERROR")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
