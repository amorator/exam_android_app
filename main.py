#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from kivy.logger import Logger

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Доп. совместимость не требуется

try:
    from app import NotesApp
    
    if __name__ == '__main__':
        Logger.info("NotesApp: Starting application...")
        try:
            app = NotesApp()
            app.run()
        except Exception as e:
            Logger.error(f"NotesApp: Runtime error - {e}")
            print(f"Ошибка выполнения: {e}")
            sys.exit(1)
        
except ImportError as e:
    Logger.error(f"NotesApp: Import error - {e}")
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что установлены все необходимые зависимости:")
    print("pip install -r requirements.txt")
    
except Exception as e:
    Logger.error(f"NotesApp: Unexpected error - {e}")
    print(f"Неожиданная ошибка: {e}")
    sys.exit(1)
