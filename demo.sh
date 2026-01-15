#!/bin/bash

# ============================================================
# Fingerprinting Agent - Demo Script
# Demonstrates the key features of the agent
# ============================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   System & Software Fingerprinting Agent - DEMO           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================
# DEMO 1: Run Test Suite
# ============================================================
echo -e "${BLUE}[DEMO 1] Running Test Suite${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 test.py
echo ""
echo -e "${GREEN}✓ Tests completed${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# ============================================================
# DEMO 2: Local Fingerprinting Scan
# ============================================================
echo -e "${BLUE}[DEMO 2] Running Local Fingerprinting Scan${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 main.py --mode local --output demo_report.json
echo ""
echo -e "${GREEN}✓ Local scan completed${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# ============================================================
# DEMO 3: View Generated Report
# ============================================================
echo -e "${BLUE}[DEMO 3] Viewing Generated Report (First 30 lines)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
head -n 30 demo_report.json
echo ""
echo "..."
echo ""
echo -e "${YELLOW}Full report available in: demo_report.json${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# ============================================================
# DEMO 4: Show Evidence Tracking
# ============================================================
echo -e "${BLUE}[DEMO 4] Evidence Tracking Example${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Every data point includes the command and raw output:"
echo ""
python3 -c "
import json
with open('demo_report.json', 'r') as f:
    data = json.load(f)
    
print('System Info Evidence:')
for key, evidence in list(data['system_info']['evidence'].items())[:2]:
    print(f'  {key}:')
    print(f'    Command: {evidence[\"command_run\"]}')
    print(f'    Output: {evidence[\"raw_output\"]}')
    print()

if data['software_inventory']:
    sw = data['software_inventory'][0]
    print('Software Detection Evidence:')
    print(f'  Product: {sw[\"productName\"]}')
    if 'detection' in sw['evidence']:
        print(f'    Command: {sw[\"evidence\"][\"detection\"][\"command_run\"]}')
        print(f'    Output: {sw[\"evidence\"][\"detection\"][\"raw_output\"]}')
"
echo ""
echo -e "${GREEN}✓ Evidence tracking ensures full auditability${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# ============================================================
# DEMO 5: Show Programmatic Usage
# ============================================================
echo -e "${BLUE}[DEMO 5] Programmatic Usage Examples${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 examples.py
echo ""
echo -e "${GREEN}✓ Examples completed${NC}"
echo ""
read -p "Press Enter to continue..."
echo ""

# ============================================================
# Summary
# ============================================================
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETED                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Key Features Demonstrated:"
echo "  ✓ Automated testing"
echo "  ✓ Local system fingerprinting"
echo "  ✓ JSON report generation"
echo "  ✓ Evidence tracking for audit"
echo "  ✓ Programmatic API usage"
echo ""
echo "Next Steps:"
echo "  1. Review the generated reports:"
echo "     - demo_report.json"
echo "     - example_local_report.json"
echo ""
echo "  2. Try remote scanning:"
echo "     python3 main.py --mode remote --host IP --user USER --key-file KEY"
echo ""
echo "  3. Customize software targets:"
echo "     Edit software_config.json"
echo ""
echo "  4. Read documentation:"
echo "     - README.md (full docs)"
echo "     - QUICKSTART.md (quick reference)"
echo "     - PROJECT_SUMMARY.md (overview)"
echo ""
echo "For help: python3 main.py --help"
echo ""
