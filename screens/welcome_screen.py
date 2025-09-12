from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp


class WelcomeScreen(Screen):
    name = 'welcome'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation='vertical', padding=[16, 24], spacing=16)

        # Верхний отступ
        root.add_widget(Widget(size_hint_y=0.3))

        title = Label(text='Добро пожаловать!', font_size='22sp', size_hint_y=None, height=40)
        root.add_widget(title)

        desc = Label(text='Это приложение заметок. Вы можете добавлять, закреплять и удалять заметки.',
                     halign='center', valign='middle', size_hint_y=None)
        desc.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        desc.height = dp(90)
        root.add_widget(desc)

        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56), spacing=14, padding=[8,0])
        self.cb = CheckBox(size_hint=(None, None), size=(dp(28), dp(28)))
        row.add_widget(self.cb)
        label = Label(text='Больше не показывать', valign='middle', size_hint_y=None, height=dp(28))
        row.add_widget(label)
        # Увеличиваем зону нажатия: тап по всей строке переключает чекбокс
        def _toggle_cb(*_):
            self.cb.active = not self.cb.active
        row.bind(on_touch_down=lambda w, t: (_toggle_cb() or True) if w.collide_point(*t.pos) else False)
        root.add_widget(row)

        # Buttons
        btn = Button(text='Продолжить', size_hint_y=None, height=dp(56))
        btn.bind(on_release=self.on_continue)
        root.add_widget(btn)

        # Нижний отступ
        root.add_widget(Widget(size_hint_y=0.4))

        self.add_widget(root)

    def on_continue(self, *_):
        if hasattr(self, 'app') and self.app:
            # Сохраняем инвертированно: чекбокс "не показывать" => show_welcome = False
            self.app.data_manager.set_show_welcome(not self.cb.active)
            self.app.sm.current = 'main'


