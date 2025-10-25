#!/bin/bash

# Bulk File Renamer - Advanced macOS DMG Installer
# Creates a professional DMG with custom styling

set -e

# Configuration
APP_NAME="Bulk File Renamer"
APP_VERSION="1.0.0"
DMG_NAME="BulkFileRenamer_macOS_Installer"
DMG_SIZE="200m"
VOLUME_NAME="Bulk File Renamer"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Creating advanced macOS DMG installer...${NC}"

# Check prerequisites
if [ ! -d "../../dist/$APP_NAME.app" ]; then
    echo -e "${RED}Error: $APP_NAME.app not found in ../../dist/${NC}"
    exit 1
fi

# Create temporary directory
TEMP_DIR="temp_dmg_advanced"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy app
echo -e "${YELLOW}Setting up DMG contents...${NC}"
cp -R "../../dist/$APP_NAME.app" "$TEMP_DIR/"

# Create Applications symlink
ln -s /Applications "$TEMP_DIR/Applications"

# Create background directory for styling
mkdir -p "$TEMP_DIR/.background"

# Create a simple background (if no custom background exists)
if [ ! -f "dmg_background.png" ]; then
    echo -e "${YELLOW}Creating default background...${NC}"
    # Create a simple background using ImageMagick if available
    if command -v convert &> /dev/null; then
        convert -size 600x400 xc:'#f0f0f0' -pointsize 24 -fill '#333333' -annotate +50+200 'Bulk File Renamer' "$TEMP_DIR/.background/background.png" 2>/dev/null || true
    fi
fi

# Create README
cat > "$TEMP_DIR/README.txt" << 'EOF'
Bulk File Renamer - Installation Guide

📱 INSTALLATION:
1. Drag "Bulk File Renamer.app" to the "Applications" folder
2. Launch from Applications or Spotlight

💻 SYSTEM REQUIREMENTS:
• macOS 10.15 (Catalina) or later
• 64-bit Intel or Apple Silicon

🔧 FEATURES:
• Bulk file renaming with patterns
• Preview before renaming
• Undo/redo support
• Multiple file types support
• Professional interface

📞 SUPPORT:
GitHub: https://github.com/dominic-ritzmann/bulk-file-renamer

© 2025 Dominic Ritzmann. All rights reserved.
EOF

# Create the DMG
echo -e "${YELLOW}Creating DMG file...${NC}"
hdiutil create -srcfolder "$TEMP_DIR" -volname "$VOLUME_NAME" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDZO -size "$DMG_SIZE" "$DMG_NAME.dmg"

# Mount the DMG to set custom view options
echo -e "${YELLOW}Setting up DMG view options...${NC}"
MOUNT_POINT=$(hdiutil attach "$DMG_NAME.dmg" | grep "Volumes" | awk '{print $3}')

# Set view options (if possible)
if [ -n "$MOUNT_POINT" ]; then
    # Try to set custom view options
    osascript -e "tell application \"Finder\"" -e "set the view options of the icon view options of container window of folder \"$VOLUME_NAME\" of disk \"$VOLUME_NAME\" to {icon size:128, text size:12, arrangement:not arranged}" -e "end tell" 2>/dev/null || true
    
    # Unmount
    hdiutil detach "$MOUNT_POINT" 2>/dev/null || true
fi

# Clean up
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Advanced DMG installer created successfully!${NC}"
echo -e "${GREEN}Output: $DMG_NAME.dmg${NC}"
echo -e "${BLUE}Size: $(du -h "$DMG_NAME.dmg" | cut -f1)${NC}"
echo -e "${YELLOW}Note: For code signing and notarization, use the sign_notarize.sh script${NC}"

