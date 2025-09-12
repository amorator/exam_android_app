# Инструкция сборки Android APK

## Требования
- **Python 3.8+**
- **Java JDK 17** (OpenJDK 17)
- **Buildozer 1.5.0** и **python-for-android 2024.1.21**
- **Android SDK/NDK** (управляются Buildozer автоматически)

## Подготовка окружения

### Arch Linux
```bash
sudo pacman -Sy --noconfirm jdk17-openjdk git python-pip unzip zip rsync
sudo archlinux-java set java-17-openjdk
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk"
```

### WSL/Ubuntu
```bash
sudo apt update
sudo apt install -y openjdk-17-jdk git python3-venv python3-pip unzip zip rsync
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
```

## Автоматическая сборка

Используйте готовый скрипт:
```bash
./build_android.sh
```

Скрипт автоматически:
- Устанавливает JDK 17 и необходимые инструменты
- Создает Python виртуальное окружение
- Устанавливает Buildozer 1.5.0 и python-for-android 2024.1.21
- Настраивает Android SDK/NDK пути
- Очищает кэш сборки
- Собирает APK с подробным выводом

## Ручная сборка

1. **Настройка окружения:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install buildozer==1.5.0 python-for-android==2024.1.21 cython==3.0.10
```

2. **Настройка путей Android:**
```bash
export ANDROIDSDK="$HOME/.buildozer/android/platform/android-sdk"
export ANDROIDNDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
```

3. **Сборка:**
```bash
buildozer android clean
buildozer android debug -v
```

## Решение проблем

### Ошибка NDK версии
- **Проблема:** NDK r23b не поддерживается
- **Решение:** Используется NDK r25b (автоматически в buildozer.spec)

### Ошибка Gradle "Unsupported class file major version 68"
- **Проблема:** Несовместимость версий Java
- **Решение:** Используется JDK 17

### Ошибка `undeclared name not builtin: long`
- **Проблема:** Cython/Python версии
- **Решение:** Используется Python 3.8+ и актуальные версии библиотек

### Ошибка `JNIUS_PYTHON3 not defined`
- **Проблема:** Pyjnius конфигурация
- **Решение:** Используется актуальная версия python-for-android

## Результат сборки

APK файлы создаются в папке `bin/`:
- `notesapp-0.1-arm64-v8a-debug.apk` - для ARM64 устройств
- `notesapp-0.1-armeabi-v7a-debug.apk` - для ARM32 устройств

## Установка на устройство

```bash
# Через ADB
adb install bin/notesapp-0.1-arm64-v8a-debug.apk

# Или скопируйте APK на устройство и установите вручную
```

## Сброс настроек приложения

```bash
./build_android.sh --reset
```

Удаляет и пересоздает файлы настроек:
- `notes.json` - заметки
- `settings.json` - настройки приложения

## Технические детали

### Конфигурация buildozer.spec
- **android.ndk = 25b** - версия NDK
- **android.api = 30** - целевая Android API
- **android.minapi = 21** - минимальная Android API
- **android.python = 3.8** - версия Python
- **android.arch = arm64-v8a** - архитектура по умолчанию

### Разрешения Android
- **CAMERA** - доступ к фонарику
- **FLASHLIGHT** - управление фонариком
- **WRITE_EXTERNAL_STORAGE** - сохранение данных
- **READ_EXTERNAL_STORAGE** - чтение данных
- **WRITE_SETTINGS** - изменение системных настроек (для яркости)

### Особенности Android
- **Портретная ориентация** - принудительно установлена
- **App-level яркость** - не требует системных разрешений
- **Системная яркость** - требует WRITE_SETTINGS (открывается системный экран)
- **Фонарик** - работает через Plyer и CameraManager