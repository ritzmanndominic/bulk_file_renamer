#!/bin/bash

# Bulk File Renamer - macOS Installer Builder
# Creates a professional PKG installer with GUI installation wizard

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🍎 Building macOS installer for Bulk File Renamer...${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if we're in the right directory
if [ ! -f "../../main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run from installer/macos/ directory.${NC}"
    exit 1
fi

# Change to project root
cd ../..

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}Error: Virtual environment not found. Please create one:${NC}"
    echo -e "${YELLOW}python -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}📥 Installing PyInstaller...${NC}"
    pip install pyinstaller
fi

echo -e "${YELLOW}🔨 Building macOS application...${NC}"

# Clean previous builds
rm -rf dist/ build/

# Build the macOS app using the spec file
pyinstaller bulk_file_renamer_macos.spec

# Check if the app was created
if [ ! -d "dist/Bulk File Renamer.app" ]; then
    echo -e "${RED}Error: Failed to create macOS app${NC}"
    exit 1
fi

echo -e "${GREEN}✅ macOS app built successfully!${NC}"

# Go back to installer directory
cd installer/macos

# Create the PKG installer
echo -e "${YELLOW}📦 Creating PKG installer...${NC}"
chmod +x create_pkg.sh
./create_pkg.sh

echo -e "${GREEN}✅ macOS installer created successfully!${NC}"
echo -e "${GREEN}Output: BulkFileRenamer_macOS_Installer.pkg${NC}"
echo -e "${BLUE}Size: $(du -h BulkFileRenamer_macOS_Installer.pkg | cut -f1)${NC}"

echo ""
echo -e "${YELLOW}📋 Installation Instructions:${NC}"
echo -e "1. Double-click the PKG file to start installation"
echo -e "2. Follow the installation wizard"
echo -e "3. Right-click the app in Applications and select 'Open' (first time only)"
echo -e "4. The app will be installed and ready to use"

echo ""
echo -e "${YELLOW}🚀 Ready for distribution!${NC}"

