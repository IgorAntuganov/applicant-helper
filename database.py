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
    conn.commit()
    conn.close()

def get_user_language_from_db(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_user_to_db(user_id, language, message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone()

    if exists:
        cursor.execute('''
            UPDATE users 
            SET language = ?, last_activity = CURRENT_TIMESTAMP,
                username = ?, first_name = ?, last_name = ?
            WHERE user_id = ?
        ''', (language, message.from_user.username,
              message.from_user.first_name, message.from_user.last_name, user_id))
    else:
        cursor.execute('''
            INSERT INTO users (user_id, language, username, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, language, message.from_user.username,
              message.from_user.first_name, message.from_user.last_name))

    conn.commit()
    conn.close()

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
