from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp


class EditScreen(Screen):
    """Экран редактирования/создания заметки."""
    name = 'edit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        self.title_input = TextInput(hint_text='Заголовок', size_hint_y=None, height=dp(44), multiline=False)
        self.title_input.bind(focus=self._on_title_focus)
        self.text_input = TextInput(hint_text='Текст заметки', multiline=True)
        row = BoxLayout(size_hint_y=None, height=dp(56), spacing=12, padding=[0,4])
        row.add_widget(Widget(size_hint_x=1))
        ok_btn = Button(text='ОК', size_hint_x=None, width=dp(120))
        cancel_btn = Button(text='Отмена', size_hint_x=None, width=dp(120))
        ok_btn.bind(on_release=self.on_ok)
        cancel_btn.bind(on_release=self.on_cancel)
        row.add_widget(ok_btn)
        row.add_widget(cancel_btn)
        row.add_widget(Widget(size_hint_x=1))
        layout.add_widget(self.title_input)
        layout.add_widget(self.text_input)
        layout.add_widget(row)
        self.add_widget(layout)

    def on_pre_enter(self, *args):
        # Кнопка Назад действует как Отмена (с подтверждением при изменениях)
        try:
            from kivy.base import EventLoop
            win = EventLoop.window
            if win:
                win.bind(on_keyboard=self._on_back)
        except Exception:
            pass
        note = getattr(self, 'note', None)
        if note:
            self.title_input.text = note.get('title', '')
            self.text_input.text = note.get('content', '')
        else:
            self.title_input.text = ''
            self.text_input.text = ''
        # Снимем флаг изменений
        self._initial_title = self.title_input.text
        self._initial_text = self.text_input.text

    def on_leave(self, *args):
        try:
            from kivy.base import EventLoop
            win = EventLoop.window
            if win:
                win.unbind(on_keyboard=self._on_back)
        except Exception:
            pass

    def on_ok(self, *_):
        if hasattr(self, 'app') and self.app:
            # Если редактируем существующую
            if getattr(self, 'note', None) and self.note.get('id') is not None:
                self.app.data_manager.update_note(self.note['id'], self.title_input.text, self.text_input.text)
            else:
                self.app.data_manager.add_note(self.title_input.text, self.text_input.text)
            # Обновляем список и возвращаемся на главный экран
            self.app.main_screen.refresh_notes()
            self.app.sm.current = 'main'

    def on_cancel(self, *_):
        if hasattr(self, 'app') and self.app:
            if self._has_changes():
                self._confirm_discard()
            else:
                self.app.sm.current = 'main'

    # API для MainScreen
    def set_note(self, note):
        self.note = note

    def _on_back(self, window, key, *args):
        if key == 27:  # Android back
            if self._has_changes():
                self._confirm_discard()
            else:
                self.on_cancel()
            return True
        return False

    def _has_changes(self) -> bool:
        return (self.title_input.text != getattr(self, '_initial_title', '') or
                self.text_input.text != getattr(self, '_initial_text', ''))

    def _confirm_discard(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.popup import Popup
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Отменить изменения?', font_size='16sp', size_hint_y=None, height=dp(40)))
        row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(48))
        no_btn = Button(text='Нет')
        yes_btn = Button(text='Да')
        row.add_widget(no_btn)
        row.add_widget(yes_btn)
        content.add_widget(row)
        popup = Popup(title='Подтверждение', content=content, size_hint=(0.8, 0.35))
        def close_no(*_):
            popup.dismiss()
        def close_yes(*_):
            popup.dismiss()
            if hasattr(self, 'app') and self.app:
                self.app.sm.current = 'main'
        no_btn.bind(on_release=close_no)
        yes_btn.bind(on_release=close_yes)
        popup.open()

    def _on_title_focus(self, instance, focused):
        # Если редактируем заметку, у которой заголовок был "Без заголовка",
        # и пользователь начал ввод — очищаем поле для удобства
        if focused and instance.text.strip() == 'Без заголовка':
            instance.text = ''