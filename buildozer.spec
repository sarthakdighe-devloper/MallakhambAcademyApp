[app]

title = Mallakhamb Academy
package.name = mallakhambapp
package.domain = org.sarthakdighe

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,db,json

version = 1.0

requirements = python3,kivy==2.3.0,pillow

orientation = portrait

fullscreen = 0

android.api = 34
android.minapi = 21
android.ndk_api = 21

android.archs = arm64-v8a

android.permissions = INTERNET

android.enable_androidx = True

android.allow_backup = True

source.exclude_dirs = venv,.git,__pycache__,build,bin
source.exclude_patterns = *.pyc,*.pyo

[buildozer]

log_level = 2
warn_on_root = 1
