from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QFont
from datetime import datetime
import sys
import os
import pytz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class InsulinPage(QWidget):
    def __init__(self, main_window, patient_id=None, readonly=False):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.readonly = readonly

        self.user_type = main_window.current_user.get('kullanici_tipi', 'hasta')

        if self.user_type == 'hasta':
            self.readonly = True
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("İnsülin Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)


        if self.user_type == 'hasta':
            info_label = QLabel("ℹ️ İnsülin kayıtlarını sadece doktorunuz ekleyebilir. Burada kayıtlarınızı görüntüleyebilirsiniz.")
            info_label.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 5px; color: #1565c0;")
            layout.addWidget(info_label)


        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Gün Seç:"))
        self.selected_date = QDateEdit()
        self.selected_date.setCalendarPopup(True)
        self.selected_date.setDate(QDate.currentDate())
        self.selected_date.dateChanged.connect(self.load_insulin)
        date_row.addWidget(self.selected_date)
        layout.addLayout(date_row)

        # Kayıt formu (sadece doktorlar için)
        if self.user_type == 'doktor' and not self.readonly:
            form_layout = QHBoxLayout()
            self.dose_input = QLineEdit()
            self.dose_input.setPlaceholderText("Doz (ör. 3.0)")
            form_layout.addWidget(QLabel("Doz:"))
            form_layout.addWidget(self.dose_input)
            self.notes_input = QTextEdit()
            self.notes_input.setPlaceholderText("Notlar...")
            self.notes_input.setMaximumHeight(40)
            form_layout.addWidget(QLabel("Notlar:"))
            form_layout.addWidget(self.notes_input)
            save_btn = QPushButton("Kaydet")
            save_btn.setStyleSheet("""
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
            save_btn.clicked.connect(self.save_insulin)
            form_layout.addWidget(save_btn)
            layout.addLayout(form_layout)

        # Tablo
        self.table = QTableWidget()
        # Doktor ise "İşlemler" sütunu da var, hasta ise sadece görüntüleme
        column_count = 4 if self.user_type == 'doktor' and not self.readonly else 3
        self.table.setColumnCount(column_count)
        
        headers = ["Tarih/Saat", "Doz (Ünite)", "Notlar"]
        if self.user_type == 'doktor' and not self.readonly:
            headers.append("İşlemler")
        
        self.table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_insulin()

    def load_insulin(self):
        selected = self.selected_date.date().toPyDate()
        query = """
            SELECT id, uygulama_zamani, doz, notlar FROM insulin_kayitlari
            WHERE hasta_id = %s AND DATE(uygulama_zamani) = %s
            ORDER BY uygulama_zamani DESC
        """
        results = self.db.fetch_all(query, (self.patient_id, selected))
        self.table.setRowCount(len(results))
        for row, rec in enumerate(results):
            tarih = rec[1].strftime("%d.%m.%Y %H:%M")
            self.table.setItem(row, 0, QTableWidgetItem(tarih))
            self.table.setItem(row, 1, QTableWidgetItem(str(rec[2])))
            self.table.setItem(row, 2, QTableWidgetItem(rec[3] or ""))
            
            # Sadece doktorlar kayıt silebilir
            if self.user_type == 'doktor' and not self.readonly:
                del_btn = QPushButton("Sil")
                del_btn.setStyleSheet("""
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
                del_btn.clicked.connect(lambda checked, id=rec[0]: self.delete_insulin(id))
                self.table.setCellWidget(row, 3, del_btn)

    def save_insulin(self):
        try:
            # Çift güvenlik kontrolü
            if self.user_type != 'doktor':
                QMessageBox.warning(self, "Yetkisiz İşlem", "Sadece doktorlar insülin kaydı ekleyebilir!")
                return
            
            if not self.dose_input.text().strip():
                QMessageBox.warning(self, "Uyarı", "Lütfen doz değeri girin!")
                return
                
            doz = float(self.dose_input.text())
            
            # Doz değeri kontrolü
            if doz <= 0 or doz > 100:
                QMessageBox.warning(self, "Uyarı", "Doz değeri 0 ile 100 arasında olmalıdır!")
                return
            
            notlar = self.notes_input.toPlainText()
            

            turkey_tz = pytz.timezone('Europe/Istanbul')
            

            tarih = self.selected_date.date().toPyDate()
            saat = datetime.now().time()
            datetime_obj = datetime.combine(tarih, saat)
            datetime_obj = turkey_tz.localize(datetime_obj)
            
            query = """
                INSERT INTO insulin_kayitlari (hasta_id, doz, uygulama_zamani, notlar)
                VALUES (%s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (self.patient_id, doz, datetime_obj, notlar))
            QMessageBox.information(self, "Başarılı", "İnsülin kaydı eklendi!")
            self.dose_input.clear()
            self.notes_input.clear()
            self.selected_date.setDate(QDate.currentDate())
            self.load_insulin()
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir sayısal doz değeri girin!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt eklenemedi: {str(e)}")

    def delete_insulin(self, insulin_id):

        if self.user_type != 'doktor':
            QMessageBox.warning(self, "Yetkisiz İşlem", "Sadece doktorlar insülin kaydı silebilir!")
            return
            
        reply = QMessageBox.question(self, "Onay", "Bu insülin kaydını silmek istediğinizden emin misiniz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM insulin_kayitlari WHERE id = %s AND hasta_id = %s"
                self.db.execute_query(query, (insulin_id, self.patient_id))
                self.load_insulin()
                QMessageBox.information(self, "Başarılı", "İnsülin kaydı silindi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kayıt silinemedi: {str(e)}") 