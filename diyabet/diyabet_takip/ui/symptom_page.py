from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QTableWidget,
                             QTableWidgetItem, QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os
from datetime import datetime

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class SymptomPage(QWidget):
    def __init__(self, main_window, patient_id=None):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.symptoms = [
            "Nöropati", "Polifaji", "Yorgunluk", "Kilo Kaybı",
            "Polidipsi", "Bulanık Görme", "Poliüri",
            "Yaraların Yavaş İyileşmesi"
        ]
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Semptom Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Yeni semptom formu
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)
        
        # Semptom seçimi
        self.symptom_combo = QComboBox()
        self.symptom_combo.addItems(self.symptoms)
        form_layout.addWidget(QLabel("Semptom:"))
        form_layout.addWidget(self.symptom_combo)
        
        # Tarih
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("Tarih:"))
        form_layout.addWidget(self.date_input)
        
        # Kaydet butonu
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
            "Tarih", "Semptom", "Durum", "İşlemler"
        ])
        layout.addWidget(self.symptom_table)
        
        self.setLayout(layout)
        self.load_symptoms()
    
    def save_symptom(self):
        try:
            symptom = self.symptom_combo.currentText()
            date = self.date_input.date().toPyDate()
            
            query = """
                INSERT INTO semptom_takibi (hasta_id, semptom, tarih)
                VALUES (%s, %s, %s)
            """
            
            self.db.execute_query(query, (
                self.patient_id,
                symptom,
                date
            ))
            
            QMessageBox.information(self, "Başarılı", "Semptom kaydedildi!")
            self.load_symptoms()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Semptom kaydedilirken bir hata oluştu: {str(e)}")
    
    def load_symptoms(self):
        query = """
            SELECT tarih, semptom, id
            FROM semptom_takibi
            WHERE hasta_id = %s
            ORDER BY tarih DESC
        """
        
        symptoms = self.db.fetch_all(query, (self.patient_id,))
        
        self.symptom_table.setRowCount(len(symptoms))
        for row, symptom in enumerate(symptoms):
            # Tarih
            date_str = symptom[0].strftime("%d.%m.%Y")
            self.symptom_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Semptom
            self.symptom_table.setItem(row, 1, QTableWidgetItem(symptom[1]))
            
            # Durum
            status_item = QTableWidgetItem("Aktif")
            status_item.setForeground(Qt.red)
            self.symptom_table.setItem(row, 2, status_item)
            
            # Silme butonu
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
            delete_button.clicked.connect(lambda checked, id=symptom[2]: self.delete_symptom(id))
            self.symptom_table.setCellWidget(row, 3, delete_button)
    
    def delete_symptom(self, symptom_id):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu semptomu silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = "DELETE FROM semptom_takibi WHERE id = %s AND hasta_id = %s"
            self.db.execute_query(query, (symptom_id, self.patient_id))
            self.load_symptoms()
            QMessageBox.information(self, "Başarılı", "Semptom silindi!") 