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

import os
import sys
import json
from typing import Dict, Any, Optional


def _resolve_languages_dir(default_dir: str = "languages") -> str:
    """Resolve the absolute path to the languages directory in both dev and packaged builds.

    Search order:
    1) PyInstaller runtime directory (sys._MEIPASS)/languages
    2) Directory of the executable (sys.executable)/languages
    3) Directory of this file (source checkout)/../../languages
    4) Current working directory /languages
    If none exist, return the provided default_dir (absolute from CWD) so the app can still run.
    """
    candidates = []

    # 1) PyInstaller temporary extraction folder
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(os.path.join(meipass, default_dir))

    # 2) Next to the executable when frozen
    exe_dir = os.path.dirname(getattr(sys, "executable", sys.argv[0]))
    if exe_dir:
        candidates.append(os.path.join(exe_dir, default_dir))

    # 3) In the repository relative to this source file
    here = os.path.dirname(os.path.abspath(__file__))
    repo_candidate = os.path.abspath(os.path.join(here, "..", "..", default_dir))
    candidates.append(repo_candidate)

    # 4) CWD fallback
    candidates.append(os.path.abspath(default_dir))

    for path in candidates:
        if os.path.isdir(path):
            return path

    # Fallback: return the first candidate even if it does not exist
    return os.path.abspath(default_dir)


class TranslationManager:
    """Manages translations and language switching for the application."""
    
    def __init__(self, languages_dir: str = "languages"):
        # Resolve languages directory for both dev and packaged builds
        self.languages_dir = _resolve_languages_dir(languages_dir)
        self.current_language = "en"  # Default to English
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_languages = self._discover_languages()
        self._load_translations()
    
    def _discover_languages(self) -> Dict[str, str]:
        """Discover available language files."""
        languages = {}
        if not os.path.exists(self.languages_dir):
            return languages
        
        for filename in os.listdir(self.languages_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # Remove .json extension
                # Try to get language name from the translation file
                try:
                    with open(os.path.join(self.languages_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        lang_name = data.get('settings', {}).get('advanced', {}).get('languages', {}).get(lang_code, lang_code.upper())
                        languages[lang_code] = lang_name
                except Exception:
                    languages[lang_code] = lang_code.upper()
        
        return languages
    
    def _load_translations(self):
        """Load all available translations."""
        for lang_code in self.available_languages:
            self._load_language(lang_code)
    
    def _load_language(self, lang_code: str):
        """Load translations for a specific language."""
        lang_file = os.path.join(self.languages_dir, f"{lang_code}.json")
        if os.path.exists(lang_file):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading language file {lang_file}: {e}")
                self.translations[lang_code] = {}
    
    def set_language(self, lang_code: str) -> bool:
        """Set the current language."""
        if lang_code in self.available_languages:
            self.current_language = lang_code
            return True
        return False
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages as {code: name} dictionary."""
        return self.available_languages.copy()
    
    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language.
        
        Args:
            key: Translation key in dot notation (e.g., 'app.title', 'main.browse_folder')
            **kwargs: Format parameters for string formatting
        
        Returns:
            Translated string or the key if translation not found
        """
        try:
            # Navigate through nested dictionary using dot notation
            keys = key.split('.')
            value = self.translations.get(self.current_language, {})
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # Fallback to English if current language doesn't have the key
                    if self.current_language != "en":
                        value = self.translations.get("en", {})
                        for k in keys:
                            if isinstance(value, dict) and k in value:
                                value = value[k]
                            else:
                                return key  # Return key if not found in English either
                    else:
                        return key  # Return key if not found
            
            # Format the string if kwargs are provided
            if kwargs and isinstance(value, str):
                try:
                    return value.format(**kwargs)
                except (KeyError, ValueError):
                    return value
            
            return str(value) if value is not None else key
            
        except Exception as e:
            print(f"Translation error for key '{key}': {e}")
            return key
    
    def tr(self, key: str, **kwargs) -> str:
        """Short alias for translate method."""
        return self.translate(key, **kwargs)
    
    def get_menu_text(self, menu_key: str) -> str:
        """Get menu text with proper ampersand handling."""
        text = self.tr(f"app.menu.{menu_key}")
        return text
    
    def get_dialog_text(self, dialog_type: str, field: str, **kwargs) -> str:
        """Get dialog text."""
        return self.translate(f"dialogs.{dialog_type}.{field}", **kwargs)
    
    def get_notification_text(self, notification_type: str, **kwargs) -> str:
        """Get notification text."""
        return self.translate(f"notifications.{notification_type}", **kwargs)
    
    def get_status_text(self, status: str) -> str:
        """Get status text."""
        return self.translate(f"status.{status}")
    
    def get_error_text(self, error_type: str, **kwargs) -> str:
        """Get error text."""
        return self.translate(f"errors.{error_type}", **kwargs)


# Global translation manager instance
_translation_manager = None


def get_translation_manager() -> TranslationManager:
    """Get the global translation manager instance."""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def tr(key: str, **kwargs) -> str:
    """Global translation function."""
    return get_translation_manager().translate(key, **kwargs)


def set_language(lang_code: str) -> bool:
    """Set the global language."""
    return get_translation_manager().set_language(lang_code)


def get_current_language() -> str:
    """Get the current language code."""
    return get_translation_manager().get_language()


def get_available_languages() -> Dict[str, str]:
    """Get available languages."""
    return get_translation_manager().get_available_languages()
