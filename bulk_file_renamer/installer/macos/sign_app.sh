#!/bin/bash

# Bulk File Renamer - App Signing Script
# This script signs the app with a proper developer certificate

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 App Signing Script for Bulk File Renamer${NC}"
echo -e "${BLUE}===========================================${NC}"

# Configuration
APP_NAME="Bulk File Renamer"
BUNDLE_ID="com.dominic-ritzmann.bulk-file-renamer"

# Check if we're in the right directory
if [ ! -f "../../main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run from installer/macos/ directory.${NC}"
    exit 1
fi

# Change to project root
cd ../..

# Check if the app exists
if [ ! -d "dist/$APP_NAME.app" ]; then
    echo -e "${RED}Error: App not found. Please build the app first.${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Checking for developer certificates...${NC}"

# List available certificates
echo -e "${BLUE}Available Developer ID certificates:${NC}"
security find-identity -v -p codesigning | grep "Developer ID Application" || echo -e "${RED}No Developer ID certificates found${NC}"

echo ""
echo -e "${YELLOW}📋 To sign the app, you need:${NC}"
echo -e "1. An Apple Developer account (\$99/year)"
echo -e "2. A Developer ID Application certificate"
echo -e "3. The certificate installed in your Keychain"
echo ""

# Check if user has certificates
APP_CERT=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | cut -d'"' -f2)
INSTALLER_CERT=$(security find-identity -v -p codesigning | grep "Developer ID Installer" | head -1 | cut -d'"' -f2)

if [ -n "$APP_CERT" ]; then
    echo -e "${GREEN}✅ Developer ID Application certificate found!${NC}"
    echo -e "${BLUE}Using certificate: $APP_CERT${NC}"
    
    echo -e "${YELLOW}Signing the app...${NC}"
    
    # Sign the app
    codesign --force --deep --sign "$APP_CERT" "dist/$APP_NAME.app"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ App signed successfully!${NC}"
        
        # Verify the signature
        echo -e "${YELLOW}Verifying signature...${NC}"
        codesign -dv --verbose=4 "dist/$APP_NAME.app"
        
        # Check Gatekeeper status
        echo -e "${YELLOW}Checking Gatekeeper status...${NC}"
        if spctl -a -v "dist/$APP_NAME.app" 2>&1 | grep -q "accepted"; then
            echo -e "${GREEN}✅ App accepted by Gatekeeper!${NC}"
        else
            echo -e "${YELLOW}⚠️  App may still need notarization for full Gatekeeper approval${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}🎉 Signing complete!${NC}"
        echo -e "${YELLOW}Next steps for full distribution:${NC}"
        echo -e "1. Create a PKG installer with the signed app"
        echo -e "2. Notarize the PKG with Apple"
        echo -e "3. The app will work on all Macs without security warnings"
        
    else
        echo -e "${RED}❌ Signing failed!${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ No Developer ID certificate found${NC}"
    echo ""
    echo -e "${YELLOW}📋 To get a certificate:${NC}"
    echo -e "1. Sign up for Apple Developer Program (\$99/year)"
    echo -e "2. Go to developer.apple.com"
    echo -e "3. Create a Developer ID Application certificate"
    echo -e "4. Download and install it in your Keychain"
    echo -e "5. Run this script again"
    echo ""
    echo -e "${BLUE}Alternative: Use the immediate fix script for testing${NC}"
    echo -e "./fix_security.sh"
fi
