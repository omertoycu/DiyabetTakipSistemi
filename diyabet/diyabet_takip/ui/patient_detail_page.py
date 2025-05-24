from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection
from ui.blood_sugar_page import BloodSugarPage
from ui.exercise_page import ExercisePage
from ui.diet_page import DietPage
from ui.symptom_page import SymptomPage
from ui.insulin_page import InsulinPage
from ui.genel_blood_sugar_page import GenelBloodSugarPage
from ui.statistics_page import StatisticsPage

class PatientDetailPage(QWidget):
    def __init__(self, main_window, patient_tc):
        super().__init__()
        self.main_window = main_window
        self.patient_tc = patient_tc
        self.db = DatabaseConnection()
        self.patient_info = self.load_patient_info()
        self.init_ui()
    
    def load_patient_info(self):
        query = """
            SELECT id, ad, soyad, email, dogum_tarihi, cinsiyet
            FROM kullanicilar
            WHERE tc_kimlik = %s AND kullanici_tipi = 'hasta'
        """
        
        result = self.db.fetch_one(query, (self.patient_tc,))
        if not result:
            QMessageBox.critical(self, "Hata", "Hasta bulunamadı!")
            return None
        
        return {
            'id': result[0],
            'ad': result[1],
            'soyad': result[2],
            'email': result[3],
            'dogum_tarihi': result[4],
            'cinsiyet': result[5]
        }
    
    def init_ui(self):
        if not self.patient_info:
            QMessageBox.critical(self, "Hata", "Hasta bilgileri yüklenemedi!")
            self.main_window.show_doctor_panel()
            return
        
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel(f"Hasta Detayları: {self.patient_info['ad']} {self.patient_info['soyad']}")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Hasta bilgileri
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        
        info_text = f"""
        TC Kimlik: {self.patient_tc}
        E-posta: {self.patient_info['email']}
        Doğum Tarihi: {self.patient_info['dogum_tarihi'].strftime('%d.%m.%Y')}
        Cinsiyet: {'Erkek' if self.patient_info['cinsiyet'] == 'E' else 'Kadın'}
        """
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
        """)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_container)
        

        tab_widget = QTabWidget()
        
        # Genel Kan Şekeri sekmesi (doktor için)
        genel_blood_sugar_page = GenelBloodSugarPage(self.main_window, self.patient_info['id'], readonly=False)
        tab_widget.addTab(genel_blood_sugar_page, "Genel Kan Şekeri")
        
        # Kan şekeri takibi
        blood_sugar_page = BloodSugarPage(self.main_window, self.patient_info['id'])
        if hasattr(blood_sugar_page, 'date_input'):
            blood_sugar_page.date_input.dateChanged.connect(lambda qdate: [blood_sugar_page.load_measurements(qdate.toPyDate()), blood_sugar_page.update_daily_average(qdate.toPyDate())])
        tab_widget.addTab(blood_sugar_page, "Kan Şekeri Takibi")
        
        # Egzersiz takibi
        exercise_page = ExercisePage(self.main_window, self.patient_info['id'], readonly=True)
        tab_widget.addTab(exercise_page, "Egzersiz Takibi")
        
        # Diyet takibi
        diet_page = DietPage(self.main_window, self.patient_info['id'], readonly=True)
        tab_widget.addTab(diet_page, "Diyet Takibi")
        
        # Semptom takibi
        symptom_page = SymptomPage(self.main_window, self.patient_info['id'])
        tab_widget.addTab(symptom_page, "Semptom Takibi")
        
        # İnsülin takibi
        insulin_page = InsulinPage(self.main_window, self.patient_info['id'], readonly=False)
        tab_widget.addTab(insulin_page, "İnsülin Takibi")
        
        # İstatistikler sekmesi
        statistics_page = StatisticsPage(self.main_window, self.patient_info['id'])
        tab_widget.addTab(statistics_page, "İstatistikler")
        
        layout.addWidget(tab_widget)
        
        # Geri dön butonu
        back_button = QPushButton("Geri Dön")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)
        
        self.setLayout(layout)
    
    def go_back(self):
        self.main_window.show_doctor_panel() 