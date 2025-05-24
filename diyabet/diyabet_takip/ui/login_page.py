from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QComboBox,
                             QStackedWidget, QDateEdit, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os
import bcrypt
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseConnection()
        self.init_ui()
    
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Diyabet Takip Sistemi")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.stacked_widget = QStackedWidget()

        login_container = QWidget()
        login_layout = QVBoxLayout(login_container)
        login_layout.setSpacing(20)
        
        # TC Kimlik
        tc_layout = QHBoxLayout()
        tc_label = QLabel("TC Kimlik:")
        tc_label.setMinimumWidth(100)
        self.tc_input = QLineEdit()
        self.tc_input.setMaxLength(11)
        tc_layout.addWidget(tc_label)
        tc_layout.addWidget(self.tc_input)
        login_layout.addLayout(tc_layout)
        
        # Şifre
        password_layout = QHBoxLayout()
        password_label = QLabel("Şifre:")
        password_label.setMinimumWidth(100)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)
        
        # Kullanıcı tipi
        user_type_layout = QHBoxLayout()
        user_type_label = QLabel("Kullanıcı Tipi:")
        user_type_label.setMinimumWidth(100)
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Doktor", "Hasta"])
        user_type_layout.addWidget(user_type_label)
        user_type_layout.addWidget(self.user_type_combo)
        login_layout.addLayout(user_type_layout)
        
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
        login_layout.addWidget(login_button)
        
        # Kayıt ol butonu
        register_button = QPushButton("Doktor Kaydı Oluştur")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        register_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        login_layout.addWidget(register_button)
        
        # Register form
        register_container = QWidget()
        register_layout = QVBoxLayout(register_container)
        register_layout.setSpacing(20)
        
        # TC Kimlik
        reg_tc_layout = QHBoxLayout()
        reg_tc_label = QLabel("TC Kimlik:")
        reg_tc_label.setMinimumWidth(100)
        self.reg_tc_input = QLineEdit()
        self.reg_tc_input.setMaxLength(11)
        reg_tc_layout.addWidget(reg_tc_label)
        reg_tc_layout.addWidget(self.reg_tc_input)
        register_layout.addLayout(reg_tc_layout)
        
        # Ad
        reg_ad_layout = QHBoxLayout()
        reg_ad_label = QLabel("Ad:")
        reg_ad_label.setMinimumWidth(100)
        self.reg_ad_input = QLineEdit()
        reg_ad_layout.addWidget(reg_ad_label)
        reg_ad_layout.addWidget(self.reg_ad_input)
        register_layout.addLayout(reg_ad_layout)
        
        # Soyad
        reg_soyad_layout = QHBoxLayout()
        reg_soyad_label = QLabel("Soyad:")
        reg_soyad_label.setMinimumWidth(100)
        self.reg_soyad_input = QLineEdit()
        reg_soyad_layout.addWidget(reg_soyad_label)
        reg_soyad_layout.addWidget(self.reg_soyad_input)
        register_layout.addLayout(reg_soyad_layout)
        
        # Email
        reg_email_layout = QHBoxLayout()
        reg_email_label = QLabel("Email:")
        reg_email_label.setMinimumWidth(100)
        self.reg_email_input = QLineEdit()
        reg_email_layout.addWidget(reg_email_label)
        reg_email_layout.addWidget(self.reg_email_input)
        register_layout.addLayout(reg_email_layout)
        
        # Şifre
        reg_password_layout = QHBoxLayout()
        reg_password_label = QLabel("Şifre:")
        reg_password_label.setMinimumWidth(100)
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        reg_password_layout.addWidget(reg_password_label)
        reg_password_layout.addWidget(self.reg_password_input)
        register_layout.addLayout(reg_password_layout)
        
        # Doğum Tarihi
        reg_dogum_layout = QHBoxLayout()
        reg_dogum_label = QLabel("Doğum Tarihi:")
        reg_dogum_label.setMinimumWidth(100)
        self.reg_dogum_input = QDateEdit()
        self.reg_dogum_input.setCalendarPopup(True)
        self.reg_dogum_input.setDate(QDate.currentDate())
        reg_dogum_layout.addWidget(reg_dogum_label)
        reg_dogum_layout.addWidget(self.reg_dogum_input)
        register_layout.addLayout(reg_dogum_layout)
        
        # Cinsiyet
        reg_cinsiyet_layout = QHBoxLayout()
        reg_cinsiyet_label = QLabel("Cinsiyet:")
        reg_cinsiyet_label.setMinimumWidth(100)
        self.reg_cinsiyet_group = QButtonGroup()
        self.reg_cinsiyet_erkek = QRadioButton("Erkek")
        self.reg_cinsiyet_kadin = QRadioButton("Kadın")
        self.reg_cinsiyet_group.addButton(self.reg_cinsiyet_erkek)
        self.reg_cinsiyet_group.addButton(self.reg_cinsiyet_kadin)
        reg_cinsiyet_layout.addWidget(reg_cinsiyet_label)
        reg_cinsiyet_layout.addWidget(self.reg_cinsiyet_erkek)
        reg_cinsiyet_layout.addWidget(self.reg_cinsiyet_kadin)
        register_layout.addLayout(reg_cinsiyet_layout)
        
        # Kayıt butonu
        register_submit_button = QPushButton("Kayıt Ol")
        register_submit_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        register_submit_button.clicked.connect(self.register_doctor)
        register_layout.addWidget(register_submit_button)
        
        # Geri dön butonu
        back_button = QPushButton("Giriş Ekranına Dön")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        register_layout.addWidget(back_button)
        
        # Add forms to stacked widget
        self.stacked_widget.addWidget(login_container)
        self.stacked_widget.addWidget(register_container)
        
        # Style containers
        for container in [login_container, register_container]:
            container.setMaximumWidth(400)
            container.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #dee2e6;
                }
            """)
        
        layout.addWidget(self.stacked_widget, alignment=Qt.AlignCenter)
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
                SELECT id, ad, soyad, email, dogum_tarihi, cinsiyet, sifre
                FROM kullanicilar
                WHERE tc_kimlik = %s AND kullanici_tipi = %s
            """
            
            result = self.db.fetch_one(query, (tc, user_type))
            
            if result and self.check_password(password, result[6].encode('utf-8')):
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
    
    def validate_tc(self, tc):
        if not tc.isdigit() or len(tc) != 11:
            return False
        return True
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password(self, password):
        """Şifre doğrulama"""
        if len(password) < 6:
            return False
        return True
    
    def validate_name(self, name):
        if not name.strip() or len(name.strip()) < 2:
            return False
        return True
    
    def register_doctor(self):
        try:

            tc = self.reg_tc_input.text().strip()
            name = self.reg_ad_input.text().strip()
            surname = self.reg_soyad_input.text().strip()
            email = self.reg_email_input.text().strip()
            password = self.reg_password_input.text()
            birth_date = self.reg_dogum_input.date().toPyDate()
            gender = 'E' if self.reg_cinsiyet_erkek.isChecked() else 'K'
            
            # Boş alan kontrolü
            if not all([tc, name, surname, email, password]):
                QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
                return
            
            # TC Kimlik kontrolü
            if not self.validate_tc(tc):
                QMessageBox.warning(self, "Uyarı", "Geçersiz TC Kimlik numarası! 11 haneli sayısal değer giriniz.")
                return
            
            # İsim kontrolü
            if not self.validate_name(name):
                QMessageBox.warning(self, "Uyarı", "Geçersiz isim! En az 2 karakter olmalıdır.")
                return
            
            # Soyisim kontrolü
            if not self.validate_name(surname):
                QMessageBox.warning(self, "Uyarı", "Geçersiz soyisim! En az 2 karakter olmalıdır.")
                return
            
            # E-posta kontrolü
            if not self.validate_email(email):
                QMessageBox.warning(self, "Uyarı", "Geçersiz e-posta adresi!")
                return
            
            # Şifre kontrolü
            if not self.validate_password(password):
                QMessageBox.warning(self, "Uyarı", "Şifre en az 6 karakter olmalıdır!")
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
            
            # Şifreyi hashle
            hashed_password = self.hash_password(password)
            
            # Doktor ekle
            insert_query = """
                INSERT INTO kullanicilar (tc_kimlik, ad, soyad, email, dogum_tarihi, cinsiyet, sifre, kullanici_tipi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'doktor')
            """
            
            self.db.execute_query(insert_query, (
                tc, name, surname, email, birth_date, gender, hashed_password.decode('utf-8')
            ))
            
            QMessageBox.information(self, "Başarılı", "Doktor kaydı başarıyla oluşturuldu!")
            self.stacked_widget.setCurrentIndex(0)  # Login sayfasına dön
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt sırasında bir hata oluştu: {str(e)}") 