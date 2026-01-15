"""
Software Detector Module
Detects installed software and extracts metadata.
Uses official version sources and standardized product families.
"""

import json
import os
import re
from typing import Dict, List, Optional
from utils import execute_command, Evidence, get_platform_key, log_message, ProductFamily


class SoftwareDetector:
    """Detects installed software products."""
    
    def __init__(self, config_path: str = "software_config.json"):
        """
        Initialize the software detector.
        
        Args:
            config_path: Path to the software configuration JSON file
        """
        self.config_path = config_path
        self.software_targets = []
        self.platform_key = get_platform_key()
        self._load_config()
    
    def _load_config(self):
        """Load software detection configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.software_targets = config.get('software_targets', [])
            log_message(f"Loaded {len(self.software_targets)} software targets from config")
        except FileNotFoundError:
            log_message(f"Config file not found: {self.config_path}", "WARNING")
            self.software_targets = []
        except json.JSONDecodeError as e:
            log_message(f"Error parsing config file: {e}", "ERROR")
            self.software_targets = []
    
    def detect_all(self) -> List[Dict]:
        """
        Detect all configured software products.
        Returns partial results even if some detections fail.
        
        Returns:
            List of detected software with metadata
        """
        log_message("Starting software detection...")
        detected_software = []
        failed_count = 0
        
        for target in self.software_targets:
            try:
                software_info = self.detect_software(target)
                if software_info:
                    detected_software.append(software_info)
            except Exception as e:
                failed_count += 1
                name = target.get('name', 'Unknown')
                log_message(f"Error detecting {name}: {str(e)}", "ERROR")
                # Continue with other software instead of crashing
                continue
        
        if failed_count > 0:
            log_message(f"Software detection complete: {len(detected_software)} found, {failed_count} failed", "WARNING")
        else:
            log_message(f"Software detection complete: {len(detected_software)} products found")
        
        return detected_software
    
    def detect_software(self, target: Dict) -> Optional[Dict]:
        """
        Detect a specific software product with robust error handling.
        
        Args:
            target: Software target configuration
            
        Returns:
            Software metadata dictionary or None if not found
        """
        name = target.get('name', 'Unknown')
        
        try:
            detection_config = target.get('detection', {})
            platform_config = detection_config.get(self.platform_key)
            
            if not platform_config:
                log_message(f"No detection config for {name} on {self.platform_key}", "INFO")
                return None
            
            # Execute detection command
            detection_cmd = platform_config.get('command', '')
            if not detection_cmd:
                log_message(f"No detection command for {name}", "WARNING")
                return None
            
            success, output = execute_command(detection_cmd)
            
            if not success or not output:
                log_message(f"{name} not detected", "INFO")
                return None
            
            log_message(f"Detected {name}", "INFO")
            
            # Extract version with improved method
            version = self._extract_version(target, platform_config, output)
            
            # Get architecture
            architecture = self._get_architecture()
            
            # Normalize product family
            family = self._normalize_product_family(target.get('family', 'Unknown'))
            
            # Build software info with all required fields
            software_info = {
                "productName": name,
                "versionNumber": version if version else "Unknown",
                "architecture": architecture,
                "productFamily": family,
                "vendor": target.get('vendor', 'Unknown'),
                "installPath": output.strip().split('\n')[0],  # First line usually contains path
                "evidence": {
                    "detection": Evidence(detection_cmd, output).to_dict()
                }
            }
            
            return software_info
            
        except Exception as e:
            log_message(f"Error detecting {name}: {str(e)}", "ERROR")
            return None
    
    def _extract_version(self, target: Dict, platform_config: Dict, detection_output: str) -> Optional[str]:
        """
        Extract version information using official sources.
        Prefers Info.plist on macOS, --version for CLI tools.
        
        Args:
            target: Software target configuration
            platform_config: Platform-specific configuration
            detection_output: Output from detection command
            
        Returns:
            Version string or None
        """
        version_cmd = platform_config.get('version_command', '')
        
        if not version_cmd:
            # Try to extract from detection output if it looks like a version
            version_pattern = r'\b(\d+\.\d+\.\d+(?:\.\d+)?)\b'
            match = re.search(version_pattern, detection_output)
            if match:
                return match.group(1)
            return None
        
        try:
            # Replace {app_path} placeholder with actual path
            if '{app_path}' in version_cmd:
                app_path = detection_output.strip().split('\n')[0]
                version_cmd = version_cmd.replace('{app_path}', app_path)
            
            success, output = execute_command(version_cmd)
            
            if success and output:
                # Clean and extract version
                version = output.strip().split('\n')[0]  # First line
                return version
            
        except Exception as e:
            log_message(f"Error extracting version for {target.get('name', 'Unknown')}: {str(e)}", "WARNING")
        
        return None
    
    def _normalize_product_family(self, family: str) -> str:
        """
        Normalize product family using ProductFamily enum.
        
        Args:
            family: Raw family string from config
            
        Returns:
            Normalized family string from enum
        """
        # Map common variations to standard enum values
        family_mapping = {
            'IDE': ProductFamily.IDE,
            'Browser': ProductFamily.BROWSER,
            'Virtualization': ProductFamily.VIRTUALIZATION,
            'Communication': ProductFamily.COMMUNICATION,
            'Programming Language': ProductFamily.PROGRAMMING_LANGUAGE,
            'Version Control': ProductFamily.VERSION_CONTROL,
            'Database': ProductFamily.DATABASE,
            'Runtime': ProductFamily.RUNTIME,
            'Container': ProductFamily.CONTAINER,
            'Cloud Tools': ProductFamily.CLOUD_TOOLS,
            'Security': ProductFamily.SECURITY,
            'Monitoring': ProductFamily.MONITORING,
        }
        
        # Try to match against enum
        if family in family_mapping:
            return family_mapping[family].value
        
        # Check if it's already an enum value
        try:
            ProductFamily(family)
            return family
        except ValueError:
            log_message(f"Unknown product family: {family}, using 'Other'", "WARNING")
            return ProductFamily.OTHER.value
    
    def _get_architecture(self) -> str:
        """
        Get system architecture.
        
        Returns:
            Architecture string (e.g., arm64, x86_64)
        """
        import platform
        return platform.machine()
    
    def detect_custom_software(self, name: str, detection_cmd: str, version_cmd: str = None,
                               family: str = "Custom", vendor: str = "Unknown") -> Optional[Dict]:
        """
        Detect custom software not in the configuration.
        
        Args:
            name: Software name
            detection_cmd: Command to detect software
            version_cmd: Command to get version (optional)
            family: Product family
            vendor: Vendor name
            
        Returns:
            Software metadata dictionary or None if not found
        """
        success, output = execute_command(detection_cmd)
        
        if not success or not output:
            return None
        
        version = "Unknown"
        version_evidence = None
        
        if version_cmd:
            v_success, v_output = execute_command(version_cmd)
            if v_success and v_output:
                version = v_output.strip()
                version_evidence = Evidence(version_cmd, v_output).to_dict()
        
        # Normalize family
        normalized_family = self._normalize_product_family(family)
        
        software_info = {
            "productName": name,
            "versionNumber": version,
            "architecture": self._get_architecture(),
            "productFamily": normalized_family,
            "vendor": vendor,
            "installPath": output.strip().split('\n')[0],
            "evidence": {
                "detection": Evidence(detection_cmd, output).to_dict()
            }
        }
        
        if version_evidence:
            software_info["evidence"]["version"] = version_evidence
        
        return software_info


def detect_software_inventory(config_path: str = "software_config.json") -> List[Dict]:
    """
    Convenience function to detect software inventory.
    
    Args:
        config_path: Path to software configuration file
        
    Returns:
        List of detected software
    """
    detector = SoftwareDetector(config_path)
    return detector.detect_all()
