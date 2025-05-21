from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.blood_sugar_page import BloodSugarPage
from ui.exercise_page import ExercisePage
from ui.diet_page import DietPage
from ui.symptom_page import SymptomPage
from ui.insulin_page import InsulinPage
from ui.genel_blood_sugar_page import GenelBloodSugarPage

class PatientPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Profil resmi ve buton
        profile_row = QHBoxLayout()
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(80, 80)
        self.profile_pic_label.setStyleSheet("border: 2px solid #2980b9; border-radius: 40px; background: #f0f0f0;")
        self.load_profile_pic()
        profile_row.addWidget(self.profile_pic_label)
        profile_btn = QPushButton("Profil Resmi Ekle/Güncelle")
        profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2471a3;
            }
        """)
        profile_btn.clicked.connect(self.change_profile_pic)
        profile_row.addWidget(profile_btn)
        profile_row.addStretch()
        layout.addLayout(profile_row)
        
        # Başlık
        title = QLabel("Hasta Paneli")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Hoş geldin mesajı
        welcome_text = f"Hoş geldiniz, {self.main_window.current_user['ad']} {self.main_window.current_user['soyad']}"
        welcome_label = QLabel(welcome_text)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Genel Kan Şekeri sekmesi (sadece görüntüleme)
        self.genel_blood_sugar_page = GenelBloodSugarPage(self.main_window, readonly=True)
        tab_widget.addTab(self.genel_blood_sugar_page, "Genel Kan Şekeri")
        
        # Kan şekeri takibi
        self.blood_sugar_page = BloodSugarPage(self.main_window)
        tab_widget.addTab(self.blood_sugar_page, "Kan Şekeri Takibi")
        
        # Egzersiz takibi
        self.exercise_page = ExercisePage(self.main_window)
        tab_widget.addTab(self.exercise_page, "Egzersiz Takibi")
        
        # Diyet takibi
        self.diet_page = DietPage(self.main_window)
        tab_widget.addTab(self.diet_page, "Diyet Takibi")
        
        # Semptom takibi
        self.symptom_page = SymptomPage(self.main_window)
        tab_widget.addTab(self.symptom_page, "Semptom Takibi")
        
        # İnsülin takibi
        self.insulin_page = InsulinPage(self.main_window)
        tab_widget.addTab(self.insulin_page, "İnsülin Takibi")
        
        layout.addWidget(tab_widget)
        
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
    
    def logout(self):
        self.main_window.current_user = None
        self.main_window.stacked_widget.setCurrentIndex(0)
    
    def load_profile_pic(self):
        user_id = self.main_window.current_user['id']
        from database.db_connection import DatabaseConnection
        db = DatabaseConnection()
        query = "SELECT profil_resmi FROM kullanicilar WHERE id = %s"
        result = db.fetch_one(query, (user_id,))
        if result and result[0]:
            path = result[0]
            if path.startswith('http'):
                from urllib.request import urlopen
                from PyQt5.QtCore import QByteArray
                try:
                    data = urlopen(path).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(data))
                    self.set_rounded_pixmap(pixmap)
                except Exception:
                    self.profile_pic_label.setText("Resim yüklenemedi")
            else:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.set_rounded_pixmap(pixmap)
                else:
                    self.profile_pic_label.setText("Resim yok")
        else:
            self.profile_pic_label.setText("Resim yok")
    
    def set_rounded_pixmap(self, pixmap, size=80):
        # Kare crop ve dairesel maske uygula
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        self.profile_pic_label.setPixmap(rounded)
    
    def change_profile_pic(self):
        choice, ok = QInputDialog.getItem(self, "Profil Resmi", "Resim ekleme yöntemi seçin:", ["Bilgisayardan Yükle", "URL Gir"], 0, False)
        if not ok:
            return
        if choice == "Bilgisayardan Yükle":
            file_path, _ = QFileDialog.getOpenFileName(self, "Profil Resmi Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                self.save_profile_pic(file_path)
        else:
            url, ok = QInputDialog.getText(self, "Profil Resmi URL", "Resim URL'si girin:")
            if ok and url:
                self.save_profile_pic(url)
    
    def save_profile_pic(self, path):
        user_id = self.main_window.current_user['id']
        from database.db_connection import DatabaseConnection
        db = DatabaseConnection()
        query = "UPDATE kullanicilar SET profil_resmi = %s WHERE id = %s"
        db.execute_query(query, (path, user_id))
        self.load_profile_pic() 