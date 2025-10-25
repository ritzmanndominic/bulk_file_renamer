#!/bin/bash

# Bulk File Renamer - PKG Installer Signing Script
# This script signs the PKG installer with a Developer ID Installer certificate

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 PKG Installer Signing Script${NC}"
echo -e "${BLUE}===============================${NC}"

# Configuration
PKG_NAME="BulkFileRenamer_macOS_Installer.pkg"

# Check if we're in the right directory
if [ ! -f "$PKG_NAME" ]; then
    echo -e "${RED}Error: $PKG_NAME not found. Please run from installer/macos/ directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Checking for Developer ID Installer certificate...${NC}"

# Check for installer certificate
INSTALLER_CERT=$(security find-identity -v -p codesigning | grep "Developer ID Installer" | head -1 | cut -d'"' -f2)

if [ -n "$INSTALLER_CERT" ]; then
    echo -e "${GREEN}✅ Developer ID Installer certificate found!${NC}"
    echo -e "${BLUE}Using certificate: $INSTALLER_CERT${NC}"
    
    echo -e "${YELLOW}Signing the PKG installer...${NC}"
    
    # Sign the PKG installer
    productsign --sign "$INSTALLER_CERT" "$PKG_NAME" "${PKG_NAME%.pkg}_signed.pkg"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PKG installer signed successfully!${NC}"
        
        # Verify the signature
        echo -e "${YELLOW}Verifying signature...${NC}"
        pkgutil --check-signature "${PKG_NAME%.pkg}_signed.pkg"
        
        echo ""
        echo -e "${GREEN}🎉 Signing complete!${NC}"
        echo -e "${BLUE}Signed installer: ${PKG_NAME%.pkg}_signed.pkg${NC}"
        echo -e "${YELLOW}Size: $(du -h "${PKG_NAME%.pkg}_signed.pkg" | cut -f1)${NC}"
        
        echo ""
        echo -e "${YELLOW}📋 Next steps for full distribution:${NC}"
        echo -e "1. Notarize the signed PKG with Apple"
        echo -e "2. The installer will work on all Macs without security warnings"
        echo -e "3. Users can install directly without right-clicking"
        
        # Ask if user wants to replace the original
        echo ""
        echo -e "${YELLOW}Replace original PKG with signed version? (y/n):${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mv "${PKG_NAME%.pkg}_signed.pkg" "$PKG_NAME"
            echo -e "${GREEN}✅ Original PKG replaced with signed version${NC}"
        else
            echo -e "${BLUE}Signed PKG saved as: ${PKG_NAME%.pkg}_signed.pkg${NC}"
        fi
        
    else
        echo -e "${RED}❌ Signing failed!${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ No Developer ID Installer certificate found${NC}"
    echo ""
    echo -e "${YELLOW}📋 To get a certificate:${NC}"
    echo -e "1. Sign up for Apple Developer Program (\$99/year)"
    echo -e "2. Go to developer.apple.com"
    echo -e "3. Navigate to: Certificates, Identifiers & Profiles"
    echo -e "4. Create a 'Developer ID Installer' certificate"
    echo -e "5. Download and install it in your Keychain"
    echo -e "6. Run this script again"
    echo ""
    echo -e "${BLUE}📝 Certificate Types:${NC}"
    echo -e "• Developer ID Application - Signs the .app bundle"
    echo -e "• Developer ID Installer - Signs the .pkg installer (what you need!)"
    echo ""
    echo -e "${YELLOW}Alternative: Use the immediate fix for testing${NC}"
    echo -e "./fix_security.sh"
fi
