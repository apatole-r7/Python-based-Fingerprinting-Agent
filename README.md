# System & Software Fingerprinting Agent

A Python-based agent for identifying system specifications and installed software details. Supports both local and remote (SSH) execution.

## Features

- **System Information Detection**: OS, version, kernel, CPU architecture
- **Software Fingerprinting**: Detects installed applications (PyCharm, VS Code, Docker, Slack, Chrome, etc.)
- **Dual Mode Operation**:
  - **Local Mode**: Run directly on the host machine
  - **Remote Mode**: Connect via SSH to fingerprint remote systems
- **Evidence Tracking**: Records commands and raw output for audit purposes
- **JSON Export**: Structured output in `fingerprint_report.json`

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Local Mode
```bash
python main.py --mode local
```

### Remote Mode
```bash
python main.py --mode remote --host 192.168.1.100 --user admin --password yourpass
```

Or with SSH key:
```bash
python main.py --mode remote --host 192.168.1.100 --user admin --key-file ~/.ssh/id_rsa
```

### Command Line Options
```
--mode          : Operation mode (local/remote) [default: local]
--host          : Remote host IP/hostname (required for remote mode)
--user          : SSH username (required for remote mode)
--password      : SSH password (optional)
--key-file      : Path to SSH private key (optional)
--port          : SSH port [default: 22]
--output        : Output JSON file path [default: fingerprint_report.json]
--config        : Custom config file [default: config.json]
```

## Output Format

The agent generates a JSON file with the following structure:

```json
{
  "agent_metadata": {
    "timestamp": "2026-01-15T10:00:00Z",
    "scan_type": "local",
    "target_host": "localhost"
  },
  "system_info": {
    "os": "macOS",
    "version": "14.2.1",
    "kernel": "23.2.0",
    "cpu": "Apple M2",
    "architecture": "arm64"
  },
  "software_inventory": [
    {
      "productName": "PyCharm Professional",
      "versionNumber": "2023.3.2",
      "architecture": "arm64",
      "productFamily": "IDE",
      "vendor": "JetBrains",
      "evidence": {
        "command_run": "mdfind \"kMDItemCFBundleIdentifier == 'com.jetbrains.pycharm'\"",
        "raw_output": "/Applications/PyCharm.app"
      }
    }
  ]
}
```

## Configuration

Software targets are defined in `config.json`. You can add custom software by following the pattern:

```json
{
  "name": "Software Name",
  "family": "Category",
  "vendor": "Vendor Name",
  "detection": {
    "darwin": {
      "command": "detection command",
      "version_command": "version extraction command"
    },
    "linux": {...},
    "windows": {...}
  }
}
```

## Project Structure

```
fingerprinting/
├── main.py                 # Main agent script
├── system_detector.py      # System information detection
├── software_detector.py    # Software fingerprinting
├── remote_executor.py      # SSH remote execution
├── utils.py               # Helper functions
├── config.json            # Software detection configurations
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Requirements

- Python 3.7+
- paramiko (for SSH connectivity)

## Security Notes

- Use SSH keys instead of passwords when possible
- Ensure proper permissions on SSH key files (chmod 600)
- Be cautious when running on production systems
- Review commands in config.json before execution

## License

MIT License
