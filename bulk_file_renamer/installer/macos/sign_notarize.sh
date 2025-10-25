#!/bin/bash

# Bulk File Renamer - Code Signing and Notarization Script
# For professional macOS distribution

set -e

# Configuration
APP_NAME="Bulk File Renamer"
APP_VERSION="1.0.0"
DMG_NAME="BulkFileRenamer_macOS_Installer"
BUNDLE_ID="com.dominic-ritzmann.bulk-file-renamer"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Code Signing and Notarization for $APP_NAME${NC}"

# Check if we have the necessary tools
if ! command -v codesign &> /dev/null; then
    echo -e "${RED}Error: codesign not found. Please install Xcode Command Line Tools.${NC}"
    exit 1
fi

if ! command -v xcrun &> /dev/null; then
    echo -e "${RED}Error: xcrun not found. Please install Xcode Command Line Tools.${NC}"
    exit 1
fi

# Check if we have a developer certificate
echo -e "${YELLOW}Checking for developer certificate...${NC}"
if ! security find-identity -v -p codesigning | grep -q "Developer ID Application"; then
    echo -e "${RED}Error: No 'Developer ID Application' certificate found.${NC}"
    echo -e "${YELLOW}Please:${NC}"
    echo -e "1. Join the Apple Developer Program"
    echo -e "2. Create a 'Developer ID Application' certificate in Keychain Access"
    echo -e "3. Run this script again"
    exit 1
fi

# Get the certificate identity
CERT_IDENTITY=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | awk '{print $2}')
echo -e "${GREEN}Found certificate: $CERT_IDENTITY${NC}"

# Check if the app exists
if [ ! -d "../../dist/$APP_NAME.app" ]; then
    echo -e "${RED}Error: $APP_NAME.app not found in ../../dist/${NC}"
    exit 1
fi

# Sign the app
echo -e "${YELLOW}Signing the application...${NC}"
codesign --force --deep --sign "$CERT_IDENTITY" "../../dist/$APP_NAME.app"

# Verify the signature
echo -e "${YELLOW}Verifying signature...${NC}"
codesign --verify --verbose "../../dist/$APP_NAME.app"
spctl --assess --verbose "../../dist/$APP_NAME.app"

# Create DMG
echo -e "${YELLOW}Creating signed DMG...${NC}"
./create_advanced_dmg.sh

# Sign the DMG
echo -e "${YELLOW}Signing the DMG...${NC}"
codesign --force --sign "$CERT_IDENTITY" "$DMG_NAME.dmg"

# Verify DMG signature
echo -e "${YELLOW}Verifying DMG signature...${NC}"
codesign --verify --verbose "$DMG_NAME.dmg"

echo -e "${GREEN}✅ Code signing completed successfully!${NC}"
echo -e "${BLUE}Signed DMG: $DMG_NAME.dmg${NC}"

# Notarization (optional - requires Apple Developer account)
echo -e "${YELLOW}For notarization, you'll need:${NC}"
echo -e "1. Apple Developer account"
echo -e "2. App-specific password"
echo -e "3. Run: xcrun notarytool submit $DMG_NAME.dmg --keychain-profile 'notarytool' --wait"
echo -e "4. Run: xcrun stapler staple $DMG_NAME.dmg"

echo -e "${GREEN}Ready for distribution!${NC}"

