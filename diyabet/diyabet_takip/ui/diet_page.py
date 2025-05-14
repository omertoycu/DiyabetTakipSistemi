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

class DietPage(QWidget):
    def __init__(self, main_window, patient_id=None):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Diyet Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Yeni diyet formu
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)
        
        # Diyet tipi
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Dengeli Beslenme", "Az Şekerli Diyet", "Şekersiz Diyet"])
        form_layout.addWidget(QLabel("Diyet Tipi:"))
        form_layout.addWidget(self.type_combo)
        
        # Tarih
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("Tarih:"))
        form_layout.addWidget(self.date_input)
        
        # Durum
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Uygulandı", "Uygulanmadı"])
        form_layout.addWidget(QLabel("Durum:"))
        form_layout.addWidget(self.status_combo)
        
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
        save_button.clicked.connect(self.save_diet)
        form_layout.addWidget(save_button)
        
        layout.addWidget(form_container)
        
        # Diyet listesi
        self.diet_table = QTableWidget()
        self.diet_table.setColumnCount(5)
        self.diet_table.setHorizontalHeaderLabels([
            "Tarih", "Diyet Tipi", "Durum", "Önerilen", "İşlemler"
        ])
        layout.addWidget(self.diet_table)
        
        self.setLayout(layout)
        self.load_diets()
    
    def save_diet(self):
        try:
            diet_type = self.type_combo.currentText()
            date = self.date_input.date().toPyDate()
            status = self.status_combo.currentText()
            
            # Önerilen diyet tipini kontrol et
            recommended_type = self.get_recommended_diet()
            
            query = """
                INSERT INTO diyet_takibi (hasta_id, diyet_tipi, tarih, durum, onerilen)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (
                self.patient_id,
                diet_type,
                date,
                status,
                recommended_type
            ))
            
            QMessageBox.information(self, "Başarılı", "Diyet kaydedildi!")
            self.load_diets()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Diyet kaydedilirken bir hata oluştu: {str(e)}")
    
    def load_diets(self):
        query = """
            SELECT tarih, diyet_tipi, durum, onerilen, id
            FROM diyet_takibi
            WHERE hasta_id = %s
            ORDER BY tarih DESC
        """
        
        diets = self.db.fetch_all(query, (self.patient_id,))
        
        self.diet_table.setRowCount(len(diets))
        for row, diet in enumerate(diets):
            # Tarih
            date_str = diet[0].strftime("%d.%m.%Y")
            self.diet_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Diyet tipi
            self.diet_table.setItem(row, 1, QTableWidgetItem(diet[1]))
            
            # Durum
            status_item = QTableWidgetItem(diet[2])
            if diet[2] == "Uygulandı":
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            self.diet_table.setItem(row, 2, status_item)
            
            # Önerilen
            self.diet_table.setItem(row, 3, QTableWidgetItem(diet[3] or "-"))
            
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
            delete_button.clicked.connect(lambda checked, id=diet[4]: self.delete_diet(id))
            self.diet_table.setCellWidget(row, 4, delete_button)
    
    def get_recommended_diet(self):
        # Kan şekeri ve semptom verilerini al
        today = datetime.now().date()
        
        # Kan şekeri ortalamasını hesapla
        blood_sugar_query = """
            SELECT AVG(olcum_degeri)
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        blood_sugar_result = self.db.fetch_one(blood_sugar_query, (self.patient_id, today))
        average_blood_sugar = blood_sugar_result[0] if blood_sugar_result[0] else 0
        
        # Semptomları al
        symptoms_query = """
            SELECT semptom
            FROM semptom_takibi
            WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        symptoms_result = self.db.fetch_all(symptoms_query, (self.patient_id, today))
        symptoms = [s[0] for s in symptoms_result]
        
        # Önerilen diyet tipini belirle
        if average_blood_sugar < 70 and all(s in symptoms for s in ["Nöropati", "Polifaji", "Yorgunluk"]):
            return "Dengeli Beslenme"
        elif 70 <= average_blood_sugar <= 110 and all(s in symptoms for s in ["Yorgunluk", "Kilo Kaybı"]):
            return "Az Şekerli Diyet"
        elif 70 <= average_blood_sugar <= 110 and all(s in symptoms for s in ["Polifaji", "Polidipsi"]):
            return "Dengeli Beslenme"
        elif 110 < average_blood_sugar <= 180 and all(s in symptoms for s in ["Bulanık Görme", "Nöropati"]):
            return "Az Şekerli Diyet"
        elif 110 < average_blood_sugar <= 180 and all(s in symptoms for s in ["Poliüri", "Polidipsi"]):
            return "Şekersiz Diyet"
        elif 110 < average_blood_sugar <= 180 and all(s in symptoms for s in ["Yorgunluk", "Nöropati", "Bulanık Görme"]):
            return "Az Şekerli Diyet"
        elif average_blood_sugar > 180 and all(s in symptoms for s in ["Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"]):
            return "Şekersiz Diyet"
        elif average_blood_sugar > 180 and all(s in symptoms for s in ["Yaraların Yavaş İyileşmesi", "Kilo Kaybı"]):
            return "Şekersiz Diyet"
        
        return None
    
    def delete_diet(self, diet_id):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu diyeti silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = "DELETE FROM diyet_takibi WHERE id = %s AND hasta_id = %s"
            self.db.execute_query(query, (diet_id, self.patient_id))
            self.load_diets()
            QMessageBox.information(self, "Başarılı", "Diyet silindi!") 