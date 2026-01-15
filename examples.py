#!/usr/bin/env python3
"""
Example usage of the Fingerprinting Agent
Demonstrates both local and remote scanning capabilities.
"""

import json
from main import FingerprintAgent
from utils import log_message


def example_local_scan():
    """Example: Run a local fingerprinting scan."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Local Scan")
    print("="*60 + "\n")
    
    # Create agent in local mode
    agent = FingerprintAgent(mode="local", config_path="software_config.json")
    
    # Run local scan
    report = agent.run_local_scan()
    
    # Export to JSON
    agent.export_report(report, "example_local_report.json")
    
    # Display results
    print("\nScan Results:")
    print(f"  OS: {report['system_info']['os']} {report['system_info']['version']}")
    print(f"  Architecture: {report['system_info']['architecture']}")
    print(f"  CPU: {report['system_info']['cpu']}")
    print(f"  Software found: {len(report['software_inventory'])}")
    
    if report['software_inventory']:
        print("\n  Detected Software:")
        for sw in report['software_inventory']:
            print(f"    - {sw['productName']} v{sw['versionNumber']}")
    
    return report


def example_custom_software_detection():
    """Example: Detect custom software not in config."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Software Detection")
    print("="*60 + "\n")
    
    from software_detector import SoftwareDetector
    
    detector = SoftwareDetector("software_config.json")
    
    # Detect a custom software (example: node.js)
    custom_software = detector.detect_custom_software(
        name="Node.js",
        detection_cmd="which node 2>/dev/null",
        version_cmd="node --version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+'",
        family="Runtime",
        vendor="OpenJS Foundation"
    )
    
    if custom_software:
        print("Custom software detected:")
        print(json.dumps(custom_software, indent=2))
    else:
        print("Custom software not found")
    
    return custom_software


def example_remote_scan():
    """
    Example: Run a remote fingerprinting scan.
    
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Remote Scan (Template)")
    print("="*60 + "\n")
    
    print("To run a remote scan, update the following parameters:")
    print("""
    agent = FingerprintAgent(mode="remote", config_path="software_config.json")
    
    report = agent.run_remote_scan(
        host="192.168.1.100",           # Remote host IP
        username="your_username",        # SSH username
        password="your_password",        # OR use key_file instead
        # key_file="/path/to/private/key",
        port=22
    )
    
    if report:
        agent.export_report(report, "example_remote_report.json")
    """)


def example_programmatic_usage():
    """Example: Programmatic usage without CLI."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Programmatic Usage")
    print("="*60 + "\n")
    
    # Direct module usage
    from system_detector import SystemDetector
    from software_detector import SoftwareDetector
    
    # Get system info
    sys_detector = SystemDetector()
    system_info = sys_detector.detect_all()
    
    print("System Information:")
    print(f"  OS: {system_info['os']}")
    print(f"  Version: {system_info['version']}")
    print(f"  Kernel: {system_info['kernel']}")
    print(f"  CPU: {system_info['cpu']}")
    print(f"  Architecture: {system_info['architecture']}")
    
    # Get software inventory
    sw_detector = SoftwareDetector("software_config.json")
    software = sw_detector.detect_all()
    
    print(f"\nSoftware Inventory ({len(software)} items):")
    for sw in software:
        print(f"  - {sw['productName']}: {sw['versionNumber']}")
    
    # Access evidence for audit
    print("\nEvidence Examples:")
    if system_info.get('evidence'):
        for key, evidence in list(system_info['evidence'].items())[:2]:
            print(f"\n  {key}:")
            print(f"    Command: {evidence['command_run']}")
            print(f"    Output: {evidence['raw_output'][:60]}...")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" "*15 + "FINGERPRINTING AGENT EXAMPLES")
    print("="*70)
    
    try:
        # Example 1: Local scan
        example_local_scan()
        
        # Example 2: Custom software detection
        example_custom_software_detection()
        
        # Example 3: Remote scan template
        example_remote_scan()
        
        # Example 4: Programmatic usage
        example_programmatic_usage()
        
        print("\n" + "="*70)
        print("Examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        log_message(f"Error in examples: {e}", "ERROR")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


#Local scan is a high-level, one-command execution, while programmatic usage
# gives developers fine-grained control by calling detection components directly.