from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.text import Label as CoreLabel
from kivy.utils import platform as kivy_platform

from utils.data_manager import DataManager
from utils.android_utils import AndroidUtils
from screens.welcome_screen import WelcomeScreen
from screens.main_screen import MainScreen
from screens.edit_screen import EditScreen
from screens.about_screen import AboutScreen

class NotesApp(App):
    """Основное приложение Kivy для заметок с поддержкой Android-функций."""
    def build(self):
        """Создает и настраивает интерфейс приложения."""
        try:
            # Инициализируем менеджер данных (заметки, настройки)
            self.data_manager = DataManager()
        except Exception as e:
            Logger.error(f"NotesApp: DataManager initialization error: {e}")
            self.data_manager = None
        
        try:
            # Инициализируем Android утилиты (фонарик, яркость)
            self.android_utils = AndroidUtils()
        except Exception as e:
            Logger.error(f"NotesApp: AndroidUtils initialization error: {e}")
            self.android_utils = None
        
        # Создаем менеджер экранов
        self.sm = ScreenManager()
        
        # Создаем экраны
        self.welcome_screen = WelcomeScreen()
        self.main_screen = MainScreen()
        self.edit_screen = EditScreen()
        self.about_screen = AboutScreen()
        
        # Добавляем экраны в менеджер
        self.sm.add_widget(self.welcome_screen)
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.edit_screen)
        self.sm.add_widget(self.about_screen)
        
        # Устанавливаем ссылки на приложение для экранов
        self.welcome_screen.app = self
        self.main_screen.app = self
        self.edit_screen.app = self
        self.about_screen.app = self
        
        # Определяем стартовый экран
        try:
            if self.data_manager and self.data_manager.should_show_welcome():
                self.sm.current = 'welcome'
            else:
                self.sm.current = 'main'
        except Exception as e:
            Logger.error(f"NotesApp: Screen selection error: {e}")
            self.sm.current = 'main'
        
        Logger.info("NotesApp: Application initialized successfully")
        return self.sm
    
    def on_start(self):
        """Вызывается при запуске приложения."""
        Logger.info("NotesApp: Application started")
        # Обработчик кнопки Назад на Android: всегда возвращать на 'main'
        try:
            from kivy.base import EventLoop
            win = EventLoop.window
            if win and kivy_platform == 'android':
                win.bind(on_keyboard=self._on_back_button)
        except Exception as e:
            Logger.warning(f"NotesApp: Cannot bind back button: {e}")
    
    def on_pause(self):
        """Вызывается при приостановке приложения."""
        Logger.info("NotesApp: Application paused")
        # Выключаем фонарик и возвращаем яркость при приостановке
        self.cleanup_on_exit()
        return True
    
    def on_resume(self):
        """Вызывается при возобновлении приложения."""
        Logger.info("NotesApp: Application resumed")
    
    def on_stop(self):
        """Вызывается при остановке приложения."""
        Logger.info("NotesApp: Application stopped")
        # Выключаем фонарик и возвращаем яркость при остановке
        self.cleanup_on_exit()

    def _on_back_button(self, window, key, *args):
        # key == 27 соответствует Android back
        if key == 27:
            try:
                # если не на главном экране — вернуться на главный
                if self.sm.current != 'main':
                    self.sm.current = 'main'
                    return True  # обработано
                # на главном — закрыть приложение полностью
                try:
                    self.stop()
                except Exception as e:
                    Logger.error(f"NotesApp: Error stopping app: {e}")
                # Дополнительно попросим Android закрыть Activity
                try:
                    if kivy_platform == 'android':
                        from jnius import autoclass
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        PythonActivity.mActivity.finish()
                except Exception as e:
                    Logger.error(f"NotesApp: Error finishing activity: {e}")
                return True
            except Exception as e:
                Logger.error(f"NotesApp: Error in back button handler: {e}")
                return False
        return False
    
    def cleanup_on_exit(self):
        """Гарантированно выключает фонарик и возвращает яркость при выходе."""
        try:
            # Выключаем фонарик
            if hasattr(self.main_screen, 'flashlight_on') and self.main_screen.flashlight_on:
                self.android_utils.turn_off_flashlight()
                Logger.info("NotesApp: Flashlight turned off on exit")
            
            # Возвращаем оригинальную яркость
            if hasattr(self.main_screen, 'brightness_on') and self.main_screen.brightness_on:
                original_brightness = getattr(self.main_screen, 'original_brightness', 0.5)
                self.android_utils.set_brightness(original_brightness)
                Logger.info(f"NotesApp: Brightness restored to {original_brightness} on exit")
        except Exception as e:
            Logger.error(f"NotesApp: Error during cleanup: {e}")
    
    def _setup_font(self):
        """Настраивает шрифт для лучшей поддержки символов"""
        # Без кастомного шрифта по умолчанию, чтобы избежать падений на десктопе
        return
