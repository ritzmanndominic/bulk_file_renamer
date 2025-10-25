#!/bin/bash

# Build macOS Installer for Bulk File Renamer
# Copyright (c) 2024 Dominic Ritzmann
# Licensed under the MIT License
# This script builds the macOS app and creates a DMG installer

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building macOS installer for Bulk File Renamer...${NC}"

# Check if we're in the right directory
if [ ! -f "../../main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run from installer/macos/ directory.${NC}"
    exit 1
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}Error: PyInstaller not found. Please install it:${NC}"
    echo -e "${YELLOW}pip install pyinstaller${NC}"
    exit 1
fi

# Change to project root
cd ../..

echo -e "${YELLOW}Building macOS application...${NC}"

# Build the macOS app
pyinstaller --onefile --windowed \
    --name "Bulk File Renamer" \
    --add-data "languages:languages" \
    --add-data "legal:legal" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.dominic-ritzmann.bulk-file-renamer" \
    --icon "assets/app.icns" \
    main.py

# Check if the app was created
if [ ! -d "dist/Bulk File Renamer.app" ]; then
    echo -e "${RED}Error: Failed to create macOS app${NC}"
    exit 1
fi

echo -e "${GREEN}✅ macOS app built successfully!${NC}"

# Go back to installer directory
cd installer/macos

# Create the DMG installer
echo -e "${YELLOW}Creating DMG installer...${NC}"
chmod +x create_advanced_dmg.sh
./create_advanced_dmg.sh

echo -e "${GREEN}✅ macOS installer created successfully!${NC}"
echo -e "${GREEN}Output: BulkFileRenamer_macOS_Installer.dmg${NC}"
echo -e "${BLUE}Size: $(du -h BulkFileRenamer_macOS_Installer.dmg | cut -f1)${NC}"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Test the DMG on a clean macOS system"
echo -e "2. For distribution, run: ./sign_notarize.sh"
echo -e "3. Upload the DMG file for distribution"

