from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QFont
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class InsulinPage(QWidget):
    def __init__(self, main_window, patient_id=None, readonly=False):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.readonly = readonly
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("İnsülin Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Filtre
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        filter_layout.addWidget(self.start_date)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("Bitiş Tarihi:"))
        filter_layout.addWidget(self.end_date)
        filter_btn = QPushButton("Filtrele")
        filter_btn.clicked.connect(self.load_insulin)
        filter_layout.addWidget(filter_btn)
        layout.addLayout(filter_layout)

        # Kayıt formu
        if not self.readonly:
            form_layout = QHBoxLayout()
            self.dose_input = QLineEdit()
            self.dose_input.setPlaceholderText("Doz (ör. 3.0)")
            form_layout.addWidget(QLabel("Doz:"))
            form_layout.addWidget(self.dose_input)
            self.datetime_input = QDateEdit()
            self.datetime_input.setCalendarPopup(True)
            self.datetime_input.setDate(QDate.currentDate())
            form_layout.addWidget(QLabel("Tarih:"))
            form_layout.addWidget(self.datetime_input)
            self.notes_input = QTextEdit()
            self.notes_input.setPlaceholderText("Notlar...")
            self.notes_input.setMaximumHeight(40)
            form_layout.addWidget(QLabel("Notlar:"))
            form_layout.addWidget(self.notes_input)
            save_btn = QPushButton("Kaydet")
            save_btn.clicked.connect(self.save_insulin)
            form_layout.addWidget(save_btn)
            layout.addLayout(form_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tarih", "Doz (Ünite)", "Notlar", "İşlemler"])
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_insulin()

    def load_insulin(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        query = """
            SELECT id, uygulama_zamani, doz, notlar FROM insulin_kayitlari
            WHERE hasta_id = %s AND DATE(uygulama_zamani) BETWEEN %s AND %s
            ORDER BY uygulama_zamani DESC
        """
        results = self.db.fetch_all(query, (self.patient_id, start, end))
        self.table.setRowCount(len(results))
        for row, rec in enumerate(results):
            tarih = rec[1].strftime("%d.%m.%Y %H:%M")
            self.table.setItem(row, 0, QTableWidgetItem(tarih))
            self.table.setItem(row, 1, QTableWidgetItem(str(rec[2])))
            self.table.setItem(row, 2, QTableWidgetItem(rec[3] or ""))
            if not self.readonly:
                del_btn = QPushButton("Sil")
                del_btn.clicked.connect(lambda checked, id=rec[0]: self.delete_insulin(id))
                self.table.setCellWidget(row, 3, del_btn)
            else:
                self.table.setItem(row, 3, QTableWidgetItem("-"))

    def save_insulin(self):
        try:
            # Sadece doktorlar kayıt ekleyebilir
            user_type = getattr(self.main_window.current_user, 'kullanici_tipi', None) if hasattr(self.main_window, 'current_user') else self.main_window.current_user.get('kullanici_tipi', None)
            if user_type == 'hasta':
                QMessageBox.warning(self, "Yetkisiz İşlem", "Sadece doktorlar insülin kaydı ekleyebilir!")
                return
            doz = float(self.dose_input.text())
            tarih = self.datetime_input.date().toPyDate()
            notlar = self.notes_input.toPlainText()
            query = """
                INSERT INTO insulin_kayitlari (hasta_id, doz, uygulama_zamani, notlar)
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(query, (self.patient_id, doz, tarih, notlar))
            QMessageBox.information(self, "Başarılı", "Kayıt eklendi!")
            self.dose_input.clear()
            self.notes_input.clear()
            self.datetime_input.setDate(QDate.currentDate())
            self.load_insulin()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt eklenemedi: {str(e)}")

    def delete_insulin(self, insulin_id):
        reply = QMessageBox.question(self, "Onay", "Bu kaydı silmek istiyor musunuz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            query = "DELETE FROM insulin_kayitlari WHERE id = %s AND hasta_id = %s"
            self.db.execute_query(query, (insulin_id, self.patient_id))
            self.load_insulin()
            QMessageBox.information(self, "Başarılı", "Kayıt silindi!") 