[app]
title = GlobalExchange
package.name = globalexchange
package.domain = org.sakil
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# requirements এ সব লাইব্রেরি দেওয়া আছে
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,urllib3,certifi,idna,charset-normalizer

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1