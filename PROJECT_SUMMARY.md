# PROJECT SUMMARY
# System & Software Fingerprinting Tool

## 📊 PROJECT STATUS: ACTIVE

Simplified, production-ready fingerprinting tool.

## 📦 Deliverables

### Core Implementation (Single Module)
✅ main.py                      - 150+ lines - Complete fingerprinting tool
✅ software_config.json         - Configuration for software detection
✅ README.md                    - Comprehensive documentation


## 🎯 Features Implemented

### System Detection ✅
- Operating System (Darwin/Linux/Windows)
- OS Version and Kernel
- CPU Architecture (x86_64/arm64)
- Hostname detection
- CPU count and memory (GB)
- Cross-platform support (macOS/Linux)

### Software Fingerprinting ✅
- Config-driven detection (software_config.json)
- Version extraction via `--version` flag
- Product family categorization
- Vendor identification
- Install path tracking
- Architecture inheritance
- Extensible via JSON config

### Connectivity Modes ✅
- **Local Mode**: Native Python execution (`platform`, `psutil`, `shutil`)
- **Remote Mode**: SSH via subprocess (key-based auth only)
- Automatic SSH connectivity testing
- Unified command interface

### Data Integrity ✅
- Evidence tracking for all detections
- Command logging ("command_run")
- Raw output capture ("raw_output")
- ISO 8601 timestamps
- Structured JSON output

### Output Format ✅
- Timestamped JSON files: `fingerprint_{mode}_{timestamp}.json`
- Scan metadata (type, host, user)
- System information section
- Software array with evidence
- Custom output path support

## 🧪 Current Status

**Implementation**: Simplified single-file architecture  
**Dependencies**: `psutil` only  
**Lines of Code**: ~150 (main.py)  
**Config Format**: JSON (software_config.json)  

## 📊 Capabilities

### Local Scan
- Direct system introspection
- Fast execution (<1 second)
- No external dependencies beyond psutil
- Native Python APIs

### Remote Scan
- SSH-based execution
- Automatic connectivity check
- Compatible with any SSH-accessible system
- Key-based authentication required

### Pre-configured Software (10 entries)
```
✅ Python (python3)
✅ Git (git)
✅ Docker (docker)
✅ Node.js (node)
✅ VS Code (code)
✅ Java (java)
✅ Chrome (google-chrome)
✅ Firefox (firefox)
✅ npm (npm)
✅ Kubernetes (kubectl)
```

## 🏗️ Architecture

```
┌───────────────────────────────────────────────┐
│              main.py (150 lines)              │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │   CLI (argparse)                        │ │
│  │   --mode, --host, --user, --config      │ │
│  └──────────────┬──────────────────────────┘ │
│                 │                             │
│     ┌───────────▼──────────┐                 │
│     │  Mode Selection      │                 │
│     └───┬──────────────┬───┘                 │
│         │              │                     │
│  ┌──────▼─────┐ ┌─────▼──────┐              │
│  │run_local   │ │run_remote  │              │
│  │_scan()     │ │_scan()     │              │
│  └──────┬─────┘ └─────┬──────┘              │
│         │              │                     │
│         └──────┬───────┘                     │
│                │                             │
│  ┌─────────────▼────────────────┐           │
│  │  get_system_info()           │           │
│  │  • platform / uname          │           │
│  │  • psutil (cpu, memory)      │           │
│  └──────────────────────────────┘           │
│                                              │
│  ┌─────────────────────────────┐            │
│  │  get_software_info()        │            │
│  │  • load_software_config()   │            │
│  │  • which / shutil.which()   │            │
│  │  • get_version()            │            │
│  └──────────────────────────────┘           │
│                                              │
│  ┌─────────────────────────────┐            │
│  │  run_cmd()                  │            │
│  │  • subprocess.run()         │            │
│  │  • SSH via subprocess       │            │
│  └──────────────────────────────┘           │
└───────────────┬──────────────────────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │  software_config.json     │
    │  (Input)                  │
    └───────────────────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │  fingerprint_*.json       │
    │  (Output)                 │
    └───────────────────────────┘
```



## 🚀 Usage

```bash
# Local scan (default)
python3 main.py

# Local with custom config
python3 main.py --config custom.json

# Remote scan
python3 main.py --mode remote --host 192.168.1.100 --user admin

# Custom output file
python3 main.py --output my_report.json

# View help
python3 main.py --help
```

## 📝 Configuration Example

**software_config.json:**
```json
{
  "software": [
    {
      "name": "PostgreSQL",
      "command": "psql",
      "family": "Database",
      "vendor": "PostgreSQL Global Development Group"
    }
  ]
}
```

## 🔧 Technical Details

- **Language**: Python 3.7+
- **Dependencies**: `psutil` (local system info)
- **SSH Method**: Native subprocess (no paramiko needed)
- **Detection**: Command existence via `which` / `shutil.which()`
- **Versioning**: Generic `--version` flag parsing
- **Output**: ISO 8601 timestamps, JSON format



