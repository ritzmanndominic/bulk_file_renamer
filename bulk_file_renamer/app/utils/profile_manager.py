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

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class ProfileManager:
    """Manages save/load of rename profiles."""
    
    def __init__(self, profiles_dir: str = None):
        if profiles_dir is None:
            # Use user's AppData directory for profiles
            import sys
            if sys.platform == "win32":
                appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
                self.profiles_dir = os.path.join(appdata, 'BulkFileRenamer', 'profiles')
            else:
                # For macOS/Linux, use user's home directory
                self.profiles_dir = os.path.join(os.path.expanduser('~'), '.bulk_file_renamer', 'profiles')
        else:
            self.profiles_dir = profiles_dir
        self._ensure_profiles_dir()
    
    def _ensure_profiles_dir(self):
        """Ensure the profiles directory exists."""
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
    
    def get_profile_path(self, profile_name: str) -> str:
        """Get the full path for a profile file."""
        return os.path.join(self.profiles_dir, f"{profile_name}.json")
    
    def save_profile(self, profile_name: str, profile_data: Dict) -> bool:
        """Save a profile to disk."""
        try:
            profile_path = self.get_profile_path(profile_name)
            
            # Add metadata
            profile_data["_metadata"] = {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving profile {profile_name}: {e}")
            return False
    
    def load_profile(self, profile_name: str) -> Optional[Dict]:
        """Load a profile from disk."""
        try:
            profile_path = self.get_profile_path(profile_name)
            
            if not os.path.exists(profile_path):
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            return profile_data
        except Exception as e:
            print(f"Error loading profile {profile_name}: {e}")
            return None
    
    def list_profiles(self) -> List[str]:
        """List all available profiles."""
        try:
            if not os.path.exists(self.profiles_dir):
                return []
            
            profiles = []
            for filename in os.listdir(self.profiles_dir):
                if filename.endswith('.json'):
                    profile_name = filename[:-5]  # Remove .json extension
                    profiles.append(profile_name)
            
            return sorted(profiles)
        except Exception as e:
            print(f"Error listing profiles: {e}")
            return []
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile from disk."""
        try:
            profile_path = self.get_profile_path(profile_name)
            
            if os.path.exists(profile_path):
                os.remove(profile_path)
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting profile {profile_name}: {e}")
            return False
    
    def profile_exists(self, profile_name: str) -> bool:
        """Check if a profile exists."""
        profile_path = self.get_profile_path(profile_name)
        return os.path.exists(profile_path)
