import sqlite3


class Analytics:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path

    def get_user_stats(self):
        """Статистика пользователей по языкам"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT language, COUNT(*) FROM users GROUP BY language')
        stats = cursor.fetchall()

        conn.close()
        return dict(stats)

    def get_daily_active_users(self):
        """Количество активных пользователей за сегодня"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE date(last_activity) = date('now')
        ''')
        count = cursor.fetchone()[0]

        conn.close()
        return count