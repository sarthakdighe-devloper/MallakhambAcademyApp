[app]

# Application
title = Mallakhamb Academy
package.name = mallakhambapp
package.domain = org.sarthakdighe

# Source
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,db,json

# Version
version = 1.0

# Requirements
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Android
android.api = 34
android.minapi = 21
android.ndk_api = 21

# Architectures
android.archs = arm64-v8a

# Permissions
android.permissions = INTERNET

# Backup
android.allow_backup = True

# AndroidX
android.enable_androidx = True

# Presplash (optional)
# presplash.filename = assets/presplash.png

# Icon (optional)
# icon.filename = assets/icon.png

# Exclude unnecessary files
source.exclude_dirs = venv,.git,__pycache__,build,bin
source.exclude_patterns = *.pyc,*.pyo,*.log

[buildozer]

log_level = 2
warn_on_root = 1
