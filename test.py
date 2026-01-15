#!/usr/bin/env python3
"""
Quick test script to verify the fingerprinting agent is working.
"""

import sys
import os


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import utils
        import system_detector
        import software_detector
        import remote_executor
        import main
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_system_detection():
    """Test system detection."""
    print("\nTesting system detection...")
    try:
        from system_detector import detect_system_info
        info = detect_system_info()
        
        print(f"✓ OS: {info['os']}")
        print(f"✓ Version: {info['version']}")
        print(f"✓ Kernel: {info['kernel']}")
        print(f"✓ CPU: {info['cpu']}")
        print(f"✓ Architecture: {info['architecture']}")
        return True
    except Exception as e:
        print(f"✗ System detection error: {e}")
        return False


def test_software_detection():
    """Test software detection."""
    print("\nTesting software detection...")
    try:
        from software_detector import SoftwareDetector
        
        if not os.path.exists("software_config.json"):
            print("⚠ software_config.json not found, skipping software detection")
            return True
        
        detector = SoftwareDetector("software_config.json")
        software = detector.detect_all()
        
        print(f"✓ Software detection complete: {len(software)} products found")
        
        if software:
            for sw in software[:3]:  # Show first 3
                print(f"  - {sw['productName']}: {sw['versionNumber']}")
            if len(software) > 3:
                print(f"  ... and {len(software) - 3} more")
        
        return True
    except Exception as e:
        print(f"✗ Software detection error: {e}")
        return False


def test_config_file():
    """Test that config file exists and is valid."""
    print("\nTesting configuration file...")
    try:
        import json
        
        if not os.path.exists("software_config.json"):
            print("✗ software_config.json not found")
            return False
        
        with open("software_config.json", 'r') as f:
            config = json.load(f)
        
        targets = config.get('software_targets', [])
        print(f"✓ Configuration loaded: {len(targets)} software targets defined")
        
        return True
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"✗ Config test error: {e}")
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utilities...")
    try:
        from utils import execute_command, get_timestamp, get_platform_key
        
        # Test command execution
        success, output = execute_command("echo test")
        if not success or "test" not in output:
            print("✗ Command execution failed")
            return False
        
        # Test timestamp
        timestamp = get_timestamp()
        if not timestamp or 'T' not in timestamp:
            print("✗ Timestamp generation failed")
            return False
        
        # Test platform detection
        platform = get_platform_key()
        if platform not in ['darwin', 'linux', 'windows']:
            print("✗ Platform detection failed")
            return False
        
        print(f"✓ Utilities working (platform: {platform})")
        return True
    except Exception as e:
        print(f"✗ Utilities test error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("FINGERPRINTING AGENT TEST SUITE")
    print("="*60)
    
    tests = [
        test_imports,
        test_utilities,
        test_config_file,
        test_system_detection,
        test_software_detection,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✓ All tests passed! The agent is ready to use.")
        print("\nTry running:")
        print("  python main.py --mode local")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
