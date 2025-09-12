from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "about"
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс экрана об авторе"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Заголовок
        title = Label(
            text='Об авторе',
            font_size='24sp',
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        main_layout.add_widget(title)
        
        # ScrollView для прокрутки содержимого
        scroll = ScrollView()
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=20
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Информация об авторе
        author_info = Label(
            text='Приложение "Notes App" разработано для сдачи экзамена.\n\n'
                 'Автор: @amorator\n'
                 'Группа: ИТС-12\n'
                 'Университет: ВГТУ\n'
                 'Год: 2025\n\n'
                 'Описание проекта:\n'
                 'Мобильное приложение для создания и управления заметками,\n'
                 'разработанное с использованием фреймворка Kivy и\n'
                 'собранное для Android с помощью Buildozer.\n\n'
                 'Функциональность:\n'
                 '• Создание, редактирование и удаление заметок\n'
                 '• Сортировка заметок по дате обновления\n'
                 '• Множественный выбор заметок для удаления\n'
                 '• Закрепление заметок\n'
                 '• Управление фонариком (Android)\n'
                 '• Настройка отображения стартового окна\n'
                 '• Адаптивный интерфейс для мобильных устройств\n\n'
                 'Технологии:\n'
                 '• Python 3.x\n'
                 '• Kivy 2.1.0\n'
                 '• Plyer (для доступа к функциям Android)\n'
                 '• Buildozer (для сборки APK)\n'
                 '• JSON (для хранения данных)\n\n'
                 'Особенности реализации:\n'
                 '• Архитектура MVC с разделением на экраны\n'
                 '• Локальное хранение данных в JSON файлах\n'
                 '• Обработка длинных нажатий для выбора элементов\n'
                 '• Адаптивный дизайн для различных размеров экранов\n'
                 '• Обработка ошибок и пользовательские уведомления\n\n'
                 'Приложение готово к сборке для Android и может быть\n'
                 'установлено на мобильные устройства через APK файл.',
            font_size='14sp',
            halign='left',
            valign='top',
            text_size=(None, None),
            size_hint_y=None,
            height=dp(2000)  # Фиксированная высота для отображения всего текста
        )
        author_info.bind(size=author_info.setter('text_size'))
        content_layout.add_widget(author_info)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        # Кнопка "Назад"
        back_btn = Button(
            text='Назад к заметкам',
            size_hint_y=None,
            height=dp(60),
            font_size='18sp',
            background_color=(0.3, 0.6, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)

    def on_pre_enter(self, *args):
        # Перехватить кнопку Назад (Android): вернуться на главный
        try:
            from kivy.base import EventLoop
            win = EventLoop.window
            if win:
                win.bind(on_keyboard=self._on_back)
        except Exception:
            pass

    def on_leave(self, *args):
        try:
            from kivy.base import EventLoop
            win = EventLoop.window
            if win:
                win.unbind(on_keyboard=self._on_back)
        except Exception:
            pass
    
    def go_back(self, instance):
        """Возвращается к главному экрану"""
        self.manager.current = 'main'

    def _on_back(self, window, key, *args):
        if key == 27:  # Android back
            self.manager.current = 'main'
            return True
        return False
