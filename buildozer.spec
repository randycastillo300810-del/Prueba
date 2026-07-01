[app]
title = Prediccion Desercion
package.name = desercionapp
package.domain = org.desercion
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xlsx
version = 1.0
requirements = python3,kivy,openpyxl,plyer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.ndk = 25c
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
