# macOS Installer - Quick Start Guide

## 🚀 When You're Ready to Launch macOS Version

### Step 1: Get Apple Developer Account
- **Cost**: $99/year
- **Sign up**: https://developer.apple.com/programs/
- **Wait**: Usually instant approval for individuals

### Step 2: Create Certificates
1. Go to: https://developer.apple.com/account/
2. Navigate to: **Certificates, Identifiers & Profiles**
3. Create **Developer ID Application** certificate
4. Create **Developer ID Installer** certificate
5. Download and install both in Keychain

### Step 3: Build and Sign
```bash
# Navigate to installer directory
cd installer/macos

# Build the app and PKG installer
./build_installer.sh

# Sign the app
./sign_app.sh

# Sign the PKG installer
./sign_installer.sh
```

### Step 4: Test and Distribute
- Test the signed PKG installer
- Distribute to users
- No more security warnings!

## 🧪 For Testing (No Certificate Needed)

```bash
# Apply immediate security fix
./fix_security.sh

# Then right-click app in Applications and select "Open"
```

## 📁 All Files Ready

- ✅ **Build scripts** - Ready to use
- ✅ **Signing scripts** - Ready to use  
- ✅ **Documentation** - Complete guides
- ✅ **PKG installer** - Professional GUI
- ✅ **Security fixes** - All issues resolved

## 🎯 You're 100% Ready!

When you decide to launch macOS version, everything is prepared. Just get the Apple Developer account and run the scripts! 🚀
