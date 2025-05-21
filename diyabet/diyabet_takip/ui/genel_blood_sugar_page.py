from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QDateEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime
from database.db_connection import DatabaseConnection

class GenelBloodSugarPage(QWidget):
    def __init__(self, main_window, patient_id=None, readonly=False):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.readonly = readonly
        self.db = DatabaseConnection()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Genel Kan Şekeri")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Sadece doktorlar için giriş formu
        if not self.readonly:
            form_layout = QHBoxLayout()
            self.value_input = QLineEdit()
            self.value_input.setPlaceholderText("Genel Kan Şekeri (mg/dL)")
            form_layout.addWidget(QLabel("Değer:"))
            form_layout.addWidget(self.value_input)
            self.date_input = QDateEdit()
            self.date_input.setCalendarPopup(True)
            self.date_input.setDate(QDate.currentDate())
            form_layout.addWidget(QLabel("Tarih:"))
            form_layout.addWidget(self.date_input)
            self.notes_input = QTextEdit()
            self.notes_input.setPlaceholderText("Notlar...")
            self.notes_input.setMaximumHeight(60)
            form_layout.addWidget(QLabel("Notlar:"))
            form_layout.addWidget(self.notes_input)
            save_button = QPushButton("Kaydet")
            save_button.clicked.connect(self.save_blood_sugar)
            form_layout.addWidget(save_button)
            layout.addLayout(form_layout)

        # Kayıtları gösteren tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Değer (mg/dL)", "Notlar", "Doktor"])
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_genel_blood_sugar()

    def save_blood_sugar(self):
        try:
            value = float(self.value_input.text())
            date = self.date_input.date().toPyDate()
            notes = self.notes_input.toPlainText()
            doktor_id = self.main_window.current_user['id']
            query = """
                INSERT INTO genel_kan_sekeri (hasta_id, doktor_id, deger, tarih, notlar)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute_query(query, (
                self.patient_id,
                doktor_id,
                value,
                date,
                notes
            ))
            # Önerileri güncelle
            self.update_recommendations(value, date)
            QMessageBox.information(self, "Başarılı", "Genel kan şekeri kaydedildi!")
            self.load_genel_blood_sugar()
        except ValueError:
            QMessageBox.critical(self, "Hata", "Lütfen geçerli bir sayı girin!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt sırasında bir hata oluştu: {str(e)}")

    def update_recommendations(self, blood_sugar_value, date):
        # Son semptomları al
        symptoms_query = """
            SELECT semptom FROM semptom_takibi 
            WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        symptoms = self.db.fetch_all(symptoms_query, (self.patient_id, date))
        symptoms = [s[0] for s in symptoms]
        def normalize(s):
            return s.strip().lower()
        norm_symptoms = set([normalize(s) for s in symptoms])
        # Tabloya göre öneri
        # Diyet
        if blood_sugar_value < 70 and set(map(normalize, ["Nöropati", "Polifaji", "Yorgunluk"])).issubset(norm_symptoms):
            diet = "Dengeli Beslenme"
            exercise = "Yok"
        elif blood_sugar_value < 70 and set(map(normalize, ["Yorgunluk", "Kilo Kaybı"])).issubset(norm_symptoms):
            diet = "Az Şekerli Diyet"
            exercise = "Yürüyüş"
        elif 70 <= blood_sugar_value <= 110 and set(map(normalize, ["Polifaji", "Polidipsi"])).issubset(norm_symptoms):
            diet = "Dengeli Beslenme"
            exercise = "Yürüyüş"
        elif 70 <= blood_sugar_value <= 110 and set(map(normalize, ["Bulanık Görme", "Nöropati"])).issubset(norm_symptoms):
            diet = "Az Şekerli Diyet"
            exercise = "Klinik Egzersiz"
        elif 110 < blood_sugar_value < 180 and set(map(normalize, ["Poliüri", "Polidipsi"])).issubset(norm_symptoms):
            diet = "Şekersiz Diyet"
            exercise = "Klinik Egzersiz"
        elif 110 < blood_sugar_value < 180 and set(map(normalize, ["Yorgunluk", "Nöropati", "Bulanık Görme"])).issubset(norm_symptoms):
            diet = "Az Şekerli Diyet"
            exercise = "Yürüyüş"
        elif blood_sugar_value >= 180 and set(map(normalize, ["Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"])).issubset(norm_symptoms):
            diet = "Şekersiz Diyet"
            exercise = "Klinik Egzersiz"
        elif blood_sugar_value >= 180 and set(map(normalize, ["Yaraların Yavaş İyileşmesi", "Kilo Kaybı"])).issubset(norm_symptoms):
            diet = "Şekersiz Diyet"
            exercise = "Yürüyüş"
        else:
            diet = "-"
            exercise = "-"
        # Veritabanına kaydet
        diet_query = """
            INSERT INTO diyet_onerileri (hasta_id, tarih, oneriler)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE oneriler = %s
        """
        exercise_query = """
            INSERT INTO egzersiz_onerileri (hasta_id, tarih, oneriler)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE oneriler = %s
        """
        self.db.execute_query(diet_query, (self.patient_id, date, diet, diet))
        self.db.execute_query(exercise_query, (self.patient_id, date, exercise, exercise))

    def load_genel_blood_sugar(self):
        query = """
            SELECT tarih, deger, notlar, doktor_id FROM genel_kan_sekeri WHERE hasta_id = %s ORDER BY tarih DESC
        """
        results = self.db.fetch_all(query, (self.patient_id,))
        self.table.setRowCount(len(results))
        for row, (tarih, deger, notlar, doktor_id) in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(tarih.strftime("%d.%m.%Y")))
            self.table.setItem(row, 1, QTableWidgetItem(str(deger)))
            self.table.setItem(row, 2, QTableWidgetItem(notlar or ""))
            # Doktor adı çek
            doktor_query = "SELECT ad, soyad FROM kullanicilar WHERE id = %s"
            doktor = self.db.fetch_one(doktor_query, (doktor_id,))
            doktor_ad = f"{doktor[0]} {doktor[1]}" if doktor else "-"
            self.table.setItem(row, 3, QTableWidgetItem(doktor_ad)) 