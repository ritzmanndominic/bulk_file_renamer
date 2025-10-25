#!/bin/bash

# Test script for the new macOS installer

echo "Testing the new macOS installer..."

# Check if the PKG file exists
if [ -f "BulkFileRenamer_macOS_Installer.pkg" ]; then
    echo "✅ PKG installer found"
    echo "Size: $(du -h BulkFileRenamer_macOS_Installer.pkg | cut -f1)"
else
    echo "❌ PKG installer not found"
fi

# Check if the app exists in dist
if [ -d "../../dist/Bulk File Renamer.app" ]; then
    echo "✅ macOS app found in dist/"
else
    echo "❌ macOS app not found in dist/"
fi

echo ""
echo "To test the installer:"
echo "1. Double-click BulkFileRenamer_macOS_Installer.pkg"
echo "2. Follow the installation wizard"
echo "3. Check if the app appears in Applications"
echo "4. Try launching the app"

