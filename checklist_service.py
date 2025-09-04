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


# checklist_service.py
class ChecklistService:
    def __init__(self, db_path='checklist.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Таблица для каждой комбинации статуса и гражданства
        combinations = [
            ('in_russia_kazakhstan', 'Уже в России - Казахстан'),
            ('in_russia_china', 'Уже в России - Китай'),
            ('in_russia_belarus', 'Уже в России - Беларусь'),
            ('not_in_russia_kazakhstan', 'Еще не в России - Казахстан'),
            ('not_in_russia_china', 'Еще не в России - Китай'),
            ('not_in_russia_belarus', 'Еще не в России - Беларусь'),
        ]

        for table_name, description in combinations:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    image_path TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        self.conn.commit()

    # checklist_service.py
    def add_item(self, checklist_type, title, description, image_path=None):
        """Добавляет пункт в конкретный чеклист"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                INSERT INTO {checklist_type} (title, description, image_path)
                VALUES (?, ?, ?)
            ''', (title, description, image_path))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_items(self, checklist_type):
        """Получает все пункты конкретного чеклиста"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT * FROM {checklist_type} WHERE is_active = 1 ORDER BY created_at
            ''')
            return cursor.fetchall()
        except Exception as e:
            raise e

    def get_item(self, checklist_type, item_id):
        """Получает один конкретный пункт из чеклиста"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT * FROM {checklist_type} WHERE id = ? AND is_active = 1
            ''', (item_id,))
            result = cursor.fetchone()

            if result:
                return {
                    'id': result[0],
                    'title': result[1],
                    'description': result[2],
                    'image_path': result[3],
                    'is_active': result[4],
                    'created_at': result[5]
                }
            return None

        except Exception as e:
            raise e

    def update_item(self, checklist_type: str, item_id: int, **kwargs):
        """Обновляет пункт в конкретном чеклисте"""
        conn = self.conn
        try:
            cursor = conn.cursor()

            # Убираем логику работы с картинками
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [item_id]

            cursor.execute(f"UPDATE {checklist_type} SET {set_clause} WHERE id = ?", values)
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e

    def delete_item(self, checklist_type: str, item_id: int):
        print(checklist_type)
        conn = self.conn
        try:
            cursor = conn.cursor()

            # Удаляем картинку если есть
            cursor.execute(f"SELECT image_path FROM {checklist_type} WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            if result and result[0] and os.path.exists(result[0]):
                os.remove(result[0])

            cursor.execute(f"DELETE FROM {checklist_type} WHERE id = ?", (item_id,))
            conn.commit()

        except Exception as e:
            conn.rollback()
            raise e