from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Diyabet Takip Sistemi")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Giriş formu
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        # TC Kimlik
        tc_layout = QHBoxLayout()
        tc_label = QLabel("TC Kimlik:")
        tc_label.setMinimumWidth(100)
        self.tc_input = QLineEdit()
        self.tc_input.setMaxLength(11)
        tc_layout.addWidget(tc_label)
        tc_layout.addWidget(self.tc_input)
        form_layout.addLayout(tc_layout)
        
        # Şifre
        password_layout = QHBoxLayout()
        password_label = QLabel("Şifre:")
        password_label.setMinimumWidth(100)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        # Kullanıcı tipi
        user_type_layout = QHBoxLayout()
        user_type_label = QLabel("Kullanıcı Tipi:")
        user_type_label.setMinimumWidth(100)
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Doktor", "Hasta"])
        user_type_layout.addWidget(user_type_label)
        user_type_layout.addWidget(self.user_type_combo)
        form_layout.addLayout(user_type_layout)
        
        # Giriş butonu
        login_button = QPushButton("Giriş Yap")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        login_button.clicked.connect(self.login)
        form_layout.addWidget(login_button)
        
        # Form container'ı ortala
        form_container.setMaximumWidth(400)
        form_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }
        """)
        
        layout.addWidget(form_container, alignment=Qt.AlignCenter)
        self.setLayout(layout)
    
    def login(self):
        tc = self.tc_input.text()
        password = self.password_input.text()
        user_type = self.user_type_combo.currentText().lower()
        
        if not tc or not password:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        try:
            query = """
                SELECT id, ad, soyad, email, dogum_tarihi, cinsiyet
                FROM kullanicilar
                WHERE tc_kimlik = %s AND sifre = %s AND kullanici_tipi = %s
            """
            
            result = self.db.fetch_one(query, (tc, password, user_type))
            
            if result:
                self.main_window.current_user = {
                    'id': result[0],
                    'ad': result[1],
                    'soyad': result[2],
                    'email': result[3],
                    'dogum_tarihi': result[4],
                    'cinsiyet': result[5],
                    'tc_kimlik': tc,
                    'kullanici_tipi': user_type
                }
                
                if user_type == 'doktor':
                    self.main_window.show_doctor_panel()
                else:
                    self.main_window.show_patient_panel()
                
                QMessageBox.information(self, "Başarılı", "Giriş başarılı!")
            else:
                QMessageBox.warning(self, "Hata", "Geçersiz TC Kimlik veya şifre!")
        
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Giriş yapılırken bir hata oluştu: {str(e)}") 