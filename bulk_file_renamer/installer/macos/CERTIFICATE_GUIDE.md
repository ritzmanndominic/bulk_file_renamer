# Apple Developer Certificate Guide

## 🎯 What You Need

For a professional macOS PKG installer, you need **TWO** certificates:

1. **Developer ID Application** - Signs the `.app` bundle
2. **Developer ID Installer** - Signs the `.pkg` installer

## 💰 Cost

- **Apple Developer Program**: $99/year
- **Includes**: Both certificates + notarization access

## 📋 Step-by-Step Process

### 1. Sign Up for Apple Developer Program

1. Go to: https://developer.apple.com/programs/
2. Click "Enroll" 
3. Choose "Individual" or "Organization"
4. Pay $99/year
5. Wait for approval (usually instant for individuals)

### 2. Create Certificates

1. Go to: https://developer.apple.com/account/
2. Navigate to: **Certificates, Identifiers & Profiles**
3. Click **Certificates** in the sidebar
4. Click the **+** button to create new certificate

### 3. Create Developer ID Application Certificate

1. Select **Developer ID Application**
2. Click **Continue**
3. Upload a Certificate Signing Request (CSR)
4. Download the certificate
5. Double-click to install in Keychain

### 4. Create Developer ID Installer Certificate

1. Select **Developer ID Installer**
2. Click **Continue**
3. Upload the same CSR
4. Download the certificate
5. Double-click to install in Keychain

### 5. Create Certificate Signing Request (CSR)

If you don't have a CSR:

1. Open **Keychain Access**
2. Go to **Keychain Access** → **Certificate Assistant** → **Request a Certificate From a Certificate Authority**
3. Fill in:
   - **User Email Address**: Your Apple ID email
   - **Common Name**: Your name
   - **CA Email Address**: Leave blank
   - **Request is**: Saved to disk
4. Save the CSR file

## 🔧 Using the Certificates

### Sign the App
```bash
./sign_app.sh
```

### Sign the PKG Installer
```bash
./sign_installer.sh
```

## 🚀 Full Distribution Process

1. **Sign the app** with Developer ID Application
2. **Create PKG installer** with signed app
3. **Sign the PKG** with Developer ID Installer
4. **Notarize with Apple** (optional but recommended)
5. **Distribute** - works on all Macs without warnings

## ⚡ Quick Start (Testing)

If you just want to test locally:

1. **Right-click** the app in Applications
2. **Select "Open"**
3. **Click "Open"** in security dialog
4. **App launches** and is added to security exceptions

## 📞 Support

- **Apple Developer Support**: https://developer.apple.com/support/
- **Documentation**: https://developer.apple.com/documentation/
- **Forums**: https://developer.apple.com/forums/
