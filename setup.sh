#!/bin/bash
#
# setup.sh - Installation script for InkAutoGen extension
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
EXTENSION_NAME="inkautogen"
INKSCAPE_EXTENSIONS_DIR="$HOME/.config/inkscape/extensions"
PYTHON_VERSION="3.8"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}InkAutoGen Installation Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print section headers
print_header() {
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
}

# Check Python version
print_header "Checking Python version"
python3 --version
if ! python3 --version | grep -q "Python ${PYTHON_VERSION}"; then
    echo -e "${RED}Warning: Python ${PYTHON_VERSION}+ is recommended${NC}"
fi

# Check if Inkscape is installed
print_header "Checking Inkscape installation"
if command -v inkscape &> /dev/null; then
    INKSCAPE_VERSION=$(inkscape --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} Inkscape found: $INKSCAPE_VERSION"
else
    echo -e "${RED}✗${NC} Inkscape not found. Please install Inkscape 1.2+"
    exit 1
fi

# Create extensions directory if it doesn't exist
print_header "Creating extensions directory"
mkdir -p "$INKSCAPE_EXTENSIONS_DIR"
echo -e "${GREEN}✓${NC} Extensions directory: $INKSCAPE_EXTENSIONS_DIR"

# Install Python dependencies
print_header "Installing Python dependencies"
echo "Installing required packages..."

# Try pip3, then fallback to pip3 command with sudo
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3 install"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip install"
else
    echo -e "${RED}✗${NC} pip not found"
    exit 1
fi

# Install dependencies
$PIP_CMD lxml chardet PyPDF2
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Copy extension files
print_header "Copying extension files"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy main files
cp "$SCRIPT_DIR/inkautogen.py" "$INKSCAPE_EXTENSIONS_DIR/"
echo -e "${GREEN}✓${NC} Copied inkautogen.py"

cp "$SCRIPT_DIR/inkautogen.inx" "$INKSCAPE_EXTENSIONS_DIR/"
echo -e "${GREEN}✓${NC} Copied inkautogen.inx"

# Copy modules directory
if [ -d "$SCRIPT_DIR/modules" ]; then
    cp -r "$SCRIPT_DIR/modules" "$INKSCAPE_EXTENSIONS_DIR/"
    echo -e "${GREEN}✓${NC} Copied modules directory"
else
    echo -e "${RED}✗${NC} modules directory not found"
    exit 1
fi

# Set permissions
print_header "Setting file permissions"
chmod +x "$INKSCAPE_EXTENSIONS_DIR/inkautogen.py"
chmod 644 "$INKSCAPE_EXTENSIONS_DIR/inkautogen.inx"
find "$INKSCAPE_EXTENSIONS_DIR/modules" -name "*.py" -exec chmod 644 {} \;
echo -e "${GREEN}✓${NC} File permissions set"

# Verification
print_header "Verifying installation"

# Check if files exist
FILES=(
    "$INKSCAPE_EXTENSIONS_DIR/inkautogen.py"
    "$INKSCAPE_EXTENSIONS_DIR/inkautogen.inx"
    "$INKSCAPE_EXTENSIONS_DIR/modules/config.py"
    "$INKSCAPE_EXTENSIONS_DIR/modules/version.py"
)

ALL_FOUND=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} Found: $(basename $file)"
    else
        echo -e "${RED}✗${NC} Missing: $(basename $file)"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = true ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Installation successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "To use InkAutoGen:"
    echo "  1. Open Inkscape"
    echo "  2. Navigate to: Extensions → Export → InkAutoGen"
    echo "  3. Follow the on-screen instructions"
    echo ""
    echo -e "${YELLOW}Note: You may need to restart Inkscape for the extension to appear${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Installation incomplete${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
