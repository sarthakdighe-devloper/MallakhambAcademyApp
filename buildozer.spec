[app]

title = Mallakhamb Academy
package.name = mallakhambapp
package.domain = org.sarthakdighe

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,db

version = 1.0

requirements = python3,kivy,pillow

orientation = portrait

fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk_api = 21

android.archs = arm64-v8a

android.enable_androidx = True

android.permissions = INTERNET

[buildozer]

log_level = 2
warn_on_root = 1
