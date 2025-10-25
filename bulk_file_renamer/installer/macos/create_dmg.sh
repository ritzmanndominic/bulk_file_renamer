#!/bin/bash

# Bulk File Renamer - macOS DMG Installer Creator
# Copyright (c) 2024 Dominic Ritzmann
# Licensed under the MIT License
# Creates a professional DMG installer for macOS

set -e  # Exit on any error

# Configuration
APP_NAME="Bulk File Renamer"
APP_VERSION="1.0.0"
DMG_NAME="BulkFileRenamer_macOS_Installer"
DMG_SIZE="200m"
DMG_FORMAT="UDZO"
DMG_ICON="app.icns"
BACKGROUND_IMAGE="dmg_background.png"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating macOS DMG installer for $APP_NAME...${NC}"

# Check if we're in the right directory
if [ ! -d "../../dist" ]; then
    echo -e "${RED}Error: dist directory not found. Please run from installer/macos/ directory.${NC}"
    exit 1
fi

# Check if the app exists
if [ ! -d "../../dist/$APP_NAME.app" ]; then
    echo -e "${RED}Error: $APP_NAME.app not found in ../../dist/${NC}"
    echo -e "${YELLOW}Please build the macOS app first using PyInstaller${NC}"
    exit 1
fi

# Create temporary DMG directory
TEMP_DMG_DIR="temp_dmg"
rm -rf "$TEMP_DMG_DIR"
mkdir -p "$TEMP_DMG_DIR"

# Copy the app to the DMG directory
echo -e "${YELLOW}Copying application...${NC}"
cp -R "../../dist/$APP_NAME.app" "$TEMP_DMG_DIR/"

# Create Applications symlink
echo -e "${YELLOW}Creating Applications symlink...${NC}"
ln -s /Applications "$TEMP_DMG_DIR/Applications"

# Create README file
echo -e "${YELLOW}Creating README...${NC}"
cat > "$TEMP_DMG_DIR/README.txt" << EOF
Bulk File Renamer - Installation Instructions

1. Drag "Bulk File Renamer.app" to the "Applications" folder
2. The app will be installed to /Applications/Bulk File Renamer.app
3. You can then launch it from Applications or Spotlight

System Requirements:
- macOS 10.15 (Catalina) or later
- 64-bit Intel or Apple Silicon processor

For support, visit: https://github.com/dominic-ritzmann/bulk-file-renamer
EOF

# Create the DMG
echo -e "${YELLOW}Creating DMG file...${NC}"
hdiutil create -srcfolder "$TEMP_DMG_DIR" -volname "$APP_NAME" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDZO -size "$DMG_SIZE" "$DMG_NAME.dmg"

# Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "$TEMP_DMG_DIR"

echo -e "${GREEN}✅ DMG installer created successfully!${NC}"
echo -e "${GREEN}Output: $DMG_NAME.dmg${NC}"
echo -e "${BLUE}Size: $(du -h "$DMG_NAME.dmg" | cut -f1)${NC}"

