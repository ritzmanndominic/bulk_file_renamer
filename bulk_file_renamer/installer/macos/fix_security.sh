#!/bin/bash

# Bulk File Renamer - macOS Security Fix Script
# This script provides solutions for macOS security issues

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 macOS Security Fix for Bulk File Renamer${NC}"
echo -e "${BLUE}===========================================${NC}"

# Check if we're in the right directory
if [ ! -f "../../main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run from installer/macos/ directory.${NC}"
    exit 1
fi

# Change to project root
cd ../..

# Check if the app exists
if [ ! -d "dist/Bulk File Renamer.app" ]; then
    echo -e "${RED}Error: App not found. Please build the app first.${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Current Security Status:${NC}"

# Check current signature
echo -e "${BLUE}Signature Status:${NC}"
codesign -dv --verbose=4 "dist/Bulk File Renamer.app" 2>&1 | grep -E "(Signature|TeamIdentifier)" || echo "No signature found"

# Check Gatekeeper status
echo -e "${BLUE}Gatekeeper Status:${NC}"
if spctl -a -v "dist/Bulk File Renamer.app" 2>&1 | grep -q "rejected"; then
    echo -e "${RED}❌ REJECTED by Gatekeeper${NC}"
else
    echo -e "${GREEN}✅ Accepted by Gatekeeper${NC}"
fi

echo ""
echo -e "${YELLOW}🛠️  Available Solutions:${NC}"
echo ""
echo -e "${GREEN}1. IMMEDIATE FIX (For Testing):${NC}"
echo -e "   • Right-click the app in Applications"
echo -e "   • Select 'Open' from the context menu"
echo -e "   • Click 'Open' in the security dialog"
echo -e "   • This will add the app to your security exceptions"
echo ""
echo -e "${GREEN}2. SYSTEM-WIDE FIX (For Development):${NC}"
echo -e "   • Disable Gatekeeper temporarily:"
echo -e "   • sudo spctl --master-disable"
echo -e "   • (Re-enable later with: sudo spctl --master-enable)"
echo ""
echo -e "${GREEN}3. PROPER SOLUTION (For Distribution):${NC}"
echo -e "   • Get an Apple Developer ID certificate"
echo -e "   • Sign the app with: codesign --sign \"Developer ID Application: Your Name\""
echo -e "   • Notarize the app with Apple"
echo -e "   • This requires a paid Apple Developer account (\$99/year)"
echo ""

# Offer to apply immediate fix
echo -e "${YELLOW}Would you like me to apply the immediate fix? (y/n):${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Applying immediate fix...${NC}"
    
    # Remove quarantine attribute
    xattr -d com.apple.quarantine "dist/Bulk File Renamer.app" 2>/dev/null || echo "No quarantine attribute found"
    
    # Add to security exceptions (this requires user interaction)
    echo -e "${GREEN}✅ Quarantine attribute removed${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "1. Copy the app to Applications:"
    echo -e "   cp -R 'dist/Bulk File Renamer.app' /Applications/"
    echo -e "2. Right-click the app in Applications and select 'Open'"
    echo -e "3. Click 'Open' in the security dialog"
    echo -e "4. The app will be added to your security exceptions"
    
    # Copy to Applications
    echo -e "${YELLOW}Copying app to Applications...${NC}"
    rm -rf "/Applications/Bulk File Renamer.app"
    cp -R "dist/Bulk File Renamer.app" "/Applications/"
    echo -e "${GREEN}✅ App copied to Applications${NC}"
    
    echo ""
    echo -e "${GREEN}🎉 Immediate fix applied!${NC}"
    echo -e "${YELLOW}Now try:${NC}"
    echo -e "1. Go to Applications folder"
    echo -e "2. Right-click 'Bulk File Renamer'"
    echo -e "3. Select 'Open'"
    echo -e "4. Click 'Open' in the security dialog"
    echo -e "5. The app should launch and be added to your security exceptions"
    
else
    echo -e "${YELLOW}No immediate fix applied.${NC}"
    echo -e "${BLUE}You can manually apply the fix by:${NC}"
    echo -e "1. Right-clicking the app in Applications"
    echo -e "2. Selecting 'Open' from the context menu"
    echo -e "3. Clicking 'Open' in the security dialog"
fi

echo ""
echo -e "${BLUE}📋 For Production Distribution:${NC}"
echo -e "• Get an Apple Developer ID certificate (\$99/year)"
echo -e "• Sign the app with proper certificate"
echo -e "• Notarize with Apple"
echo -e "• This ensures the app works on all Macs without security warnings"
