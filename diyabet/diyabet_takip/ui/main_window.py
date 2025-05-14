from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QMessageBox,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.login_page import LoginPage
from .blood_sugar_page import BloodSugarPage
from ui.doctor_panel import DoctorPanel
from ui.patient_panel import PatientPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.current_user_type = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Diyabet Takip Sistemi")
        self.setMinimumSize(1200, 800)
        
        # Stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Sayfaları ekle
        self.login_page = LoginPage(self)
        self.stacked_widget.addWidget(self.login_page)
        
        # Başlangıçta login sayfasını göster
        self.stacked_widget.setCurrentWidget(self.login_page)
    
    def show_doctor_panel(self):
        # Önceki hasta detay sayfalarını temizle
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Doktor panelini oluştur ve ekle
        self.doctor_panel = DoctorPanel(self)
        self.stacked_widget.addWidget(self.doctor_panel)
        self.stacked_widget.setCurrentWidget(self.doctor_panel)
    
    def show_patient_panel(self):
        # Önceki sayfaları temizle
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Hasta panelini oluştur ve ekle
        self.patient_panel = PatientPanel(self)
        self.stacked_widget.addWidget(self.patient_panel)
        self.stacked_widget.setCurrentWidget(self.patient_panel)
    
    def create_menu_buttons(self):
        # Logo veya başlık
        logo_label = QLabel("Diyabet Takip")
        logo_label.setStyleSheet("color: white; font-size: 18px; padding: 20px;")
        logo_label.setAlignment(Qt.AlignCenter)
        self.menu_layout.addWidget(logo_label)
        
        # Menü butonları
        menu_buttons = [
            ("Giriş Yap", self.show_login_page),
            ("Hasta Paneli", self.show_patient_panel),
            ("Doktor Paneli", self.show_doctor_panel),
            ("Kan Şekeri Takibi", self.show_blood_sugar_tracking),
            ("Egzersiz Takibi", self.show_exercise_tracking),
            ("Diyet Takibi", self.show_diet_tracking),
            ("Belirti Takibi", self.show_symptom_tracking),
            ("Raporlar", self.show_reports),
            ("Ayarlar", self.show_settings)
        ]
        
        for text, slot in menu_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    border: none;
                    padding: 10px;
                    text-align: left;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            btn.clicked.connect(slot)
            self.menu_layout.addWidget(btn)
        
        self.menu_layout.addStretch()
    
    def show_login_page(self):
        # Giriş sayfası widget'ını oluştur ve göster
        login_page = LoginPage(self)
        self.stacked_widget.addWidget(login_page)
        self.stacked_widget.setCurrentWidget(login_page)
    
    def show_blood_sugar_tracking(self):
        blood_sugar_page = BloodSugarPage(self)
        self.stacked_widget.addWidget(blood_sugar_page)
        self.stacked_widget.setCurrentWidget(blood_sugar_page)
    
    def show_exercise_tracking(self):
        # Egzersiz takip widget'ını oluştur ve göster
        exercise_widget = QWidget()
        exercise_layout = QVBoxLayout(exercise_widget)
        
        exercise_label = QLabel("Egzersiz Takibi")
        exercise_label.setStyleSheet("font-size: 24px; margin: 20px;")
        exercise_layout.addWidget(exercise_label)
        
        self.stacked_widget.addWidget(exercise_widget)
        self.stacked_widget.setCurrentWidget(exercise_widget)
    
    def show_diet_tracking(self):
        # Diyet takip widget'ını oluştur ve göster
        diet_widget = QWidget()
        diet_layout = QVBoxLayout(diet_widget)
        
        diet_label = QLabel("Diyet Takibi")
        diet_label.setStyleSheet("font-size: 24px; margin: 20px;")
        diet_layout.addWidget(diet_label)
        
        self.stacked_widget.addWidget(diet_widget)
        self.stacked_widget.setCurrentWidget(diet_widget)
    
    def show_symptom_tracking(self):
        # Belirti takip widget'ını oluştur ve göster
        symptom_widget = QWidget()
        symptom_layout = QVBoxLayout(symptom_widget)
        
        symptom_label = QLabel("Belirti Takibi")
        symptom_label.setStyleSheet("font-size: 24px; margin: 20px;")
        symptom_layout.addWidget(symptom_label)
        
        self.stacked_widget.addWidget(symptom_widget)
        self.stacked_widget.setCurrentWidget(symptom_widget)
    
    def show_reports(self):
        # Raporlar widget'ını oluştur ve göster
        reports_widget = QWidget()
        reports_layout = QVBoxLayout(reports_widget)
        
        reports_label = QLabel("Raporlar")
        reports_label.setStyleSheet("font-size: 24px; margin: 20px;")
        reports_layout.addWidget(reports_label)
        
        self.stacked_widget.addWidget(reports_widget)
        self.stacked_widget.setCurrentWidget(reports_widget)
    
    def show_settings(self):
        # Ayarlar widget'ını oluştur ve göster
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        settings_label = QLabel("Ayarlar")
        settings_label.setStyleSheet("font-size: 24px; margin: 20px;")
        settings_layout.addWidget(settings_label)
        
        self.stacked_widget.addWidget(settings_widget)
        self.stacked_widget.setCurrentWidget(settings_widget) 