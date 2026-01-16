import platform # for system info
import psutil # for system and hardware info
import shutil # for finding executable paths
import json
import subprocess # for running shell commands
import argparse
import os # for file operations
from datetime import datetime, timezone

def run_cmd(cmd, remote_host=None, ssh_user=None):
    """Run command locally or remotely via SSH"""
    try:
        if remote_host:
            ssh_cmd = f"ssh {ssh_user}@{remote_host} '{cmd}'"
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def get_version(cmd, remote_host=None, ssh_user=None):
    """Get version of a command by running it with --version flag"""
    version_cmd = f"{cmd} --version 2>&1 | head -n 1"
    return run_cmd(version_cmd, remote_host, ssh_user) or "Unknown"

def get_system_info(remote_host=None, ssh_user=None):
    """Get system information locally or remotely"""
    if remote_host:
        return {
            "os": run_cmd("uname -s", remote_host, ssh_user) or "Unknown",
            "version": run_cmd("uname -v", remote_host, ssh_user) or "Unknown",
            "kernel": run_cmd("uname -r", remote_host, ssh_user) or "Unknown",
            "cpu": run_cmd("uname -p", remote_host, ssh_user) or "Unknown",
            "architecture": run_cmd("uname -m", remote_host, ssh_user) or "Unknown",
            "hostname": run_cmd("hostname", remote_host, ssh_user) or "Unknown",
            "cpu_count": run_cmd("nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo Unknown", remote_host, ssh_user) or "Unknown",
            "memory_gb": run_cmd("free -g 2>/dev/null | awk '/^Mem:/{print $2}' || sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024/1024}' || echo Unknown", remote_host, ssh_user) or "Unknown"
        }
    return {
        "os": platform.system(),
        "version": platform.version(),
        "kernel": platform.release(),
        "cpu": platform.processor(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "cpu_count": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2)
    }

def load_software_config(config_file="software_config.json"):
    
    if not os.path.exists(config_file):
        print(f"Warning: Config file '{config_file}' not found. No software will be scanned.")
        return []
    
    with open(config_file, 'r') as f:
        return json.load(f).get("software", [])

def get_software_info(remote_host=None, ssh_user=None, config_file="software_config.json"):
    
    software = []
    apps = load_software_config(config_file)
    arch = run_cmd("uname -m", remote_host, ssh_user) if remote_host else platform.machine()
    
    for app in apps:
        cmd = app["command"]
        path = run_cmd(f"which {cmd}", remote_host, ssh_user) if remote_host else shutil.which(cmd)
        
        if path:
            software.append({
                "productName": app["name"],
                "versionNumber": get_version(cmd, remote_host, ssh_user),
                "architecture": arch,
                "productFamily": app["family"],
                "vendor": app["vendor"],
                "installPath": path,
                "evidence": {"command_run": f"which {cmd}", "raw_output": path}
            })
    
    return software

def run_local_scan(config_file="software_config.json"):
    print("Running LOCAL scan...")
    report = {
        "scan_type": "local",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": get_system_info(),
        "software": get_software_info(config_file=config_file)
    }
    return report

def run_remote_scan(remote_host, ssh_user, config_file="software_config.json"):
    print(f"Running REMOTE scan on {ssh_user}@{remote_host}...")
    
    if run_cmd("echo 'connection_test'", remote_host, ssh_user) != "connection_test":
        print(f"ERROR: Cannot connect to {remote_host}. Check SSH configuration.")
        return None
    
    return {
        "scan_type": "remote",
        "remote_host": remote_host,
        "ssh_user": ssh_user,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": get_system_info(remote_host, ssh_user),
        "software": get_software_info(remote_host, ssh_user, config_file)
    }

def main():
    parser = argparse.ArgumentParser(description="System Fingerprinting Tool - Local and Remote Scanning")
    parser.add_argument("--mode", choices=["local", "remote"], default="local",
                        help="Scan mode: local or remote (default: local)")
    parser.add_argument("--host", type=str, help="Remote host IP or hostname (required for remote mode)")
    parser.add_argument("--user", type=str, help="SSH username (required for remote mode)")
    parser.add_argument("--output", type=str, help="Output filename (optional)")
    parser.add_argument("--config", type=str, default="software_config.json",
                        help="Path to software configuration file (default: software_config.json)")
    
    args = parser.parse_args()
    
    # Validate remote mode arguments
    if args.mode == "remote":
        if not args.host or not args.user:
            print("ERROR: Remote mode requires --host and --user arguments")
            parser.print_help()
            return
        report = run_remote_scan(args.host, args.user, args.config)
    else:
        report = run_local_scan(args.config)
    
    if not report:
        print("Scan failed!")
        return
    
    # Generate filename
    if args.output:
        filename = args.output
    else:
        scan_type = args.mode
        filename = f"fingerprint_{scan_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    print(f"\nSaved to: {filename}")

if __name__ == "__main__":
    main()
