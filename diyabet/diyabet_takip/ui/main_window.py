from PyQt5.QtWidgets import (QMainWindow, QStackedWidget)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.login_page import LoginPage
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
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_page = LoginPage(self)
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.setCurrentWidget(self.login_page)
    
    def show_doctor_panel(self):
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        self.doctor_panel = DoctorPanel(self)
        self.stacked_widget.addWidget(self.doctor_panel)
        self.stacked_widget.setCurrentWidget(self.doctor_panel)
    
    def show_patient_panel(self):
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        self.patient_panel = PatientPanel(self)
        self.stacked_widget.addWidget(self.patient_panel)
        self.stacked_widget.setCurrentWidget(self.patient_panel) 