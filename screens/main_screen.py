from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from datetime import datetime

class MainScreen(Screen):
    """Главный экран со списком заметок и верхней панелью.

    Упрощено: без эмодзи, явные тексты кнопок, отдельная панель
    для режима выделения, фиксированный держатель панели.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        self.selected_notes = set()
        self.is_selection_mode = False
        self.flashlight_on = False
        self.brightness_on = False
        self.original_brightness = None
        self.long_press_clock = None
        self.long_press_duration = 0.5  # Длительность длинного нажатия в секундах
        self.setup_ui()
    
    
    def setup_ui(self):
        """Настраивает интерфейс главного экрана."""
        main_layout = BoxLayout(orientation='vertical')
        
        # Держатель для верхней панели, чтобы не прыгала по вертикали при замене
        self.toolbar_holder = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50))
        main_layout.add_widget(self.toolbar_holder)
        self.setup_top_panel(self.toolbar_holder)
        
        # Список заметок
        self.setup_notes_list(main_layout)
        
        self.add_widget(main_layout)
    
    def setup_top_panel(self, parent):
        """Создает верхнюю панель с кнопками управления."""
        self.top_panel = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[6, 6],
            spacing=6
        )
        
        # Кнопка добавления заметки (слева)
        self.add_btn = Button(
            text='Добавить',
            size_hint_x=None,
            width=dp(88),
            font_size='13sp'
        )
        self.add_btn.bind(on_press=self.add_note)
        self.top_panel.add_widget(self.add_btn)
        
        # Невидимый виджет для центрирования
        left_spacer = Widget(size_hint_x=1)
        self.top_panel.add_widget(left_spacer)
        
        # Кнопка яркости (в центре)
        self.brightness_btn = Button(
            text='Яркость',
            size_hint_x=None,
            width=dp(84),
            font_size='12sp'
        )
        self.brightness_btn.bind(on_press=self.toggle_brightness)
        self.top_panel.add_widget(self.brightness_btn)
        
        # Кнопка фонарика (в центре)
        self.flashlight_btn = Button(
            text='Фонарик',
            size_hint_x=None,
            width=dp(84),
            font_size='12sp'
        )
        self.flashlight_btn.bind(on_press=self.toggle_flashlight)
        self.top_panel.add_widget(self.flashlight_btn)
        
        # Невидимый виджет для центрирования
        right_spacer = Widget(size_hint_x=1)
        self.top_panel.add_widget(right_spacer)
        
        # Кнопка об авторе (в правом углу)
        self.about_btn = Button(
            text='Об авторе',
            size_hint_x=None,
            width=dp(88),
            font_size='12sp'
        )
        self.about_btn.bind(on_press=self.show_about)
        self.top_panel.add_widget(self.about_btn)
        
        # Панель режима выделения (отдельная)
        self.selection_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[6,6], spacing=6)

        self.delete_btn = Button(
            text='Удалить',
            size_hint_x=None,
            width=dp(74),
            font_size='12sp',
            background_color=(1, 0.3, 0.3, 1),
        )
        self.delete_btn.bind(on_press=self.delete_selected_notes)
        self.selection_panel.add_widget(self.delete_btn)
        
        # Кнопка закрепления (скрыта по умолчанию)
        self.pin_btn = Button(
            text='Закрепить',
            size_hint_x=None,
            width=dp(74),
            font_size='12sp',
            background_color=(0.3, 0.6, 1, 1),
        )
        self.pin_btn.bind(on_press=self.toggle_pin_selected_notes)
        self.selection_panel.add_widget(self.pin_btn)
        
        # Кнопка отмены выбора (скрыта по умолчанию)
        self.cancel_selection_btn = Button(
            text='Отмена',
            size_hint_x=None,
            width=dp(74),
            font_size='12sp',
            background_color=(0.7, 0.7, 0.7, 1),
        )
        self.cancel_selection_btn.bind(on_press=self.cancel_selection)
        self.selection_panel.add_widget(self.cancel_selection_btn)

        # Вставляем в держатель
        parent.clear_widgets()
        parent.add_widget(self.top_panel)
    
    def setup_notes_list(self, parent):
        """Создает прокручиваемый список заметок."""
        # Контейнер для заметок
        notes_container = BoxLayout(orientation='vertical')
        
        # ScrollView для прокрутки заметок
        scroll = ScrollView()
        self.notes_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10),
            padding=[10, 5]
        )
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))
        
        scroll.add_widget(self.notes_layout)
        notes_container.add_widget(scroll)
        
        parent.add_widget(notes_container)
    
    def refresh_notes(self):
        """Заполняет список заметок из хранилища."""
        self.notes_layout.clear_widgets()
        
        if hasattr(self, 'app') and self.app:
            notes = self.app.data_manager.get_notes()
            
            if not notes:
                # Показываем сообщение, если заметок нет
                no_notes_label = Label(
                    text='Заметок пока нет.\nНажмите "Добавить" для создания первой заметки.',
                    font_size='18sp',
                    size_hint_y=None,
                    height=dp(100),
                    halign='center',
                    valign='middle'
                )
                no_notes_label.bind(size=no_notes_label.setter('text_size'))
                self.notes_layout.add_widget(no_notes_label)
            else:
                # Добавляем заметки в список
                for note in notes:
                    note_widget = self.create_note_widget(note)
                    self.notes_layout.add_widget(note_widget)
    
    def create_note_widget(self, note):
        """Создает карточку заметки."""
        # Определяем заголовок для отображения
        display_title = note['title']
        if not display_title or display_title == "Без заголовка":
            # Показываем первые 50 символов содержимого
            content_preview = note['content'][:50]
            if len(note['content']) > 50:
                content_preview += "..."
            display_title = content_preview or "Пустая заметка"
        
        # Создаем контейнер для заметки
        note_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            padding=[15, 10],
            spacing=15
        )
        
        # Добавляем фон для заметки
        from kivy.graphics import Color, RoundedRectangle
        with note_container.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Светло-серый фон
            note_container.rect = RoundedRectangle(
                pos=note_container.pos,
                size=note_container.size,
                radius=[10]
            )
        
        note_container.bind(pos=self.update_rect, size=self.update_rect)
        
        # Добавляем обработчики касаний
        note_container.bind(
            on_touch_down=lambda w, touch: self.on_note_touch_down(w, touch),
            on_touch_up=lambda w, touch: self.on_note_touch_up(w, touch)
        )
        
        # Чекбокс для выбора (скрыт по умолчанию)
        checkbox = CheckBox(
            size_hint_x=None,
            width=dp(40),
            opacity=0,
            disabled=True
        )
        checkbox.note_id = note['id']
        checkbox.bind(active=self.on_note_selected)
        note_container.add_widget(checkbox)
        
        # Сохраняем ссылку на checkbox в контейнере
        note_container.checkbox = checkbox
        note_container.note_id = note['id']
        
        # Основной контент заметки
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=1
        )
        
        # Заголовок с маркером закрепления
        title_text = display_title
        if note.get('pinned', False):
            title_text = f"[ЗАКРЕПЛЕНО] {display_title}"  # Текстовый маркер
        
        # Цвет текста в зависимости от статуса закрепления
        text_color = (0.1, 0.4, 0.8, 1) if note.get('pinned', False) else (0.2, 0.2, 0.2, 1)
        
        title_label = Label(
            text=title_text,
            font_size='18sp',
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle',
            text_size=(None, None),
            bold=True,
            color=text_color
        )
        title_label.bind(size=title_label.setter('text_size'))
        content_layout.add_widget(title_label)
        
        # Превью содержимого (если есть)
        if note['content']:
            content_preview = note['content'][:100]
            if len(note['content']) > 100:
                content_preview += "..."
            content_label = Label(
                text=content_preview,
                font_size='14sp',
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                text_size=(None, None),
                color=(0.4, 0.4, 0.4, 1)  # Более темный текст для лучшей читаемости
            )
            content_label.bind(size=content_label.setter('text_size'))
            content_layout.add_widget(content_label)
        
        # Дата создания
        created_date = datetime.fromisoformat(note['created_at']).strftime('%d.%m.%Y %H:%M')
        date_label = Label(
            text=created_date,
            font_size='12sp',
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle',
            color=(0.7, 0.7, 0.7, 1)
        )
        date_label.bind(size=date_label.setter('text_size'))
        content_layout.add_widget(date_label)
        
        note_container.add_widget(content_layout)
        
        # Сохраняем ссылки для управления
        note_container.checkbox = checkbox
        note_container.note_id = note['id']
        
        return note_container
    
    def _is_popup_open(self):
        """Проверяет, открыт ли какой-либо попап (ошибка/отладка)."""
        try:
            from utils.debug_utils import is_popup_open
            return is_popup_open()
        except Exception:
            return False
    
    def add_note(self, instance):
        """Открывает экран создания новой заметки."""
        # Передаем пустую заметку для создания новой ДО переключения экрана
        if hasattr(self, 'app') and self.app:
            self.app.edit_screen.set_note(None)
        self.manager.current = 'edit'
    
    def edit_note(self, instance):
        """Открывает редактор для существующей заметки."""
        note_id = instance.note_id
        if hasattr(self, 'app') and self.app:
            note = self.app.data_manager.get_note(note_id)
            if note:
                self.manager.current = 'edit'
                self.app.edit_screen.set_note(note)
    
    def show_about(self, instance):
        """Переходит на экран "Об авторе"."""
        self.manager.current = 'about'
    
    def toggle_flashlight(self, instance):
        """Переключает фонарик."""
        if hasattr(self, 'app') and self.app and self.app.android_utils:
            try:
                result = self.app.android_utils.toggle_flashlight()
                if result is not None:
                    self.flashlight_on = result
                    # Подсвечиваем кнопку вместо изменения текста
                    self.flashlight_btn.background_color = (0.3, 1, 0.3, 1) if self.flashlight_on else (0.7, 0.7, 0.7, 1)
            except Exception as e:
                from kivy.logger import Logger
                import traceback
                error_details = f"MainScreen flashlight error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
                Logger.error(f"MainScreen: Error toggling flashlight: {e}")
                from utils.debug_utils import show_error_popup
                show_error_popup("Ошибка фонарика", error_details)
    
    def toggle_brightness(self, instance):
        """Переключает яркость экрана (макс/предыдущее) без всплывающих уведомлений."""
        if not hasattr(self, 'app') or not self.app or not self.app.android_utils:
            from utils.debug_utils import show_debug_info
            show_debug_info("Яркость", "Android утилиты недоступны")
            return
            
        try:
            # Сохраняем оригинальную яркость при первом включении
            if not self.brightness_on and self.original_brightness is None:
                self.original_brightness = self.app.android_utils.get_brightness()
                if self.original_brightness is None:
                    self.original_brightness = 0.5  # Значение по умолчанию
            
            result = self.app.android_utils.toggle_brightness()
            if result is not None:
                self.brightness_on = result
                # Подсвечиваем кнопку
                self.brightness_btn.background_color = (1, 1, 0.3, 1) if self.brightness_on else (0.7, 0.7, 0.7, 1)
            else:
                # Тихий фейл без уведомлений
                pass
        except Exception as e:
            from kivy.logger import Logger
            import traceback
            error_details = f"MainScreen brightness error:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
            Logger.error(f"MainScreen: Error toggling brightness: {e}")
            from utils.debug_utils import show_error_popup
            show_error_popup("Ошибка яркости", error_details)
    
    def on_note_selected(self, checkbox, is_active):
        """Обрабатывает переключение чекбокса заметки."""
        note_id = checkbox.note_id
        
        if is_active:
            self.selected_notes.add(note_id)
        else:
            self.selected_notes.discard(note_id)
        
        # Переключаем режим выбора
        if self.selected_notes and not self.is_selection_mode:
            self.enter_selection_mode()
        elif not self.selected_notes and self.is_selection_mode:
            self.exit_selection_mode()
        
        # Обновляем текст кнопки закрепления
        if self.is_selection_mode:
            self.update_pin_button_text()
    
    def enter_selection_mode(self):
        """Входит в режим выбора заметок."""
        self.is_selection_mode = True
        # Заменяем верхнюю панель на панель выбора
        # Меняем содержимое держателя
        if hasattr(self, 'toolbar_holder') and self.toolbar_holder:
            self.toolbar_holder.clear_widgets()
            self.toolbar_holder.add_widget(self.selection_panel)

        # Показываем чекбоксы
        for child in self.notes_layout.children:
            if hasattr(child, 'checkbox'):
                child.checkbox.opacity = 1
                child.checkbox.disabled = False
    
    def exit_selection_mode(self):
        """Выходит из режима выбора заметок."""
        self.is_selection_mode = False
        self.selected_notes.clear()
        # Вернуть обычную панель
        if hasattr(self, 'toolbar_holder') and self.toolbar_holder:
            self.toolbar_holder.clear_widgets()
            self.toolbar_holder.add_widget(self.top_panel)

        # Скрываем чекбоксы и снимаем выделение
        for child in self.notes_layout.children:
            if hasattr(child, 'checkbox'):
                child.checkbox.opacity = 0
                child.checkbox.active = False
                child.checkbox.disabled = True
    
    def delete_selected_notes(self, instance):
        """Удаляет выбранные заметки с подтверждением."""
        if not self.selected_notes:
            return
        
        # Показываем диалог подтверждения
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(
            text=f'Удалить {len(self.selected_notes)} заметок?',
            font_size='16sp'
        ))
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        cancel_btn = Button(text='Отмена')
        confirm_btn = Button(text='Удалить', background_color=(1, 0.3, 0.3, 1))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Подтверждение удаления',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def confirm_delete(instance):
            if hasattr(self, 'app') and self.app:
                self.app.data_manager.delete_notes(list(self.selected_notes))
                self.exit_selection_mode()
                self.refresh_notes()
            popup.dismiss()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=cancel_delete)
        
        popup.open()
    
    def toggle_pin_selected_notes(self, instance):
        """Переключает закрепление выбранных заметок."""
        if not self.selected_notes:
            return
        
        if hasattr(self, 'app') and self.app:
            # Определяем, что делать с заметками
            pinned_count = 0
            unpinned_count = 0
            
            for note_id in self.selected_notes:
                if self.app.data_manager.is_note_pinned(note_id):
                    pinned_count += 1
                else:
                    unpinned_count += 1
            
            # Переключаем закрепление
            self.app.data_manager.toggle_pin_notes(list(self.selected_notes))
            
            # Обновляем список заметок
            self.refresh_notes()
            
            # Показываем уведомление
            if pinned_count > 0 and unpinned_count > 0:
                self.show_toast("Закрепление изменено!")
            elif pinned_count > 0:
                self.show_toast("Заметки откреплены!")
            else:
                self.show_toast("Заметки закреплены!")
            
            # Выходим из режима выбора
            self.exit_selection_mode()
    
    def update_pin_button_text(self):
        """Обновляет текст кнопки закрепления в зависимости от выбранных заметок."""
        if not self.selected_notes:
            return
        
        if hasattr(self, 'app') and self.app:
            pinned_count = 0
            for note_id in self.selected_notes:
                if self.app.data_manager.is_note_pinned(note_id):
                    pinned_count += 1
            
            if pinned_count == len(self.selected_notes):
                # Все заметки закреплены
                self.pin_btn.text = 'Открепить'
            elif pinned_count == 0:
                # Все заметки не закреплены
                self.pin_btn.text = 'Закрепить'
            else:
                # Смешанное состояние
                self.pin_btn.text = 'Переключить'
    
    def cancel_selection(self, instance):
        """Отменяет выбор заметок и возвращает обычную панель."""
        self.exit_selection_mode()
        self.refresh_notes()
    
    def show_toast(self, message):
        """Показывает ненавязчивое уведомление вверху экрана."""
        from kivy.uix.label import Label
        from kivy.animation import Animation
        
        # Создаем простое уведомление
        toast = Label(
            text=message,
            size_hint=(None, None),
            size=(300, 50),
            pos_hint={'center_x': 0.5, 'top': 0.9},
            color=(1, 1, 1, 1),
            font_size='16sp',
            halign='center'
        )
        toast.bind(size=toast.setter('text_size'))
        
        # Добавляем фон
        from kivy.graphics import Color, RoundedRectangle
        with toast.canvas.before:
            Color(0.2, 0.2, 0.2, 0.8)
            toast.rect = RoundedRectangle(
                pos=toast.pos,
                size=toast.size,
                radius=[10]
            )
        
        # Добавляем на экран
        self.add_widget(toast)
        
        # Анимация появления и исчезновения
        anim = Animation(opacity=0, duration=0.3) + Animation(opacity=1, duration=0.3)
        anim.bind(on_complete=lambda *args: self.remove_widget(toast))
        anim.start(toast)
        
        # Автоматически убираем через 2 секунды
        Clock.schedule_once(lambda dt: self.remove_widget(toast) if toast in self.children else None, 2)
    
    def on_enter(self):
        """Вызывается при переходе на этот экран."""
        self.refresh_notes()
        self.exit_selection_mode()  # Сбрасываем режим выбора
        # Back в режиме выбора = Отмена, иначе стандартное поведение
        try:
            from kivy.base import EventLoop
            win = EventLoop.window
            if win:
                win.bind(on_keyboard=self._on_back)
        except Exception:
            pass
    
    def update_rect(self, instance, value):
        """Обновляет позицию и размер прямоугольника"""
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def _on_back(self, window, key, *args):
        if key == 27:  # Android back
            if self.is_selection_mode:
                self.cancel_selection(None)
                return True
            return False
        return False
    
    def on_note_touch_down(self, widget, touch):
        """Обрабатывает начало касания заметки"""
        # Проверяем, не открыт ли попап (ошибка/отладка)
        if self._is_popup_open():
            return False
            
        if widget.collide_point(*touch.pos):
            # Сбрасываем флаг длинного нажатия
            if hasattr(widget, '_long_press_handled'):
                delattr(widget, '_long_press_handled')
            # Запоминаем стартовые данные для тапа
            widget._touch_start_pos = touch.pos
            widget._touch_start_time = Clock.get_time()
            widget._tap_candidate = True
            # Запускаем таймер для длинного нажатия
            self.long_press_clock = Clock.schedule_once(
                lambda dt: self.on_long_press(widget),
                self.long_press_duration
            )
            return True
        return False
    
    def on_note_touch_up(self, widget, touch):
        """Обрабатывает окончание касания заметки"""
        # Проверяем, не открыт ли попап (ошибка/отладка)
        if self._is_popup_open():
            return False
            
        # Отменяем таймер длинного нажатия
        if self.long_press_clock:
            self.long_press_clock.cancel()
            self.long_press_clock = None
        
        if not widget.collide_point(*touch.pos):
            return False

        # Если был лонгтап — завершаем без дальнейшей обработки
        if hasattr(widget, '_long_press_handled'):
            try:
                delattr(widget, '_long_press_handled')
            except Exception:
                pass
            return True

        # Оценим, что это был короткий тап
        start_pos = getattr(widget, '_touch_start_pos', None)
        if start_pos is not None:
            dx = abs(touch.pos[0] - start_pos[0])
            dy = abs(touch.pos[1] - start_pos[1])
            moved_far = (dx > 10 or dy > 10)
        else:
            moved_far = False

        if self.is_selection_mode:
            # В режиме выбора одиночный тап переключает выделение
            if hasattr(widget, 'note_id') and hasattr(widget, 'checkbox'):
                note_id = widget.note_id
                if note_id in self.selected_notes:
                    self.selected_notes.remove(note_id)
                    widget.checkbox.active = False
                    if not self.selected_notes:
                        self.exit_selection_mode()
                else:
                    self.selected_notes.add(note_id)
                    widget.checkbox.active = True
                self.update_pin_button_text()
            return True

        # Не режим выбора, короткий тап без сдвига — открыть редактор
        if not moved_far:
            self.edit_note_by_widget(widget)
            return True

        return False
    
    def on_long_press(self, widget):
        """Обрабатывает длинное нажатие на заметку"""
        self.long_press_clock = None
        
        # Устанавливаем флаг, что длинное нажатие было обработано
        widget._long_press_handled = True
        
        if hasattr(widget, 'note_id'):
            note_id = widget.note_id
            
            if not self.is_selection_mode:
                # Входим в режим выбора
                self.enter_selection_mode()
                # Выбираем заметку
                if hasattr(widget, 'checkbox'):
                    widget.checkbox.active = True
                    self.selected_notes.add(note_id)
            else:
                # Уже в режиме выбора - переключаем состояние заметки
                if note_id in self.selected_notes:
                    # Отменяем выделение
                    self.selected_notes.remove(note_id)
                    if hasattr(widget, 'checkbox'):
                        widget.checkbox.active = False
                    
                    # Если больше нет выбранных заметок, выходим из режима выбора
                    if not self.selected_notes:
                        self.exit_selection_mode()
                else:
                    # Выбираем заметку
                    self.selected_notes.add(note_id)
                    if hasattr(widget, 'checkbox'):
                        widget.checkbox.active = True
                
                # Обновляем текст кнопки закрепления
                self.update_pin_button_text()
    
    def edit_note_by_widget(self, widget):
        """Редактирует заметку по виджету"""
        if hasattr(widget, 'note_id'):
            note_id = widget.note_id
            if hasattr(self, 'app') and self.app:
                note = self.app.data_manager.get_note(note_id)
                if note:
                    # Сначала передаем заметку в экран редактирования, затем переключаемся
                    self.app.edit_screen.set_note(note)
                    self.manager.current = 'edit'
