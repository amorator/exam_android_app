"""
Утилиты для отладки и показа ошибок в GUI.
"""

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

# Глобальная переменная для отслеживания открытых попапов
_popup_open = False


def show_error_popup(title: str, message: str, parent=None):
    """Показывает всплывающее окно с ошибкой и полным текстом ошибки."""
    global _popup_open
    try:
        _popup_open = True
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        # Текст ошибки
        error_label = Label(
            text=message,
            text_size=(dp(450), None),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(200),
            font_size='12sp',
            color=(1, 1, 1, 1)
        )
        error_label.bind(size=error_label.setter('text_size'))
        content.add_widget(error_label)
        
        # Кнопка закрытия
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=dp(50),
            font_size='16sp'
        )
        content.add_widget(btn)
        
        # Создаем и показываем попап
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.95, 0.7),
            auto_dismiss=False,
            title_size='18sp'
        )
        
        def close_popup(instance):
            global _popup_open
            _popup_open = False
            popup.dismiss()
            return True  # Останавливаем всплытие события
        
        btn.bind(on_press=close_popup)
        popup.open()
        
    except Exception as e:
        _popup_open = False
        # Если не можем показать GUI, хотя бы в лог
        from kivy.logger import Logger
        Logger.error(f"DebugUtils: Cannot show error popup: {e}")


def show_debug_info(title: str, message: str, parent=None):
    """Показывает отладочную информацию в GUI попапе."""
    global _popup_open
    try:
        _popup_open = True
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        # Текст отладки
        debug_label = Label(
            text=message,
            text_size=(dp(400), None),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(120),
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        debug_label.bind(size=debug_label.setter('text_size'))
        content.add_widget(debug_label)
        
        # Кнопка закрытия
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=dp(50),
            font_size='16sp'
        )
        content.add_widget(btn)
        
        # Создаем и показываем попап
        popup = Popup(
            title=f"Отладка: {title}",
            content=content,
            size_hint=(0.9, 0.5),
            auto_dismiss=False,
            title_size='18sp'
        )
        
        def close_popup(instance):
            global _popup_open
            _popup_open = False
            popup.dismiss()
            return True  # Останавливаем всплытие события
        
        btn.bind(on_press=close_popup)
        popup.open()
        
    except Exception as e:
        _popup_open = False
        from kivy.logger import Logger
        Logger.error(f"DebugUtils: Cannot show debug info: {e}")


def show_success_message(message: str, parent=None):
    """Показывает сообщение об успехе в GUI попапе."""
    global _popup_open
    try:
        _popup_open = True
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        success_label = Label(
            text=message,
            text_size=(dp(250), None),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(60)
        )
        success_label.bind(size=success_label.setter('text_size'))
        content.add_widget(success_label)
        
        btn = Button(
            text='OK',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title='Успех',
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=False
        )
        
        def close_popup(instance):
            global _popup_open
            _popup_open = False
            popup.dismiss()
            return True  # Останавливаем всплытие события
        
        btn.bind(on_press=close_popup)
        popup.open()
        
    except Exception as e:
        _popup_open = False
        from kivy.logger import Logger
        Logger.error(f"DebugUtils: Cannot show success message: {e}")


def is_popup_open():
    """Возвращает True, если открыт какой-либо попап (для предотвращения обработки touch событий)."""
    global _popup_open
    return _popup_open
