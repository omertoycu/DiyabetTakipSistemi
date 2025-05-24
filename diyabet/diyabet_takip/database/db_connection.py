import mysql.connector
from mysql.connector import Error

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
                self.connection.cursor().execute("SET time_zone = '+03:00';")
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
    
    def add_critical_blood_sugar_warning(self, hasta_id, olcum_degeri, tarih=None):

        if olcum_degeri < 70:
            uyari_tipi = 'Kritik Seviye'
            mesaj = f"Hastanın kan şekeri seviyesi 70 mg/dL'nin altına düştü. Hipoglisemi riski! Hızlı müdahale gerekebilir. (Ölçüm: {olcum_degeri} mg/dL)"
        elif olcum_degeri > 200:
            uyari_tipi = 'Kritik Seviye'
            mesaj = f"Hastanın kan şekeri seviyesi 200 mg/dL'nin üzerinde. Hiperglisemi durumu. Acil müdahale gerekebilir. (Ölçüm: {olcum_degeri} mg/dL)"
        else:
            return  # Kritik değilse ekleme
        from datetime import datetime
        now = tarih if tarih else datetime.now()
        # Aynı gün ve tipte uyarı var mı?
        check_query = "SELECT id FROM uyarilar WHERE hasta_id = %s AND uyari_tipi = %s AND DATE(tarih) = %s"
        cursor = self.get_connection().cursor()
        cursor.execute(check_query, (hasta_id, uyari_tipi, now.date()))
        if cursor.fetchone():
            cursor.close()
            return  # Zaten var
        cursor.close()
        # Ekle
        insert_query = "INSERT INTO uyarilar (hasta_id, uyari_tipi, mesaj, tarih) VALUES (%s, %s, %s, %s)"
        self.execute_query(insert_query, (hasta_id, uyari_tipi, mesaj, now)) 