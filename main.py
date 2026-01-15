import platform
import psutil
import shutil
import json
import subprocess
from datetime import datetime, timezone

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def get_version(app_name, path):
    version_cmds = {
        "Python": "python3 --version 2>&1 | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+'",
        "Git": "git --version | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+'",
        "Docker": "docker --version | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+'",
        "Node.js": "node --version | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+'",
        "VS Code": "code --version 2>/dev/null | head -n 1",
        "Java": "java -version 2>&1 | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+' | head -n 1",
        "Chrome": "google-chrome --version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+'",
        "Firefox": "firefox --version 2>/dev/null | grep -oE '[0-9]+\\.[0-9]+\\.[0-9]+'"
    }
    return run_cmd(version_cmds.get(app_name, "echo Unknown")) or "Unknown"

def get_system_info():
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

def get_software_info():
    software = []
    apps = {
        "Python": ("python3", "Programming Language", "Python Software Foundation"),
        "Git": ("git", "Version Control", "Git SCM"),
        "Docker": ("docker", "Virtualization", "Docker Inc."),
        "Node.js": ("node", "Runtime", "OpenJS Foundation"),
        "VS Code": ("code", "IDE", "Microsoft"),
        "Java": ("java", "Runtime", "Oracle"),
        "Chrome": ("google-chrome", "Browser", "Google"),
        "Firefox": ("firefox", "Browser", "Mozilla")
    }
    
    arch = platform.machine()
    
    for name, (cmd, family, vendor) in apps.items():
        path = shutil.which(cmd)
        if path:
            version = get_version(name, path)
            software.append({
                "productName": name,
                "versionNumber": version,
                "architecture": arch,
                "productFamily": family,
                "vendor": vendor,
                "installPath": path,
                "evidence": {
                    "command_run": f"which {cmd}",
                    "raw_output": path
                }
            })
    
    return software

def main():
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": get_system_info(),
        "software": get_software_info()
    }
    
    filename = f"fingerprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    print(f"\nSaved to: {filename}")

if __name__ == "__main__":
    main()
