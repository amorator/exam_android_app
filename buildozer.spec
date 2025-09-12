[app]

# (str) Title of your application
title = Notes App

# (str) Package name
package.name = notesapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,plyer,pyjnius

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (list) Android specific
android.orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# WRITE_SETTINGS is special; it's declared here but must be granted by user in Settings
android.permissions = CAMERA,FLASHLIGHT,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WRITE_SETTINGS

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (str) Python version to use
android.python = 3.8
