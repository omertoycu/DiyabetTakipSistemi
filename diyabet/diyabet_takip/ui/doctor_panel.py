from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialog, QLineEdit, QDateEdit,
                             QComboBox, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os
from datetime import datetime

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection
from ui.patient_detail_page import PatientDetailPage

class AddPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Yeni Hasta Ekle")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # TC Kimlik
        self.tc_input = QLineEdit()
        self.tc_input.setMaxLength(11)
        layout.addRow("TC Kimlik:", self.tc_input)
        
        # Ad
        self.name_input = QLineEdit()
        layout.addRow("Ad:", self.name_input)
        
        # Soyad
        self.surname_input = QLineEdit()
        layout.addRow("Soyad:", self.surname_input)
        
        # E-posta
        self.email_input = QLineEdit()
        layout.addRow("E-posta:", self.email_input)
        
        # Doğum Tarihi
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate.currentDate())
        layout.addRow("Doğum Tarihi:", self.birth_date)
        
        # Cinsiyet
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Erkek", "Kadın"])
        layout.addRow("Cinsiyet:", self.gender_combo)
        
        # Şifre
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Şifre:", self.password_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
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
        save_button.clicked.connect(self.save_patient)
        
        cancel_button = QPushButton("İptal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def save_patient(self):
        try:
            tc = self.tc_input.text()
            name = self.name_input.text()
            surname = self.surname_input.text()
            email = self.email_input.text()
            birth_date = self.birth_date.date().toPyDate()
            gender = 'E' if self.gender_combo.currentText() == "Erkek" else 'K'
            password = self.password_input.text()
            
            if not all([tc, name, surname, email, password]):
                QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
                return
            
            # TC ve e-posta kontrolü
            check_query = """
                SELECT id FROM kullanicilar
                WHERE tc_kimlik = %s OR email = %s
            """
            existing_user = self.db.fetch_one(check_query, (tc, email))
            
            if existing_user:
                QMessageBox.warning(self, "Uyarı", "Bu TC Kimlik veya E-posta adresi zaten kullanılıyor!")
                return
            
            # Hasta ekle
            insert_query = """
                INSERT INTO kullanicilar (tc_kimlik, ad, soyad, email, dogum_tarihi, cinsiyet, sifre, kullanici_tipi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'hasta')
            """
            
            self.db.execute_query(insert_query, (
                tc, name, surname, email, birth_date, gender, password
            ))
            
            # Doktor-Hasta ilişkisi kur
            patient_id = self.db.fetch_one("SELECT LAST_INSERT_ID()")[0]
            doctor_id = self.parent().main_window.current_user['id']
            
            relation_query = """
                INSERT INTO doktor_hasta_iliskisi (doktor_id, hasta_id)
                VALUES (%s, %s)
            """
            
            self.db.execute_query(relation_query, (doctor_id, patient_id))
            
            QMessageBox.information(self, "Başarılı", "Hasta başarıyla eklendi!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hasta eklenirken bir hata oluştu: {str(e)}")

class DoctorPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Doktor Paneli")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Hoş geldin mesajı
        if self.main_window.current_user:
            welcome_text = f"Hoş geldiniz, Dr. {self.main_window.current_user['ad']} {self.main_window.current_user['soyad']}"
        else:
            welcome_text = "Hoş geldiniz"
        welcome_label = QLabel(welcome_text)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Yeni hasta ekle butonu
        add_patient_button = QPushButton("Yeni Hasta Ekle")
        add_patient_button.setStyleSheet("""
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
        add_patient_button.clicked.connect(self.add_patient)
        layout.addWidget(add_patient_button)
        
        # Hasta listesi
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(6)
        self.patient_table.setHorizontalHeaderLabels([
            "TC Kimlik", "Ad Soyad", "E-posta", "Son Ölçüm", "Durum", "İşlemler"
        ])
        layout.addWidget(self.patient_table)
        
        # Çıkış yap butonu
        logout_button = QPushButton("Çıkış Yap")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)
        
        self.setLayout(layout)
        self.load_patients()
    
    def add_patient(self):
        dialog = AddPatientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_patients()
    
    def load_patients(self):
        query = """
            SELECT 
                k.tc_kimlik,
                CONCAT(k.ad, ' ', k.soyad) as ad_soyad,
                k.email,
                COALESCE(MAX(ks.olcum_degeri), 0) as son_olcum,
                CASE 
                    WHEN MAX(ks.olcum_degeri) > 180 THEN 'Yüksek'
                    WHEN MAX(ks.olcum_degeri) < 70 THEN 'Düşük'
                    ELSE 'Normal'
                END as durum
            FROM kullanicilar k
            LEFT JOIN doktor_hasta_iliskisi dhi ON k.id = dhi.hasta_id
            LEFT JOIN kan_sekeri_olcumleri ks ON k.id = ks.hasta_id
            WHERE dhi.doktor_id = %s
            GROUP BY k.id, k.tc_kimlik, k.ad, k.soyad, k.email
            ORDER BY k.ad, k.soyad
        """
        
        patients = self.db.fetch_all(query, (self.main_window.current_user['id'],))
        
        self.patient_table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            # TC Kimlik
            self.patient_table.setItem(row, 0, QTableWidgetItem(patient[0]))
            
            # Ad Soyad
            self.patient_table.setItem(row, 1, QTableWidgetItem(patient[1]))
            
            # E-posta
            self.patient_table.setItem(row, 2, QTableWidgetItem(patient[2]))
            
            # Son Ölçüm
            self.patient_table.setItem(row, 3, QTableWidgetItem(str(patient[3])))
            
            # Durum
            status_item = QTableWidgetItem(patient[4])
            if patient[4] == 'Yüksek':
                status_item.setForeground(Qt.red)
            elif patient[4] == 'Düşük':
                status_item.setForeground(Qt.blue)
            else:
                status_item.setForeground(Qt.green)
            self.patient_table.setItem(row, 4, status_item)
            
            # İşlemler
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            view_button = QPushButton("Detay")
            view_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            view_button.clicked.connect(lambda checked, tc=patient[0]: self.view_patient(tc))
            
            remove_button = QPushButton("Sil")
            remove_button.setStyleSheet("""
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
            remove_button.clicked.connect(lambda checked, tc=patient[0]: self.remove_patient(tc))
            
            actions_layout.addWidget(view_button)
            actions_layout.addWidget(remove_button)
            
            self.patient_table.setCellWidget(row, 5, actions_widget)
    
    def view_patient(self, patient_tc):
        patient_detail = PatientDetailPage(self.main_window, patient_tc)
        self.main_window.stacked_widget.addWidget(patient_detail)
        self.main_window.stacked_widget.setCurrentWidget(patient_detail)
    
    def remove_patient(self, patient_tc):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu hastayı silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Önce hasta ID'sini al
                patient_query = "SELECT id FROM kullanicilar WHERE tc_kimlik = %s"
                patient_id = self.db.fetch_one(patient_query, (patient_tc,))[0]
                
                # İlişkiyi sil
                relation_query = """
                    DELETE FROM doktor_hasta_iliskisi
                    WHERE doktor_id = %s AND hasta_id = %s
                """
                self.db.execute_query(relation_query, (self.main_window.current_user['id'], patient_id))
                
                # Hastanın kayıtlarını sil
                tables = [
                    'kan_sekeri_olcumleri',
                    'egzersiz_kayitlari',
                    'diyet_kayitlari',
                    'semptom_kayitlari'
                ]
                
                for table in tables:
                    delete_query = f"DELETE FROM {table} WHERE hasta_id = %s"
                    self.db.execute_query(delete_query, (patient_id,))
                
                # Hastayı sil
                patient_delete_query = "DELETE FROM kullanicilar WHERE id = %s"
                self.db.execute_query(patient_delete_query, (patient_id,))
                
                QMessageBox.information(self, "Başarılı", "Hasta başarıyla silindi!")
                self.load_patients()
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Hasta silinirken bir hata oluştu: {str(e)}")
    
    def logout(self):
        self.main_window.current_user = None
        self.main_window.stacked_widget.setCurrentIndex(0) 