# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.
# 
# You may use this software for personal and professional purposes, including
# using it to organize and rename files as part of your business or selling
# files that have been processed using this software.
# 
# However, you may NOT modify, alter, or create derivative works of this software,
# or sell, distribute, or license this software itself without explicit written
# permission from the copyright holder.

"""
License Manager for Bulk File Renamer
Handles hardware fingerprinting and license validation
"""

import os
import platform
import hashlib
import json
from datetime import datetime
from typing import Optional, Tuple


def get_machine_fingerprint() -> str:
    """
    Generate unique hardware fingerprint for the current machine.
    This creates a unique identifier based on hardware characteristics.
    """
    try:
        # Get hardware identifiers
        cpu_id = platform.processor()
        machine = platform.machine()
        system = platform.system()
        node = platform.node()  # Computer name
        
        # Additional identifiers for better uniqueness
        try:
            import uuid
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                                  for ele in range(0,8*6,8)][::-1])
        except:
            mac_address = "unknown"
        
        # Create unique fingerprint
        fingerprint_data = f"{cpu_id}:{machine}:{system}:{node}:{mac_address}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:12]
    except Exception:
        # Fallback if any component fails
        return "unknown"


def generate_license_key(machine_id: str, secret_key: str = "BulkFileRenamer2024") -> str:
    """
    Generate license key for specific machine ID.
    This is used by the license generator tool.
    """
    combined = f"{machine_id}:{secret_key}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()


def validate_license_key(license_key: str, machine_id: str, secret_key: str = "BulkFileRenamer2024") -> bool:
    """
    Validate license key against machine ID.
    """
    expected_key = generate_license_key(machine_id, secret_key)
    return license_key.upper() == expected_key.upper()


class LicenseManager:
    """Manages license validation and activation for the application."""
    
    def __init__(self, app_name: str = "BulkFileRenamer"):
        self.app_name = app_name
        self.license_file = os.path.join(os.path.expanduser("~"), f".{app_name}_license.dat")
        self.machine_id = get_machine_fingerprint()
        self.embedded_license_file = os.path.join(os.path.dirname(__file__), "..", "..", "license.dat")
    
    def is_licensed(self) -> bool:
        """
        Check if the application is properly licensed for this machine.
        First checks embedded license, then user license, then auto-activates universal license.
        """
        # Check embedded license first (for pre-activated installations)
        if self._check_embedded_license():
            return True
        
        # Check user license (for manual activation)
        if self._check_user_license():
            return True
        
        # Check for universal license and auto-activate
        if self._check_and_activate_universal_license():
            return True
        
        return False
    
    def _check_embedded_license(self) -> bool:
        """Check if there's a valid embedded license file."""
        if not os.path.exists(self.embedded_license_file):
            return False
        
        try:
            with open(self.embedded_license_file, 'r', encoding='utf-8') as f:
                license_data = json.load(f)
            
            # Validate machine ID
            if license_data.get("machine_id") != self.machine_id:
                return False
            
            # Validate license key
            license_key = license_data.get("license_key", "")
            if not validate_license_key(license_key, self.machine_id):
                return False
            
            # Copy embedded license to user directory for future use
            self._copy_embedded_to_user_license(license_data)
            
            return True
            
        except Exception:
            return False
    
    def _check_user_license(self) -> bool:
        """Check if there's a valid user license file."""
        if not os.path.exists(self.license_file):
            return False
        
        try:
            with open(self.license_file, 'r', encoding='utf-8') as f:
                license_data = json.load(f)
            
            # Validate machine ID
            if license_data.get("machine_id") != self.machine_id:
                return False
            
            # Validate license key
            license_key = license_data.get("license_key", "")
            if not validate_license_key(license_key, self.machine_id):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _copy_embedded_to_user_license(self, license_data: dict):
        """Copy embedded license to user directory."""
        try:
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2)
        except Exception:
            pass  # Ignore errors when copying
    
    def _check_and_activate_universal_license(self) -> bool:
        """Check for universal license and auto-activate it."""
        if not os.path.exists(self.embedded_license_file):
            return False
        
        try:
            with open(self.embedded_license_file, 'r', encoding='utf-8') as f:
                license_data = json.load(f)
            
            # Check if it's a universal license
            if license_data.get("license_type") != "universal":
                return False
            
            # Auto-activate the universal license for this machine
            license_key = generate_license_key(self.machine_id)
            
            # Create activated license data
            activated_license = {
                "license_key": license_key,
                "machine_id": self.machine_id,
                "activated_date": datetime.now().isoformat(),
                "app_version": "1.0.0",
                "license_type": "activated_universal"
            }
            
            # Save the activated license
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(activated_license, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Activate license with the provided key.
        Returns (success, message)
        """
        # Validate license key format
        if len(license_key) != 16 or not license_key.replace("-", "").isalnum():
            return False, "Invalid license key format. Please enter a 16-character license key."
        
        # Clean license key (remove dashes if present)
        clean_key = license_key.replace("-", "").upper()
        
        # Validate license key against current machine
        if not validate_license_key(clean_key, self.machine_id):
            return False, "Invalid license key for this machine. Please contact support."
        
        try:
            # Save license data
            license_data = {
                "license_key": clean_key,
                "machine_id": self.machine_id,
                "activated_date": platform.system(),  # Simple timestamp
                "app_version": "1.0.0"
            }
            
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2)
            
            return True, "License activated successfully!"
            
        except Exception as e:
            return False, f"Failed to save license: {str(e)}"
    
    def get_machine_id(self) -> str:
        """Get the current machine ID for license generation."""
        return self.machine_id
    
    def deactivate_license(self) -> bool:
        """
        Deactivate license (remove license file).
        Useful for transferring license to another machine.
        """
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            return True
        except Exception:
            return False
    
    def get_license_info(self) -> Optional[dict]:
        """
        Get current license information.
        """
        if not os.path.exists(self.license_file):
            return None
        
        try:
            with open(self.license_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None