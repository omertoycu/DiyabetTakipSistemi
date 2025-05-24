from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QTableWidget,
                             QTableWidgetItem, QComboBox, QDateEdit, QDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class ExercisePage(QWidget):
    def __init__(self, main_window, patient_id=None, readonly=False):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.readonly = readonly
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Egzersiz Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Önerilen egzersizler bölümü
        recommendations_container = QWidget()
        recommendations_layout = QVBoxLayout(recommendations_container)
        
        recommendations_title = QLabel("Günün Önerilen Egzersizleri")
        recommendations_title.setFont(QFont("Arial", 14, QFont.Bold))
        recommendations_layout.addWidget(recommendations_title)
        
        self.recommendations_label = QLabel()
        self.recommendations_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #b8daff;
            }
        """)
        recommendations_layout.addWidget(self.recommendations_label)
        
        layout.addWidget(recommendations_container)
        
        # Yeni egzersiz formu
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)
        
        # Egzersiz tipi
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Yürüyüş", "Bisiklet", "Klinik Egzersiz"])
        form_layout.addWidget(QLabel("Egzersiz Tipi:"))
        form_layout.addWidget(self.type_combo)
        
        # Tarih
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.dateChanged.connect(self.on_date_changed)
        form_layout.addWidget(QLabel("Tarih:"))
        form_layout.addWidget(self.date_input)
        
        # Durum sadece doktor panelinde gösterilecek
        user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
        if user_type == 'doktor':
            self.status_combo = QComboBox()
            self.status_combo.addItems(["Yapıldı", "Yapılmadı"])
            form_layout.addWidget(QLabel("Durum:"))
            form_layout.addWidget(self.status_combo)
            

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
            save_button.clicked.connect(self.save_exercise)
            form_layout.addWidget(save_button)
        
        layout.addWidget(form_container)
        
        # Uyum grafiği butonu
        self.compliance_graph_button = QPushButton("Uyum Grafiğini Göster")
        self.compliance_graph_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2471a3;
            }
        """)
        self.compliance_graph_button.clicked.connect(self.show_compliance_graph)
        layout.addWidget(self.compliance_graph_button)
        
        # Egzersiz listesi
        self.exercise_table = QTableWidget()
        self.exercise_table.setColumnCount(5)
        self.exercise_table.setHorizontalHeaderLabels([
            "Tarih", "Egzersiz Tipi", "Durum", "Önerilen", "İşlemler"
        ])
        layout.addWidget(self.exercise_table)
        
        self.setLayout(layout)
        self.load_exercises()
        self.load_recommendations()
    
    def on_date_changed(self, qdate):
        selected_date = qdate.toPyDate()
        self.load_exercises(selected_date)
        self.load_recommendations(selected_date)
    
    def load_recommendations(self, selected_date=None):

        if selected_date is None:
            selected_date = self.date_input.date().toPyDate()
        query = """
            SELECT oneriler FROM egzersiz_onerileri WHERE hasta_id = %s AND tarih = %s
        """
        result = self.db.fetch_one(query, (self.patient_id, selected_date))
        if result and result[0]:
            self.recommendations_label.setText(result[0])
        else:
            self.recommendations_label.setText("Henüz egzersiz önerisi bulunmuyor.")
    
    def load_exercises(self, selected_date=None):

        if selected_date is None:
            selected_date = self.date_input.date().toPyDate()
        query = """
            SELECT e.tarih, e.egzersiz_tipi, e.durum, o.oneriler, e.id
            FROM egzersiz_takibi e
            LEFT JOIN egzersiz_onerileri o ON e.hasta_id = o.hasta_id AND e.tarih = o.tarih
            WHERE e.hasta_id = %s AND e.tarih = %s
            ORDER BY e.tarih DESC
        """
        exercises = self.db.fetch_all(query, (self.patient_id, selected_date))
        self.exercise_table.setRowCount(len(exercises))
        user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
        for row, exercise in enumerate(exercises):
            # Tarih
            date_str = exercise[0].strftime("%d.%m.%Y")
            self.exercise_table.setItem(row, 0, QTableWidgetItem(date_str))
            # Egzersiz tipi
            self.exercise_table.setItem(row, 1, QTableWidgetItem(exercise[1]))
            # Durum
            durum = exercise[2] if exercise[2] else "-"
            if user_type == 'hasta':
                combo = QComboBox()
                combo.addItems(["Yapıldı", "Yapılmadı"])
                if exercise[2]:
                    combo.setCurrentText(exercise[2])
                combo.currentTextChanged.connect(lambda value, ex_id=exercise[4]: self.update_exercise_status(ex_id, value))
                self.exercise_table.setCellWidget(row, 2, combo)
            else:
                status_item = QTableWidgetItem(durum if durum != "-" else "Henüz bilgi girilmedi")
                if exercise[2] == "Yapıldı":
                    status_item.setForeground(Qt.green)
                elif exercise[2] == "Yapılmadı":
                    status_item.setForeground(Qt.red)
                self.exercise_table.setItem(row, 2, status_item)
            # Önerilen
            recommendations = exercise[3] if exercise[3] else ""
            self.exercise_table.setItem(row, 3, QTableWidgetItem(recommendations))
            if user_type == 'doktor':
                delete_button = QPushButton("Sil")
                delete_button.setStyleSheet("""
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
                delete_button.clicked.connect(lambda checked, id=exercise[4]: self.delete_exercise(id))
                self.exercise_table.setCellWidget(row, 4, delete_button)
            else:
                self.exercise_table.setItem(row, 4, QTableWidgetItem("-"))
    
    def calculate_compliance(self, exercise_type, recommendations):
        if not recommendations:
            return "Belirsiz"
            
        # Egzersiz tipine göre uyum hesaplama
        if exercise_type == "Yürüyüş" and any("yürüyüş" in r.lower() for r in recommendations):
            return "Yüksek"
        elif exercise_type == "Klinik Egzersiz" and any("klinik" in r.lower() for r in recommendations):
            return "Yüksek"
        elif exercise_type in ["Yürüyüş", "Bisiklet"] and any("egzersiz" in r.lower() for r in recommendations):
            return "Orta"
        else:
            return "Düşük"
    
    def save_exercise(self):
        try:
            exercise_type = self.type_combo.currentText()
            date = self.date_input.date().toPyDate()
            user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
            if user_type == 'doktor':
                status = "Yapılmadı"  # Doktor için varsayılan durum
            else:
                status = self.status_combo.currentText()
            query = """
                INSERT INTO egzersiz_takibi (hasta_id, egzersiz_tipi, tarih, durum)
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(query, (
                self.patient_id,
                exercise_type,
                date,
                status
            ))
            # Kayıttan sonra öneriyi güncelle
            self.load_recommendations()
            QMessageBox.information(self, "Başarılı", "Egzersiz kaydedildi!")
            self.load_exercises()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Egzersiz kaydedilirken bir hata oluştu: {str(e)}")
    
    def get_recommended_exercise(self):
        # En son genel kan şekeri ve semptom verilerini al
        query = """
            SELECT deger, tarih FROM genel_kan_sekeri WHERE hasta_id = %s ORDER BY tarih DESC LIMIT 1
        """
        result = self.db.fetch_one(query, (self.patient_id,))
        if not result:
            return "Genel kan şekeri kaydı bulunamadı."
        genel_blood_sugar, tarih = result
        # O tarihteki semptomları al (sadece gün bazında karşılaştır)
        symptoms_query = """
            SELECT semptom FROM semptom_takibi WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        symptoms_result = self.db.fetch_all(symptoms_query, (self.patient_id, tarih.date() if hasattr(tarih, 'date') else tarih))
        symptoms = [s[0] for s in symptoms_result]
        def normalize(s):
            return s.strip().lower()
        norm_symptoms = set([normalize(s) for s in symptoms])

        if genel_blood_sugar < 70 and set(map(normalize, ["Nöropati", "Polifaji", "Yorgunluk"])).issubset(norm_symptoms):
            return "Yok"
        elif genel_blood_sugar < 70 and set(map(normalize, ["Yorgunluk", "Kilo Kaybı"])).issubset(norm_symptoms):
            return "Yürüyüş"
        elif 70 <= genel_blood_sugar <= 110 and set(map(normalize, ["Polifaji", "Polidipsi"])).issubset(norm_symptoms):
            return "Yürüyüş"
        elif 70 <= genel_blood_sugar <= 110 and set(map(normalize, ["Bulanık Görme", "Nöropati"])).issubset(norm_symptoms):
            return "Klinik Egzersiz"
        elif 110 < genel_blood_sugar < 180 and set(map(normalize, ["Poliüri", "Polidipsi"])).issubset(norm_symptoms):
            return "Klinik Egzersiz"
        elif 110 < genel_blood_sugar < 180 and set(map(normalize, ["Yorgunluk", "Nöropati", "Bulanık Görme"])).issubset(norm_symptoms):
            return "Yürüyüş"
        elif genel_blood_sugar >= 180 and set(map(normalize, ["Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"])).issubset(norm_symptoms):
            return "Klinik Egzersiz"
        elif genel_blood_sugar >= 180 and set(map(normalize, ["Yaraların Yavaş İyileşmesi", "Kilo Kaybı"])).issubset(norm_symptoms):
            return "Yürüyüş"
        else:
            return "Uygun semptomlar girilmediği için öneri üretilemedi. Lütfen semptomları ve genel kan şekeri değerini aynı gün için girin."
    
    def delete_exercise(self, exercise_id):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu egzersizi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = "DELETE FROM egzersiz_takibi WHERE id = %s AND hasta_id = %s"
            self.db.execute_query(query, (exercise_id, self.patient_id))
            self.load_exercises()
            QMessageBox.information(self, "Başarılı", "Egzersiz silindi!")
    
    def update_exercise_status(self, exercise_id, new_status):
        try:
            query = """
                UPDATE egzersiz_takibi SET durum = %s WHERE id = %s AND hasta_id = %s
            """
            self.db.execute_query(query, (new_status, exercise_id, self.patient_id))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Durum güncellenirken bir hata oluştu: {str(e)}")
    
    def show_compliance_graph(self):
        # Egzersiz uyumunu yüzde olarak hesapla
        query = """
            SELECT durum FROM egzersiz_takibi WHERE hasta_id = %s
        """
        results = self.db.fetch_all(query, (self.patient_id,))
        if not results:
            QMessageBox.information(self, "Bilgi", "Grafik için yeterli veri yok.")
            return
        total = len(results)
        done = sum(1 for r in results if r[0] == "Yapıldı")
        not_done = total - done
        labels = ["Yapıldı", "Yapılmadı"]
        sizes = [done, not_done]
        colors = ["#27ae60", "#e74c3c"]
        # Grafik penceresi oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("Egzersiz Uyum Yüzdesi")
        layout = QVBoxLayout(dialog)
        fig = Figure(figsize=(6,6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title("Egzersiz Uyum Yüzdesi")
        ax.axis('equal')
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.exec_() 