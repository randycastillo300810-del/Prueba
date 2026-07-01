[app]
title = Prediccion Desercion
package.name = desercionapp
package.domain = org.desercion
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xlsx
version = 1.0
requirements = python3,kivy,openpyxl,plyer
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.gradle_dependencies = 
android.arch = arm64-v8a
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0
[buildozer]
log_level = 2
warn_on_root = 1
