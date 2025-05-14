from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.blood_sugar_page import BloodSugarPage
from ui.exercise_page import ExercisePage
from ui.diet_page import DietPage
from ui.symptom_page import SymptomPage

class PatientPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
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
        
        # Kan şekeri takibi
        blood_sugar_page = BloodSugarPage(self.main_window)
        tab_widget.addTab(blood_sugar_page, "Kan Şekeri Takibi")
        
        # Egzersiz takibi
        exercise_page = ExercisePage(self.main_window)
        tab_widget.addTab(exercise_page, "Egzersiz Takibi")
        
        # Diyet takibi
        diet_page = DietPage(self.main_window)
        tab_widget.addTab(diet_page, "Diyet Takibi")
        
        # Semptom takibi
        symptom_page = SymptomPage(self.main_window)
        tab_widget.addTab(symptom_page, "Semptom Takibi")
        
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