import json
import os
from datetime import datetime
from typing import List, Dict, Any

class DataManager:
    def __init__(self):
        self.notes_file = "notes.json"
        self.settings_file = "settings.json"
        self.notes = []
        self.settings = {"show_welcome": True}
        self.load_data()
    
    def load_data(self):
        """Загружает заметки и настройки из файлов"""
        # Загружаем заметки
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.notes = []
        else:
            self.notes = []
        
        # Загружаем настройки
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.settings = {"show_welcome": True}
        else:
            self.settings = {"show_welcome": True}
    
    def save_notes(self):
        """Сохраняет заметки в файл"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def add_note(self, title: str, content: str) -> Dict[str, Any]:
        """Добавляет новую заметку"""
        note = {
            "id": len(self.notes) + 1,
            "title": title.strip() or "Без заголовка",
            "content": content.strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "pinned": False
        }
        self.notes.append(note)
        self.save_notes()
        return note
    
    def update_note(self, note_id: int, title: str, content: str) -> bool:
        """Обновляет существующую заметку"""
        for note in self.notes:
            if note["id"] == note_id:
                note["title"] = title.strip() or "Без заголовка"
                note["content"] = content.strip()
                note["updated_at"] = datetime.now().isoformat()
                self.save_notes()
                return True
        return False
    
    def delete_note(self, note_id: int) -> bool:
        """Удаляет заметку по ID"""
        for i, note in enumerate(self.notes):
            if note["id"] == note_id:
                del self.notes[i]
                self.save_notes()
                return True
        return False
    
    def delete_notes(self, note_ids: List[int]) -> int:
        """Удаляет несколько заметок по списку ID"""
        deleted_count = 0
        self.notes = [note for note in self.notes if note["id"] not in note_ids]
        if deleted_count > 0:
            self.save_notes()
        return deleted_count
    
    def get_notes(self) -> List[Dict[str, Any]]:
        """Возвращает все заметки, отсортированные по дате обновления (закрепленные сверху)"""
        # Сначала закрепленные, потом обычные, внутри каждой группы по дате обновления
        pinned_notes = [note for note in self.notes if note.get("pinned", False)]
        unpinned_notes = [note for note in self.notes if not note.get("pinned", False)]
        
        pinned_sorted = sorted(pinned_notes, key=lambda x: x["updated_at"], reverse=True)
        unpinned_sorted = sorted(unpinned_notes, key=lambda x: x["updated_at"], reverse=True)
        
        return pinned_sorted + unpinned_sorted
    
    def get_note(self, note_id: int) -> Dict[str, Any]:
        """Возвращает заметку по ID"""
        for note in self.notes:
            if note["id"] == note_id:
                return note
        return None
    
    def set_show_welcome(self, show: bool):
        """Устанавливает флаг показа стартового окна"""
        self.settings["show_welcome"] = show
        self.save_settings()
    
    def should_show_welcome(self) -> bool:
        """Проверяет, нужно ли показывать стартовое окно"""
        return self.settings.get("show_welcome", True)
    
    def toggle_pin_note(self, note_id: int) -> bool:
        """Переключает состояние закрепления заметки"""
        for note in self.notes:
            if note["id"] == note_id:
                note["pinned"] = not note.get("pinned", False)
                note["updated_at"] = datetime.now().isoformat()
                self.save_notes()
                return True
        return False
    
    def toggle_pin_notes(self, note_ids: List[int]) -> int:
        """Переключает состояние закрепления нескольких заметок"""
        pinned_count = 0
        for note in self.notes:
            if note["id"] in note_ids:
                note["pinned"] = not note.get("pinned", False)
                note["updated_at"] = datetime.now().isoformat()
                pinned_count += 1
        if pinned_count > 0:
            self.save_notes()
        return pinned_count
    
    def is_note_pinned(self, note_id: int) -> bool:
        """Проверяет, закреплена ли заметка"""
        for note in self.notes:
            if note["id"] == note_id:
                return note.get("pinned", False)
        return False
