import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot_data.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Tabel users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel gacha_history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gacha_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                country TEXT,
                phone_number TEXT,
                success BOOLEAN,
                otp_code TEXT,
                message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Tabel admin_numbers untuk nomor yang dibuat admin
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT,
                phone_number TEXT,
                otp_code TEXT,
                created_by INTEGER,
                used BOOLEAN DEFAULT FALSE,
                message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel channels untuk menyimpan channel/grup yang terdaftar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                chat_title TEXT,
                chat_type TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name, last_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()
    
    def add_gacha_record(self, user_id, country, phone_number, success, otp_code, message_id=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO gacha_history (user_id, country, phone_number, success, otp_code, message_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, country, phone_number, success, otp_code, message_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_gacha_message_id(self, record_id, message_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE gacha_history SET message_id = ? WHERE id = ?
        ''', (message_id, record_id))
        self.conn.commit()
    
    def get_user_stats(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as total_gacha,
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_gacha
            FROM gacha_history 
            WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchone()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()
    
    def get_all_gacha_records(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT gh.*, u.username 
            FROM gacha_history gh 
            LEFT JOIN users u ON gh.user_id = u.user_id
            ORDER BY gh.created_at DESC
        ''')
        return cursor.fetchall()
    
    # Fungsi untuk fitur admin
    def add_admin_number(self, country, phone_number, otp_code, admin_id, message_id=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO admin_numbers (country, phone_number, otp_code, created_by, message_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (country, phone_number, otp_code, admin_id, message_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_admin_message_id(self, record_id, message_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE admin_numbers SET message_id = ? WHERE id = ?
        ''', (message_id, record_id))
        self.conn.commit()
    
    def get_admin_numbers(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT an.*, u.username 
            FROM admin_numbers an 
            LEFT JOIN users u ON an.created_by = u.user_id
            ORDER BY an.created_at DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    
    def get_available_admin_numbers(self, country=None):
        cursor = self.conn.cursor()
        if country:
            cursor.execute('''
                SELECT * FROM admin_numbers 
                WHERE used = FALSE AND country = ?
                ORDER BY created_at DESC
            ''', (country,))
        else:
            cursor.execute('''
                SELECT * FROM admin_numbers 
                WHERE used = FALSE 
                ORDER BY created_at DESC
            ''')
        return cursor.fetchall()
    
    # Fungsi untuk channel/grup
    def add_channel(self, chat_id, chat_title, chat_type):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO channels (chat_id, chat_title, chat_type)
            VALUES (?, ?, ?)
        ''', (chat_id, chat_title, chat_type))
        self.conn.commit()
    
    def get_active_channels(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM channels WHERE is_active = TRUE
        ''')
        return cursor.fetchall()
    
    def remove_channel(self, chat_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM channels WHERE chat_id = ?
        ''', (chat_id,))
        self.conn.commit()

db = Database()