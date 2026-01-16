# System & Software Fingerprinting Tool

A lightweight Python tool for identifying system specifications and installed software. Supports both local and remote (SSH) scanning.

## Features

- **System Information Detection**: OS, version, kernel, CPU, architecture, memory
- **Software Fingerprinting**: Detects installed applications via configuration file
- **Dual Mode Operation**:
  - **Local Mode**: Scan the current system
  - **Remote Mode**: Connect via SSH to scan remote systems
- **Evidence Tracking**: Records detection commands and raw output
- **JSON Export**: Timestamped structured output files
- **Configurable**: External JSON config for software definitions

## Installation

```bash
# Install dependencies
pip install psutil
```

## Usage

### Local Mode
```bash
python3 main.py
# or explicitly
python3 main.py --mode local
```

### Remote Mode
```bash
python3 main.py --mode remote --host 192.168.1.100 --user admin
```

**Note**: Remote mode requires SSH key-based authentication to be configured.

### Command Line Options
```
--mode          : Operation mode (local/remote) [default: local]
--host          : Remote host IP/hostname (required for remote mode)
--user          : SSH username (required for remote mode)
--output        : Output JSON file path (optional, auto-generated if not specified)
--config        : Custom config file [default: software_config.json]
```

## Output Format

The tool generates a JSON file with the following structure:

```json
{
  "scan_type": "local",
  "timestamp": "2026-01-16T10:30:00.123456+00:00",
  "system": {
    "os": "Darwin",
    "version": "Darwin Kernel Version 24.6.0",
    "kernel": "24.6.0",
    "cpu": "arm",
    "architecture": "arm64",
    "hostname": "MacBook-Pro.local",
    "cpu_count": 12,
    "memory_gb": 32.0
  },
  "software": [
    {
      "productName": "Python",
      "versionNumber": "Python 3.9.6",
      "architecture": "arm64",
      "productFamily": "Programming Language",
      "vendor": "Python Software Foundation",
      "installPath": "/usr/bin/python3",
      "evidence": {
        "command_run": "which python3",
        "raw_output": "/usr/bin/python3"
      }
    }
  ]
}
```

## Configuration

Software targets are defined in `software_config.json`. Add or modify software entries:

```json
{
  "software": [
    {
      "name": "PostgreSQL",
      "command": "psql",
      "family": "Database",
      "vendor": "PostgreSQL Global Development Group"
    },
    {
      "name": "Kubernetes",
      "command": "kubectl",
      "family": "Container Orchestration",
      "vendor": "CNCF"
    }
  ]
}
```

**Fields:**
- `name`: Display name of the software
- `command`: Shell command to detect (e.g., `python3`, `docker`, `git`)
- `family`: Category (e.g., "Programming Language", "IDE", "Database")
- `vendor`: Software vendor or organization

## Project Structure

```
fingerprinting/
├── main.py                     # Main application (all-in-one)
├── software_config.json        # Software detection configurations
├── README.md                   # This file
└── fingerprint_*.json          # Output files (generated)
```

## How It Works

1. **Local Scan**: Uses Python's `platform`, `psutil`, and `shutil` modules to detect system info and software
2. **Remote Scan**: Executes commands via SSH using `subprocess` (requires SSH key authentication)
3. **Version Detection**: Runs `<command> --version` for each detected software
4. **Evidence Collection**: Stores the exact commands and outputs for audit trails

## Requirements

- Python 3.7+
- `psutil` library
- SSH access (for remote mode)

## Security Notes

- Remote mode requires SSH key-based authentication
- Ensure proper SSH key permissions (`chmod 600 ~/.ssh/id_rsa`)
- Review software_config.json before scanning
- Be cautious when running on production systems

## Examples

```bash
# Scan localhost with default config
python3 main.py

# Scan localhost with custom config
python3 main.py --config custom_software.json --output my_scan.json

# Scan remote server
python3 main.py --mode remote --host prod-server-01 --user sysadmin

# Scan remote with custom output
python3 main.py --mode remote --host 10.0.1.50 --user admin --output server_scan.json
```
