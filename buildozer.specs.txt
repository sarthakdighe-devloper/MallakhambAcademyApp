[app]
title = Mallakhamb Academy
package.name = mallakhambapp
package.domain = org.sarthakdighe
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Crucial mobile requirements 
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pillow,openpyxl,reportlab,jnius

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Request system permissions for storage export
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1