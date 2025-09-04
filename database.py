import sqlite3

def init_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT NOT NULL DEFAULT 'russian',
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Новая таблица для пройденных пунктов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_completed_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            checklist_type TEXT,
            item_id INTEGER,
            item_title TEXT,
            item_description TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()

def get_user_language_from_db(user_id):
    """Получить язык пользователя из базы данных, возвращает None если пользователя нет"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None  # Возвращаем None если пользователя нет


def save_user_to_db(user_id, language, message):
    """Сохранить пользователя в базу данных"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone()

    if exists:
        # Обновляем язык и время активности
        cursor.execute('''
            UPDATE users 
            SET language = ?, last_activity = CURRENT_TIMESTAMP,
                username = ?, first_name = ?, last_name = ?
            WHERE user_id = ?
        ''', (language, message.from_user.username,
              message.from_user.first_name, message.from_user.last_name, user_id))
    else:
        # Добавляем нового пользователя
        cursor.execute('''
            INSERT INTO users (user_id, language, username, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, language, message.from_user.username,
              message.from_user.first_name, message.from_user.last_name))

    conn.commit()
    conn.close()
def check_user_exists(user_id):
    """Проверить, существует ли пользователь в базе"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def update_user_activity(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()

def get_user_stats():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language, COUNT(*) as count FROM users GROUP BY language')
    stats = cursor.fetchall()
    conn.close()
    return stats


def save_user_status(user_id, status):
    """Сохранить статус пользователя в базе данных"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, есть ли колонка status в таблице
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'status' not in columns:
        # Добавляем колонку если её нет
        cursor.execute('ALTER TABLE users ADD COLUMN status TEXT')

    # Обновляем статус пользователя
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))

    conn.commit()
    conn.close()


def save_user_citizenship(user_id, citizenship):
    """Сохранить гражданство пользователя в базе данных"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, есть ли колонка citizenship в таблице
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'citizenship' not in columns:
        # Добавляем колонку если её нет
        cursor.execute('ALTER TABLE users ADD COLUMN citizenship TEXT')

    # Обновляем гражданство пользователя
    cursor.execute('UPDATE users SET citizenship = ? WHERE user_id = ?', (citizenship, user_id))

    conn.commit()
    conn.close()


def get_user_data(user_id):
    """Получить все данные пользователя из базы данных"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language, status, citizenship FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'language': result[0],
            'status': result[1],
            'citizenship': result[2]
        }
    return None
# database.py
def save_completed_item(user_id, checklist_type, item_id, item_title, item_description):
    """Сохраняет пройденный пункт чек-листа"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_completed_items (user_id, checklist_type, item_id, item_title, item_description)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, checklist_type, item_id, item_title, item_description))

    conn.commit()
    conn.close()


def get_user_completed_items(user_id, checklist_type):
    """Получает все пройденные пункты пользователя для конкретного чек-листа"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT item_id, item_title, item_description, completed_at 
        FROM user_completed_items 
        WHERE user_id = ? AND checklist_type = ?
        ORDER BY completed_at
    ''', (user_id, checklist_type))

    items = cursor.fetchall()
    conn.close()

    return items


def is_item_completed(user_id, checklist_type, item_id):
    """Проверяет, пройден ли конкретный пункт пользователем"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM user_completed_items 
        WHERE user_id = ? AND checklist_type = ? AND item_id = ?
    ''', (user_id, checklist_type, item_id))

    result = cursor.fetchone()
    conn.close()

    return result is not None


# database.py
def remove_completed_item(user_id, checklist_type, item_id):
    """Удаляет отметку о выполнении пункта"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM user_completed_items 
        WHERE user_id = ? AND checklist_type = ? AND item_id = ?
    ''', (user_id, checklist_type, item_id))

    conn.commit()
    conn.close()