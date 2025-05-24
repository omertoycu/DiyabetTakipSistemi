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

class DietPage(QWidget):
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
        title = QLabel("Diyet Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Önerilen diyetler bölümü
        recommendations_container = QWidget()
        recommendations_layout = QVBoxLayout(recommendations_container)
        
        recommendations_title = QLabel("Günün Önerilen Diyet Planı")
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
        
        # Yeni diyet formu
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)
        
        # Öğün tipi
        self.meal_combo = QComboBox()
        self.meal_combo.addItems(["Kahvaltı", "Öğle Yemeği", "İkindi", "Akşam Yemeği", "Gece"])
        form_layout.addWidget(QLabel("Öğün:"))
        form_layout.addWidget(self.meal_combo)
        
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
            self.status_combo.addItems(["Uygulandı", "Uygulanmadı"])
            form_layout.addWidget(QLabel("Durum:"))
            form_layout.addWidget(self.status_combo)
            
            # Kaydet butonu sadece doktor için
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
            save_button.clicked.connect(self.save_diet)
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
        
        # Diyet listesi
        self.diet_table = QTableWidget()
        self.diet_table.setColumnCount(5)
        self.diet_table.setHorizontalHeaderLabels([
            "Tarih", "Öğün", "Durum", "Önerilen", "İşlemler"
        ])
        layout.addWidget(self.diet_table)
        
        self.setLayout(layout)
        self.load_diets()
        self.load_recommendations()
    
    def on_date_changed(self, qdate):
        selected_date = qdate.toPyDate()
        self.load_diets(selected_date)
        self.load_recommendations(selected_date)
    
    def load_recommendations(self, selected_date=None):
        # Seçili tarihi kullan
        if selected_date is None:
            selected_date = self.date_input.date().toPyDate()
        query = """
            SELECT oneriler FROM diyet_onerileri WHERE hasta_id = %s AND tarih = %s
        """
        result = self.db.fetch_one(query, (self.patient_id, selected_date))
        if result and result[0]:
            self.recommendations_label.setText(result[0])
        else:
            self.recommendations_label.setText("Henüz diyet önerisi bulunmuyor.")
    
    def load_diets(self, selected_date=None):
        # Seçili tarihi kullan
        if selected_date is None:
            selected_date = self.date_input.date().toPyDate()
        query = """
            SELECT d.tarih, d.ogun, d.durum, o.oneriler, d.id
            FROM diyet_takibi d
            LEFT JOIN diyet_onerileri o ON d.hasta_id = o.hasta_id AND d.tarih = o.tarih
            WHERE d.hasta_id = %s AND d.tarih = %s
            ORDER BY d.tarih DESC, FIELD(d.ogun, 'Kahvaltı', 'Öğle Yemeği', 'İkindi', 'Akşam Yemeği', 'Gece')
        """
        diets = self.db.fetch_all(query, (self.patient_id, selected_date))
        self.diet_table.setRowCount(len(diets))
        user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
        for row, diet in enumerate(diets):
            # Tarih
            date_str = diet[0].strftime("%d.%m.%Y")
            self.diet_table.setItem(row, 0, QTableWidgetItem(date_str))
            # Öğün
            self.diet_table.setItem(row, 1, QTableWidgetItem(diet[1]))
            # Durum
            durum = diet[2] if diet[2] else "-"
            if user_type == 'hasta':
                combo = QComboBox()
                combo.addItems(["Uygulandı", "Uygulanmadı"])
                if diet[2]:
                    combo.setCurrentText(diet[2])
                combo.currentTextChanged.connect(lambda value, diet_id=diet[4]: self.update_diet_status(diet_id, value))
                self.diet_table.setCellWidget(row, 2, combo)
            else:
                status_item = QTableWidgetItem(durum if durum != "-" else "Henüz bilgi girilmedi")
                if diet[2] == "Uygulandı":
                    status_item.setForeground(Qt.green)
                elif diet[2] == "Uygulanmadı":
                    status_item.setForeground(Qt.red)
                self.diet_table.setItem(row, 2, status_item)
            # Önerilen
            recommendations = diet[3] if diet[3] else ""
            self.diet_table.setItem(row, 3, QTableWidgetItem(recommendations))
            # Silme butonu sadece doktor için
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
                delete_button.clicked.connect(lambda checked, id=diet[4]: self.delete_diet(id))
                self.diet_table.setCellWidget(row, 4, delete_button)
            else:
                self.diet_table.setItem(row, 4, QTableWidgetItem("-"))
    
    def calculate_compliance(self, meal_type, recommendations):
        if not recommendations:
            return "Belirsiz"
            
        # Öğün tipine göre uyum hesaplama
        meal_keywords = {
            "Kahvaltı": ["kahvaltı", "sabah", "protein"],
            "Öğle Yemeği": ["öğle", "ana öğün", "protein"],
            "İkindi": ["ikindi", "ara öğün", "meyve"],
            "Akşam Yemeği": ["akşam", "ana öğün", "protein"],
            "Gece": ["gece", "ara öğün", "süt"]
        }
        
        keywords = meal_keywords.get(meal_type, [])
        matches = sum(1 for r in recommendations if any(k in r.lower() for k in keywords))
        
        if matches >= 2:
            return "Yüksek"
        elif matches == 1:
            return "Orta"
        else:
            return "Düşük"
    
    def save_diet(self):
        try:
            meal_type = self.meal_combo.currentText()
            date = self.date_input.date().toPyDate()
            user_type = self.main_window.current_user.get('kullanici_tipi', 'hasta')
            if user_type == 'doktor':
                status = "Uygulanmadı"  # Doktor için varsayılan durum
            else:
                status = self.status_combo.currentText()
            query = """
                INSERT INTO diyet_takibi (hasta_id, ogun, tarih, durum)
                VALUES (%s, %s, %s, %s)
            """
            self.db.execute_query(query, (
                self.patient_id,
                meal_type,
                date,
                status
            ))
            # Kayıttan sonra öneriyi güncelle
            self.load_recommendations()
            QMessageBox.information(self, "Başarılı", "Diyet kaydedildi!")
            self.load_diets()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Diyet kaydedilirken bir hata oluştu: {str(e)}")
    
    def delete_diet(self, diet_id):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu diyeti silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = "DELETE FROM diyet_takibi WHERE id = %s AND hasta_id = %s"
            self.db.execute_query(query, (diet_id, self.patient_id))
            self.load_diets()
            QMessageBox.information(self, "Başarılı", "Diyet silindi!")
    
    def update_diet_status(self, diet_id, new_status):
        try:
            query = """
                UPDATE diyet_takibi SET durum = %s WHERE id = %s AND hasta_id = %s
            """
            self.db.execute_query(query, (new_status, diet_id, self.patient_id))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Durum güncellenirken bir hata oluştu: {str(e)}")
    
    def show_compliance_graph(self):
        # Diyet uyumunu yüzde olarak hesapla
        query = """
            SELECT durum FROM diyet_takibi WHERE hasta_id = %s
        """
        results = self.db.fetch_all(query, (self.patient_id,))
        if not results:
            QMessageBox.information(self, "Bilgi", "Grafik için yeterli veri yok.")
            return
        total = len(results)
        applied = sum(1 for r in results if r[0] == "Uygulandı")
        not_applied = total - applied
        labels = ["Uygulandı", "Uygulanmadı"]
        sizes = [applied, not_applied]
        colors = ["#27ae60", "#e74c3c"]
        # Grafik penceresi oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("Diyet Uyum Yüzdesi")
        layout = QVBoxLayout(dialog)
        fig = Figure(figsize=(6,6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title("Diyet Uyum Yüzdesi")
        ax.axis('equal')
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def get_recommended_diet(self):
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
        # Tabloya göre öneri
        if genel_blood_sugar < 70 and set(map(normalize, ["Nöropati", "Polifaji", "Yorgunluk"])).issubset(norm_symptoms):
            return "Dengeli Beslenme"
        elif genel_blood_sugar < 70 and set(map(normalize, ["Yorgunluk", "Kilo Kaybı"])).issubset(norm_symptoms):
            return "Az Şekerli Diyet"
        elif 70 <= genel_blood_sugar <= 110 and set(map(normalize, ["Polifaji", "Polidipsi"])).issubset(norm_symptoms):
            return "Dengeli Beslenme"
        elif 70 <= genel_blood_sugar <= 110 and set(map(normalize, ["Bulanık Görme", "Nöropati"])).issubset(norm_symptoms):
            return "Az Şekerli Diyet"
        elif 110 < genel_blood_sugar < 180 and set(map(normalize, ["Poliüri", "Polidipsi"])).issubset(norm_symptoms):
            return "Şekersiz Diyet"
        elif 110 < genel_blood_sugar < 180 and set(map(normalize, ["Yorgunluk", "Nöropati", "Bulanık Görme"])).issubset(norm_symptoms):
            return "Az Şekerli Diyet"
        elif genel_blood_sugar >= 180 and set(map(normalize, ["Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"])).issubset(norm_symptoms):
            return "Şekersiz Diyet"
        elif genel_blood_sugar >= 180 and set(map(normalize, ["Yaraların Yavaş İyileşmesi", "Kilo Kaybı"])).issubset(norm_symptoms):
            return "Şekersiz Diyet"
        else:
            return "Uygun semptomlar girilmediği için öneri üretilemedi. Lütfen semptomları ve genel kan şekeri değerini aynı gün için girin." 