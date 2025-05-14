import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="145323",
                database="diyabet_takip",
                charset="utf8mb4",
                collation="utf8mb4_turkish_ci",
                auth_plugin='mysql_native_password'
            )
            if self.connection.is_connected():
                print("Veritabanı bağlantısı başarılı")
        except Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            raise
    
    def get_connection(self):
        if not self.connection.is_connected():
            self._initialize_connection()
        return self.connection
    
    def execute_query(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Sorgu hatası: {e}")
            if cursor:
                cursor.close()
            return None
    
    def fetch_all(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Sorgu hatası: {e}")
            if cursor:
                cursor.close()
            return []
    
    def fetch_one(self, query, params=None):
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Sorgu hatası: {e}")
            if cursor:
                cursor.close()
            return None
    
    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("Veritabanı bağlantısı kapatıldı") 