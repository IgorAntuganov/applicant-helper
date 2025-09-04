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
            ('in_russia_kazakhstan', '🇷🇺 Уже в России • 🇰🇿 Казахстан',),
            ('in_russia_tajikistan', '🇷🇺 Уже в России • 🇹🇯 Таджикистан',),
            ('in_russia_uzbekistan', '🇷🇺 Уже в России • 🇺🇿 Узбекистан',),
            ('in_russia_china', '🇷🇺 Уже в России • 🇨🇳 Китай',),
            ('in_russia_belarus', '🇷🇺 Уже в России • 🇧🇾 Беларусь',),
            ('in_russia_ukraine', '🇷🇺 Уже в России • 🇺🇦 Украина',),

            ('not_in_russia_kazakhstan', '🌍 Еще не в России • 🇰🇿 Казахстан',),
            ('not_in_russia_tajikistan', '🌍 Еще не в России • 🇹🇯 Таджикистан',),
            ('not_in_russia_uzbekistan', '🌍 Еще не в России • 🇺🇿 Узбекистан',),
            ('not_in_russia_china', '🌍 Еще не в России • 🇨🇳 Китай',),
            ('not_in_russia_belarus', '🌍 Еще не в России • 🇧🇾 Беларусь',),
            ('not_in_russia_ukraine', '🌍 Еще не в России • 🇺🇦 Украина'),

        ]

        for table_name, description in combinations:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    image_path TEXT,a
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        self.conn.commit()

    def add_item(self, checklist_type, title, description, position, image_path=None):
        """Добавляет пункт в конкретный чеклист на указанную позицию"""
        try:
            cursor = self.conn.cursor()

            # Если позиция не указана - добавляем в конец
            if position is None:
                cursor.execute(f'''
                    INSERT INTO {checklist_type} (title, description, image_path)
                    VALUES (?, ?, ?)
                ''', (title, description, image_path))
                self.conn.commit()
                return cursor.lastrowid

            # Получаем текущие пункты
            cursor.execute(f'SELECT id, title, description, image_path FROM {checklist_type} ORDER BY id')
            items = cursor.fetchall()

            # Если позиция больше количества элементов - добавляем в конец
            if position >= len(items):
                cursor.execute(f'''
                    INSERT INTO {checklist_type} (title, description, image_path)
                    VALUES (?, ?, ?)
                ''', (title, description, image_path))
                self.conn.commit()
                return cursor.lastrowid

            # Вставляем новый элемент в конец
            cursor.execute(f'''
                INSERT INTO {checklist_type} (title, description, image_path)
                VALUES (?, ?, ?)
            ''', (title, description, image_path))
            new_id = cursor.lastrowid

            # Получаем все элементы снова (включая новый)
            cursor.execute(f'SELECT id, title, description, image_path FROM {checklist_type} ORDER BY id')
            all_items = cursor.fetchall()

            # "Сдвигаем" элементы начиная с позиции вставки
            for i in range(len(all_items) - 1, position, -1):
                current_item = all_items[i]
                prev_item = all_items[i - 1]

                # Меняем местами содержимое текущего и предыдущего элемента
                cursor.execute(f'''
                    UPDATE {checklist_type} 
                    SET title = ?, description = ?, image_path = ?
                    WHERE id = ?
                ''', (prev_item[1], prev_item[2], prev_item[3], current_item[0]))

                cursor.execute(f'''
                    UPDATE {checklist_type} 
                    SET title = ?, description = ?, image_path = ?
                    WHERE id = ?
                ''', (current_item[1], current_item[2], current_item[3], prev_item[0]))

            self.conn.commit()
            return new_id

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