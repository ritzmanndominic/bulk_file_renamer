#!/bin/bash

# Bulk File Renamer - macOS PKG Installer Creator
# Copyright (c) 2024 Dominic Ritzmann
# Licensed under the MIT License
# Creates a professional PKG installer with GUI installation wizard

set -e

# Configuration
APP_NAME="Bulk File Renamer"
APP_VERSION="1.0.0"
PKG_NAME="BulkFileRenamer_macOS_Installer"
BUNDLE_ID="com.dominic-ritzmann.bulk-file-renamer"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Creating macOS PKG installer for $APP_NAME...${NC}"

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

# Create temporary directories
TEMP_DIR="temp_pkg"
SCRIPTS_DIR="$TEMP_DIR/scripts"
PAYLOAD_DIR="$TEMP_DIR/payload"

echo -e "${YELLOW}Setting up PKG structure...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$PAYLOAD_DIR"

# Copy the app to payload directory
echo -e "${YELLOW}Copying application...${NC}"
cp -R "../../dist/$APP_NAME.app" "$PAYLOAD_DIR/"

# Create pre-installation script
echo -e "${YELLOW}Creating installation scripts...${NC}"
cat > "$SCRIPTS_DIR/preinstall" << 'EOF'
#!/bin/bash

# Pre-installation script for Bulk File Renamer
echo "Preparing to install Bulk File Renamer..."

# Check if the app is already installed
if [ -d "/Applications/Bulk File Renamer.app" ]; then
    echo "Removing existing installation..."
    rm -rf "/Applications/Bulk File Renamer.app"
fi

# Check if the app is currently running
if pgrep -f "Bulk File Renamer" > /dev/null; then
    echo "Bulk File Renamer is currently running. Please close it before installing."
    exit 1
fi

echo "Pre-installation completed successfully."
exit 0
EOF

# Create post-installation script
cat > "$SCRIPTS_DIR/postinstall" << 'EOF'
#!/bin/bash

# Post-installation script for Bulk File Renamer
echo "Finalizing Bulk File Renamer installation..."

# Set proper permissions
chmod -R 755 "/Applications/Bulk File Renamer.app"

# Register with Launch Services
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "/Applications/Bulk File Renamer.app"

echo "Bulk File Renamer has been successfully installed!"
echo "You can now launch it from Applications or Spotlight."

exit 0
EOF

# Make scripts executable
chmod +x "$SCRIPTS_DIR/preinstall"
chmod +x "$SCRIPTS_DIR/postinstall"

# Create distribution XML for the installer
echo -e "${YELLOW}Creating installer configuration...${NC}"
cat > "$TEMP_DIR/distribution.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
    <title>Bulk File Renamer $APP_VERSION</title>
    <organization>com.dominic-ritzmann</organization>
    <domains enable_localSystem="true"/>
    <options customize="never" require-scripts="true" rootVolumeOnly="true"/>
    
    <!-- Define the volume requirements -->
    <volume-check>
        <allowed-os-versions>
            <os-version min="10.15.0"/>
        </allowed-os-versions>
    </volume-check>
    
    <!-- Installation choices -->
    <choices-outline>
        <line choice="default">
            <line choice="BulkFileRenamer"/>
        </line>
    </choices-outline>
    
    <choice id="default"/>
    <choice id="BulkFileRenamer" visible="false">
        <pkg-ref id="$BUNDLE_ID"/>
    </choice>
    
    <pkg-ref id="$BUNDLE_ID" version="$APP_VERSION" onConclusion="none">BulkFileRenamer.pkg</pkg-ref>
    
    <!-- Installation UI -->
    <welcome file="welcome.html" mime-type="text/html"/>
    <license file="license.html" mime-type="text/html"/>
    <conclusion file="conclusion.html" mime-type="text/html"/>
    
    <!-- Installation requirements -->
    <installation-check script="pm_install_check();"/>
    <script>
    <![CDATA[
        function pm_install_check() {
            if(!(system.compareVersions(system.version.ProductVersion, '10.15.0') >= 0)) {
                my.result.title = 'System Requirements Not Met';
                my.result.message = 'Bulk File Renamer requires macOS 10.15 (Catalina) or later.';
                my.result.type = 'Fatal';
                return false;
            }
            return true;
        }
    ]]>
    </script>
</installer-gui-script>
EOF

