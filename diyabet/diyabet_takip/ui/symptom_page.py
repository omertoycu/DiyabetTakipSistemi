from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QTableWidget,
                             QTableWidgetItem, QComboBox, QDateEdit, QDialog,
                             QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class SymptomPage(QWidget):
    def __init__(self, main_window, patient_id=None):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.symptoms = [
            'Nöropati', 'Polifaji', 'Yorgunluk', 'Kilo Kaybı',
            'Polidipsi', 'Bulanık Görme', 'Poliüri',
            'Yaraların Yavaş İyileşmesi'
        ]
        self.belirtiler = {
            'poliuri': 'Poliüri',
            'polifaji': 'Polifaji',
            'polidipsi': 'Polidipsi',
            'noropati': 'Nöropati',
            'kilo_kaybi': 'Kilo Kaybı',
            'yorgunluk': 'Yorgunluk',
            'yara_iyilesme': 'Yaraların Yavaş İyileşmesi',
            'bulanik_gorme': 'Bulanık Görme'
        }
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Semptom ve Belirti Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tarih seçici (günlük gösterim için)
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Gün Seç:"))
        self.selected_date = QDateEdit()
        self.selected_date.setCalendarPopup(True)
        self.selected_date.setDate(QDate.currentDate())
        self.selected_date.dateChanged.connect(self.load_symptoms)
        date_row.addWidget(self.selected_date)
        layout.addLayout(date_row)
        
        # Yeni semptom formu
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)
        
        # Semptom seçimi
        self.symptom_combo = QComboBox()
        self.symptom_combo.addItems(self.symptoms)
        form_layout.addWidget(QLabel("Semptom:"))
        form_layout.addWidget(self.symptom_combo)
        
        # Notlar
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notlar...")
        self.notes_input.setMaximumHeight(60)
        form_layout.addWidget(QLabel("Notlar:"))
        form_layout.addWidget(self.notes_input)
        
        # Kaydet butonu sadece doktor için
        user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
        if user_type == 'doktor':
            save_button = QPushButton("Kaydet")
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            save_button.clicked.connect(self.save_symptom)
            form_layout.addWidget(save_button)
        
        layout.addWidget(form_container)
        
        # Semptom listesi
        self.symptom_table = QTableWidget()
        self.symptom_table.setColumnCount(4)
        self.symptom_table.setHorizontalHeaderLabels([
            "Tarih", "Semptom/Belirti", "Notlar", "İşlemler"
        ])
        layout.addWidget(self.symptom_table)
        
        self.setLayout(layout)
        self.load_symptoms()
    
    def save_symptom(self):
        try:
            symptom = self.symptom_combo.currentText()
            date = self.selected_date.date().toPyDate()
            notes = self.notes_input.toPlainText()
            
            # Semptom kaydet
            symptom_query = """
                INSERT INTO semptom_takibi (hasta_id, semptom, tarih)
                VALUES (%s, %s, %s)
            """
            self.db.execute_query(symptom_query, (
                self.patient_id,
                symptom,
                date
            ))
            
            # Belirti kaydet (ENUM ile birebir aynı değer gönder)
            belirti_query = """
                INSERT INTO belirtiler (hasta_id, belirti_tipi, tarih, notlar)
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(belirti_query, (
                self.patient_id,
                symptom,  # Doğrudan ENUM değeri
                date,
                notes
            ))
            
            QMessageBox.information(self, "Başarılı", "Semptom ve belirti kaydedildi!")
            self.notes_input.clear()
            self.load_symptoms()
            
            # Diyet ve egzersiz önerilerini güncelle
            if hasattr(self.main_window, 'patient_panel'):
                panel = self.main_window.patient_panel
                if hasattr(panel, 'diet_page'):
                    panel.diet_page.load_recommendations()
                if hasattr(panel, 'exercise_page'):
                    panel.exercise_page.load_recommendations()
            # Eğer detay sayfası ise
            if hasattr(self.main_window, 'diet_page'):
                self.main_window.diet_page.load_recommendations()
            if hasattr(self.main_window, 'exercise_page'):
                self.main_window.exercise_page.load_recommendations()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Semptom kaydedilirken bir hata oluştu: {str(e)}")
    
    def load_symptoms(self):
        # Sadece seçilen günün semptomlarını ve belirtilerini göster
        selected = self.selected_date.date().toPyDate()
        query = """
            SELECT s.tarih, s.semptom, b.notlar, s.id
            FROM semptom_takibi s
            LEFT JOIN belirtiler b ON s.hasta_id = b.hasta_id 
                AND s.tarih = b.tarih 
                AND b.belirti_tipi = s.semptom
            WHERE s.hasta_id = %s AND s.tarih = %s
            ORDER BY s.tarih DESC
        """
        symptoms = self.db.fetch_all(query, (self.patient_id, selected))
        self.symptom_table.setRowCount(len(symptoms))
        user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
        
        for row, symptom in enumerate(symptoms):
            # Tarih
            date_str = symptom[0].strftime("%d.%m.%Y")
            self.symptom_table.setItem(row, 0, QTableWidgetItem(date_str))
            # Semptom
            self.symptom_table.setItem(row, 1, QTableWidgetItem(symptom[1]))
            # Notlar
            self.symptom_table.setItem(row, 2, QTableWidgetItem(symptom[2] or ""))
            # Silme butonu sadece doktor için
            if user_type == 'doktor':
                delete_button = QPushButton("Sil")
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        padding: 5px;
                        border: none;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_button.clicked.connect(lambda checked, id=symptom[3]: self.delete_symptom(id))
                self.symptom_table.setCellWidget(row, 3, delete_button)
            else:
                self.symptom_table.setItem(row, 3, QTableWidgetItem("-"))
    
    def delete_symptom(self, symptom_id):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu semptomu silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Önce semptom bilgisini al
                query = "SELECT semptom, tarih FROM semptom_takibi WHERE id = %s AND hasta_id = %s"
                result = self.db.fetch_one(query, (symptom_id, self.patient_id))
                if result:
                    symptom, date = result
                    # Semptomu sil
                    self.db.execute_query(
                        "DELETE FROM semptom_takibi WHERE id = %s AND hasta_id = %s",
                        (symptom_id, self.patient_id)
                    )
                    # İlgili belirtiyi sil (ENUM ile birebir aynı değer kullan)
                    self.db.execute_query(
                        "DELETE FROM belirtiler WHERE hasta_id = %s AND belirti_tipi = %s AND tarih = %s",
                        (self.patient_id, symptom, date)
                    )
                    self.load_symptoms()
                    QMessageBox.information(self, "Başarılı", "Semptom silindi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Semptom silinirken bir hata oluştu: {str(e)}") 