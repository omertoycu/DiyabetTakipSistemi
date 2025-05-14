from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QTableWidget,
                             QTableWidgetItem, QComboBox, QDateEdit, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os
from datetime import datetime, timedelta

# Proje kök dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class BloodSugarPage(QWidget):
    def __init__(self, main_window, patient_id=None):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Başlık
        title = QLabel("Kan Şekeri Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Yeni ölçüm formu
        form_container = QWidget()
        form_layout = QHBoxLayout(form_container)
        
        # Ölçüm değeri
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Ölçüm değeri (mg/dL)")
        form_layout.addWidget(QLabel("Ölçüm Değeri:"))
        form_layout.addWidget(self.value_input)
        
        # Ölçüm tipi
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Sabah", "Öğlen", "İkindi", "Akşam", "Gece"])
        form_layout.addWidget(QLabel("Ölçüm Tipi:"))
        form_layout.addWidget(self.type_combo)
        
        # Tarih
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("Tarih:"))
        form_layout.addWidget(self.date_input)
        
        # Notlar
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notlar...")
        self.notes_input.setMaximumHeight(60)
        form_layout.addWidget(QLabel("Notlar:"))
        form_layout.addWidget(self.notes_input)
        
        # Kaydet butonu
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
        save_button.clicked.connect(self.save_measurement)
        form_layout.addWidget(save_button)
        
        layout.addWidget(form_container)
        
        # Günlük özet
        summary_container = QWidget()
        summary_layout = QVBoxLayout(summary_container)
        
        summary_title = QLabel("Günlük Özet")
        summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        summary_layout.addWidget(summary_title)
        
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
        """)
        summary_layout.addWidget(self.summary_label)
        
        # İnsülin önerisi
        self.insulin_label = QLabel()
        self.insulin_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #b8daff;
            }
        """)
        summary_layout.addWidget(self.insulin_label)
        
        layout.addWidget(summary_container)
        
        # Ölçüm listesi
        self.measurement_table = QTableWidget()
        self.measurement_table.setColumnCount(5)
        self.measurement_table.setHorizontalHeaderLabels([
            "Tarih", "Ölçüm Tipi", "Değer", "Notlar", "İşlemler"
        ])
        layout.addWidget(self.measurement_table)
        
        self.setLayout(layout)
        self.load_measurements()
    
    def save_measurement(self):
        try:
            value = float(self.value_input.text())
            measurement_type = self.type_combo.currentText().lower()
            date = self.date_input.date().toPyDate()
            notes = self.notes_input.toPlainText()
            
            # Aynı gün ve ölçüm tipi için kontrol
            check_query = """
                SELECT COUNT(*) FROM kan_sekeri_olcumleri 
                WHERE hasta_id = %s AND DATE(tarih) = %s AND olcum_tipi = %s
            """
            count = self.db.fetch_one(check_query, (self.patient_id, date, measurement_type))[0]
            
            if count > 0:
                reply = QMessageBox.question(
                    self, 
                    "Uyarı",
                    f"Bu tarih için {measurement_type.capitalize()} ölçümü zaten kayıtlı. Üzerine yazmak istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    # Mevcut kaydı sil
                    delete_query = """
                        DELETE FROM kan_sekeri_olcumleri 
                        WHERE hasta_id = %s AND DATE(tarih) = %s AND olcum_tipi = %s
                    """
                    self.db.execute_query(delete_query, (self.patient_id, date, measurement_type))
                else:
                    return
            
            # Yeni ölçümü kaydet
            query = """
                INSERT INTO kan_sekeri_olcumleri (hasta_id, olcum_degeri, olcum_tipi, tarih, notlar)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (
                self.patient_id,
                value,
                measurement_type,
                date,
                notes
            ))
            
            QMessageBox.information(self, "Başarılı", "Ölçüm kaydedildi!")
            self.clear_form()
            self.load_measurements()
            
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir ölçüm değeri girin!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ölçüm kaydedilirken bir hata oluştu: {str(e)}")
    
    def clear_form(self):
        self.value_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.notes_input.clear()
    
    def load_measurements(self):
        query = """
            SELECT tarih, olcum_tipi, olcum_degeri, notlar, id
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s
            ORDER BY tarih DESC, FIELD(olcum_tipi, 'sabah', 'öğlen', 'ikindi', 'akşam', 'gece')
        """
        
        measurements = self.db.fetch_all(query, (self.patient_id,))
        
        self.measurement_table.setRowCount(len(measurements))
        for row, measurement in enumerate(measurements):
            # Tarih
            date_str = measurement[0].strftime("%d.%m.%Y")
            self.measurement_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Ölçüm tipi
            self.measurement_table.setItem(row, 1, QTableWidgetItem(measurement[1].capitalize()))
            
            # Değer
            value_item = QTableWidgetItem(str(measurement[2]))
            if measurement[2] > 180:
                value_item.setForeground(Qt.red)
            elif measurement[2] < 70:
                value_item.setForeground(Qt.blue)
            else:
                value_item.setForeground(Qt.green)
            self.measurement_table.setItem(row, 2, value_item)
            
            # Notlar
            self.measurement_table.setItem(row, 3, QTableWidgetItem(measurement[3] or ""))
            
            # Silme butonu
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
            delete_button.clicked.connect(lambda checked, id=measurement[4]: self.delete_measurement(id))
            self.measurement_table.setCellWidget(row, 4, delete_button)
        
        self.update_daily_summary()
    
    def update_daily_summary(self):
        selected_date = self.date_input.date().toPyDate()
        query = """
            SELECT olcum_tipi, olcum_degeri
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s AND DATE(tarih) = %s
            ORDER BY FIELD(olcum_tipi, 'sabah', 'öğlen', 'ikindi', 'akşam', 'gece')
        """
        
        results = self.db.fetch_all(query, (self.patient_id, selected_date))
        
        if not results:
            self.summary_label.setText("Seçili tarih için henüz ölçüm yapılmamış.")
            self.insulin_label.setText("")
            return
        
        # Ölçüm sayısı kontrolü
        if len(results) < 3:
            self.summary_label.setText("Yetersiz veri! Ortalama hesaplaması güvenilir değildir.")
            self.insulin_label.setText("")
            return
        
        # Eksik ölçüm kontrolü
        expected_types = {'sabah', 'öğlen', 'ikindi', 'akşam', 'gece'}
        actual_types = {r[0] for r in results}
        missing_types = expected_types - actual_types
        
        if missing_types:
            missing_text = ", ".join(missing_types)
            self.summary_label.setText(f"Ölçüm eksik! Ortalama alınırken şu ölçümler hesaba katılmadı: {missing_text}")
        else:
            self.summary_label.setText("Tüm ölçümler tamamlandı.")
        
        # Ortalama hesaplama
        values = [r[1] for r in results]
        average = sum(values) / len(values)
        
        # Semptomları al
        symptoms_query = """
            SELECT semptom
            FROM semptom_takibi
            WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        symptoms_result = self.db.fetch_all(symptoms_query, (self.patient_id, selected_date))
        symptoms = [s[0] for s in symptoms_result]
        
        # İnsülin önerisi
        insulin_recommendation = self.get_insulin_recommendation(average)
        
        # Diyet ve egzersiz önerileri
        diet_exercise_recommendations = self.get_diet_exercise_recommendations(average, symptoms)
        
        summary_text = f"Günlük Ortalama: {average:.1f} mg/dL\n"
        summary_text += f"İnsülin Önerisi: {insulin_recommendation}\n\n"
        summary_text += f"Önerilen Diyet: {diet_exercise_recommendations['diet']}\n"
        summary_text += f"Önerilen Egzersiz: {diet_exercise_recommendations['exercise']}"
        
        self.insulin_label.setText(summary_text)
        
        # Önerileri veritabanına kaydet
        self.save_recommendations(selected_date, diet_exercise_recommendations)
    
    def get_insulin_recommendation(self, average):
        if average < 70:
            return "Yok (Hipoglisemi)"
        elif average <= 110:
            return "Yok (Normal)"
        elif average <= 150:
            return "1 ml (Orta Yüksek)"
        elif average <= 200:
            return "2 ml (Yüksek)"
        else:
            return "3 ml (Çok Yüksek)"
    
    def get_diet_exercise_recommendations(self, average, symptoms):
        # Hipoglisemi durumu
        if average < 70 and all(s in symptoms for s in ["Nöropati", "Polifaji", "Yorgunluk"]):
            return {
                "diet": "Dengeli Beslenme",
                "exercise": "Yok"
            }
        
        # Normal - Alt Düzey durumları
        elif 70 <= average <= 110:
            if all(s in symptoms for s in ["Yorgunluk", "Kilo Kaybı"]):
                return {
                    "diet": "Az Şekerli Diyet",
                    "exercise": "Yürüyüş"
                }
            elif all(s in symptoms for s in ["Polifaji", "Polidipsi"]):
                return {
                    "diet": "Dengeli Beslenme",
                    "exercise": "Yürüyüş"
                }
        
        # Normal - Üst Düzey / Hafif Yüksek durumları
        elif 110 < average <= 180:
            if all(s in symptoms for s in ["Bulanık Görme", "Nöropati"]):
                return {
                    "diet": "Az Şekerli Diyet",
                    "exercise": "Klinik Egzersiz"
                }
            elif all(s in symptoms for s in ["Poliüri", "Polidipsi"]):
                return {
                    "diet": "Şekersiz Diyet",
                    "exercise": "Klinik Egzersiz"
                }
            elif all(s in symptoms for s in ["Yorgunluk", "Nöropati", "Bulanık Görme"]):
                return {
                    "diet": "Az Şekerli Diyet",
                    "exercise": "Yürüyüş"
                }
        
        # Hiperglisemi durumları
        elif average > 180:
            if all(s in symptoms for s in ["Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"]):
                return {
                    "diet": "Şekersiz Diyet",
                    "exercise": "Klinik Egzersiz"
                }
            elif all(s in symptoms for s in ["Yaraların Yavaş İyileşmesi", "Kilo Kaybı"]):
                return {
                    "diet": "Şekersiz Diyet",
                    "exercise": "Yürüyüş"
                }
        
        # Varsayılan öneriler
        return {
            "diet": "Dengeli Beslenme",
            "exercise": "Yürüyüş"
        }
    
    def save_recommendations(self, date, recommendations):
        # Diyet önerisini kaydet
        diet_query = """
            INSERT INTO diyet_takibi (hasta_id, diyet_tipi, tarih, durum, onerilen)
            VALUES (%s, %s, %s, 'Uygulanmadı', %s)
            ON DUPLICATE KEY UPDATE onerilen = %s
        """
        self.db.execute_query(diet_query, (
            self.patient_id,
            recommendations['diet'],
            date,
            recommendations['diet'],
            recommendations['diet']
        ))
        
        # Egzersiz önerisini kaydet
        exercise_query = """
            INSERT INTO egzersiz_takibi (hasta_id, egzersiz_tipi, tarih, durum, onerilen)
            VALUES (%s, %s, %s, 'Yapılmadı', %s)
            ON DUPLICATE KEY UPDATE onerilen = %s
        """
        self.db.execute_query(exercise_query, (
            self.patient_id,
            recommendations['exercise'],
            date,
            recommendations['exercise'],
            recommendations['exercise']
        ))
    
    def delete_measurement(self, measurement_id):
        reply = QMessageBox.question(
            self, "Onay",
            "Bu ölçümü silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            query = "DELETE FROM kan_sekeri_olcumleri WHERE id = %s AND hasta_id = %s"
            self.db.execute_query(query, (measurement_id, self.patient_id))
            self.load_measurements()
            QMessageBox.information(self, "Başarılı", "Ölçüm silindi!") 