# Create welcome page with proper styling
cat > "$TEMP_DIR/welcome.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to Bulk File Renamer</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 20px; 
            background-color: #ffffff;
            color: #1d1d1f;
        }
        h1 { 
            color: #1d1d1f; 
            font-size: 24px;
            margin-bottom: 20px;
        }
        h2 { 
            color: #1d1d1f; 
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        p { 
            color: #1d1d1f; 
            line-height: 1.5; 
            margin-bottom: 10px;
        }
        .feature { 
            margin: 10px 0; 
            color: #1d1d1f;
        }
        .feature strong { 
            color: #1d1d1f; 
            font-weight: 600;
        }
    </style>
</head>
<body>
    <h1>Welcome to Bulk File Renamer</h1>
    <p>Thank you for choosing Bulk File Renamer! This installer will guide you through the installation process.</p>
    
    <h2>What's New in Version 1.0.0:</h2>
    <div class="feature"><strong>🎯 Bulk File Renaming:</strong> Rename multiple files at once with powerful patterns</div>
    <div class="feature"><strong>👀 Live Preview:</strong> See exactly what will happen before you rename</div>
    <div class="feature"><strong>↩️ Undo Support:</strong> Easily undo your last rename operation</div>
    <div class="feature"><strong>🌍 Multi-language:</strong> Available in English and German</div>
    <div class="feature"><strong>🎨 Modern Interface:</strong> Clean, intuitive design with dark/light themes</div>
    <div class="feature"><strong>⚡ Fast Performance:</strong> Optimized for handling large numbers of files</div>
    
    <p><strong>System Requirements:</strong> macOS 10.15 (Catalina) or later</p>
    <p>Click "Continue" to begin the installation.</p>
</body>
</html>
EOF

# Create license page with proper styling (matching welcome page)
cat > "$TEMP_DIR/license.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>License Agreement</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 20px; 
            background-color: #ffffff;
            color: #1d1d1f;
        }
        h1 { 
            color: #1d1d1f; 
            font-size: 24px;
            margin-bottom: 20px;
        }
        h2 { 
            color: #1d1d1f; 
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        h3 { 
            color: #1d1d1f; 
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 8px;
        }
        p { 
            color: #1d1d1f; 
            line-height: 1.5; 
            margin-bottom: 10px;
        }
        .license-text { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border: 1px solid #e9ecef;
        }
        strong {
            color: #1d1d1f;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <h1>Software License Agreement</h1>
    
    <div class="license-text">
        <h2>Bulk File Renamer - End User License Agreement</h2>
        
        <p><strong>Copyright © 2025 Dominic Ritzmann. All rights reserved.</strong></p>
        
        <h3>1. Grant of License</h3>
        <p>This software is provided as-is for personal and commercial use. You may install and use this software on multiple computers under your control.</p>
        
        <h3>2. Restrictions</h3>
        <p>You may not reverse engineer, decompile, or disassemble this software. You may not redistribute this software without explicit permission.</p>
        
        <h3>3. Disclaimer</h3>
        <p>This software is provided "as is" without warranty of any kind. The author shall not be liable for any damages arising from the use of this software.</p>
        
        <h3>4. Privacy</h3>
        <p>This software does not collect, store, or transmit any personal data. All file operations are performed locally on your computer.</p>
        
        <p>By clicking "Agree", you acknowledge that you have read and agree to the terms of this license agreement.</p>
    </div>
</body>
</html>
EOF

# Create conclusion page with proper styling (matching welcome page)
cat > "$TEMP_DIR/conclusion.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Installation Complete</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 20px; 
            background-color: #ffffff;
            color: #1d1d1f;
        }
        h1 { 
            color: #1d1d1f; 
            font-size: 24px;
            margin-bottom: 20px;
        }
        h2 { 
            color: #1d1d1f; 
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        p { 
            color: #1d1d1f; 
            line-height: 1.5; 
            margin-bottom: 10px;
        }
        .success { 
            background: #d4edda; 
            border: 1px solid #c3e6cb; 
            color: #155724; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
        }
        .next-steps { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border: 1px solid #e9ecef;
        }
        strong {
            color: #1d1d1f;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <h1>Installation Complete!</h1>
    
    <div class="success">
        <strong>✅ Bulk File Renamer has been successfully installed!</strong>
    </div>
    
    <div class="next-steps">
        <h2>What's Next?</h2>
        <p><strong>🚀 Launch the App:</strong> You can find Bulk File Renamer in your Applications folder or search for it in Spotlight.</p>
        <p><strong>📁 Start Renaming:</strong> Add files to the app and use powerful renaming patterns to organize your files.</p>
        <p><strong>⚙️ Customize:</strong> Explore the settings to change themes, languages, and preferences.</p>
    </div>
    
    <h2>Need Help?</h2>
    <p>• <strong>Documentation:</strong> Check the Help menu in the application</p>
    <p>• <strong>Support:</strong> Visit our GitHub repository for support and updates</p>
    <p>• <strong>Feedback:</strong> We'd love to hear your feedback and suggestions</p>
    
    <p>Thank you for choosing Bulk File Renamer!</p>
</body>
</html>
EOF

# Build the component package
echo -e "${YELLOW}Building component package...${NC}"
pkgbuild \
    --root "$PAYLOAD_DIR" \
    --scripts "$SCRIPTS_DIR" \
    --identifier "$BUNDLE_ID" \
    --version "$APP_VERSION" \
    --install-location "/Applications" \
    "$TEMP_DIR/BulkFileRenamer.pkg"

# Build the distribution package
echo -e "${YELLOW}Building distribution package...${NC}"
productbuild \
    --distribution "$TEMP_DIR/distribution.xml" \
    --package-path "$TEMP_DIR" \
    --resources "$TEMP_DIR" \
    "$PKG_NAME.pkg"

# Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ PKG installer created successfully!${NC}"
echo -e "${GREEN}Output: $PKG_NAME.pkg${NC}"
echo -e "${BLUE}Size: $(du -h "$PKG_NAME.pkg" | cut -f1)${NC}"

echo -e "${YELLOW}Installation Instructions:${NC}"
echo -e "1. Double-click the PKG file to start installation"
echo -e "2. Follow the installation wizard"
echo -e "3. The app will be installed to /Applications"
echo -e "4. Right-click the app in Applications and select 'Open' (first time only)"
echo -e "5. Launch from Applications or Spotlight"

