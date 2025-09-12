#!/usr/bin/env bash
set -euo pipefail

# Reset app JSONs before each build
echo "Resetting notes.json and settings.json to defaults"
echo "[]" > notes.json
echo "{\"show_welcome\": true}" > settings.json

# Detect package manager and ensure JDK 17 and basic tools
if command -v pacman >/dev/null 2>&1; then
  sudo pacman -Sy --noconfirm jdk17-openjdk unzip zip rsync || true
  sudo archlinux-java set java-17-openjdk || true
  export JAVA_HOME="/usr/lib/jvm/java-17-openjdk"
elif command -v apt >/dev/null 2>&1; then
  sudo apt update -y
  sudo apt install -y openjdk-17-jdk unzip zip rsync
  export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
fi
export PATH="$JAVA_HOME/bin:$PATH"

# Python venv
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip -q install --upgrade pip
python -m pip -q install buildozer==1.5.0 python-for-android==2024.1.21 cython==3.0.10

# Ensure NDK r25b via buildozer-managed paths
export ANDROIDSDK="$HOME/.buildozer/android/platform/android-sdk"
export ANDROIDNDK="$HOME/.buildozer/android/platform/android-ndk-r25b"

# Enforce NDK 25b in spec
if [ -f buildozer.spec ]; then
  sed -i "s/^android\.ndk\s*=.*/android.ndk = 25b/" buildozer.spec || true
fi

# Clean and build
yes y | buildozer appclean || true
yes y | buildozer android clean || true
buildozer android debug -v | tee build_log.txt

# Show resulting APK(s)
ls -1 bin/*.apk 2>/dev/null || true
