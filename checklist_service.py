import os
import sqlite3
from typing import Optional
from dataclasses import dataclass


@dataclass
class ChecklistItem:
    id: Optional[int]
    order_index: int
    title: str
    description: str
    image_path: Optional[str]
    is_active: bool


class ChecklistService:
    def __init__(self):
        self.upload_folder = "uploads/images/"
        os.makedirs(self.upload_folder, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Создание базы данных и таблиц если они не существуют"""
        conn = sqlite3.connect('checklists.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS checklist_items
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      order_index INTEGER,
                      title TEXT,
                      description TEXT,
                      image_path TEXT,
                      is_active BOOLEAN DEFAULT TRUE)''')

        conn.commit()
        conn.close()
        print("База чеклистов инициализирована")

    def add_item(self, title: str, description: str, image_path: Optional[str] = None) -> int:
        conn = sqlite3.connect('checklists.db')
        c = conn.cursor()

        # Получаем максимальный order_index
        c.execute("SELECT MAX(order_index) FROM checklist_items")
        max_index = c.fetchone()[0] or 0

        c.execute('''INSERT INTO checklist_items 
                    (order_index, title, description, image_path, is_active)
                    VALUES (?, ?, ?, ?, ?)''',
                  (max_index + 1, title, description, image_path, True))

        item_id = c.lastrowid
        conn.commit()
        conn.close()
        return item_id

    def get_all_active_items(self) -> list[ChecklistItem]:
        conn = sqlite3.connect('checklists.db')
        c = conn.cursor()

        c.execute('''SELECT id, order_index, title, description, image_path, is_active
                    FROM checklist_items 
                    WHERE is_active = TRUE 
                    ORDER BY order_index''')

        items = []
        for row in c.fetchall():
            items.append(ChecklistItem(*row))

        conn.close()
        return items

    def update_item(self, item_id: int, **kwargs):
        conn = sqlite3.connect('checklists.db')
        c = conn.cursor()

        if 'image_path' in kwargs and kwargs['image_path']:
            # Удаляем старую картинку если есть
            c.execute("SELECT image_path FROM checklist_items WHERE id = ?", (item_id,))
            old_image = c.fetchone()[0]
            if old_image and os.path.exists(old_image):
                os.remove(old_image)

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [item_id]

        c.execute(f"UPDATE checklist_items SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def delete_item(self, item_id: int):
        conn = sqlite3.connect('checklists.db')
        c = conn.cursor()

        # Удаляем картинку если есть
        c.execute("SELECT image_path FROM checklist_items WHERE id = ?", (item_id,))
        image_path = c.fetchone()[0]
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

        c.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
