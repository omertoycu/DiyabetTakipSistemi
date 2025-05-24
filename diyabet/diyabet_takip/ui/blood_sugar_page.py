from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QTableWidget,
                             QTableWidgetItem, QComboBox, QDateEdit, QTextEdit,
                             QDialog, QTimeEdit)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont
import sys
import os
from datetime import datetime, timedelta , time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pytz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection

class BloodSugarPage(QWidget):
    def __init__(self, main_window, patient_id=None):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id or main_window.current_user['id']
        self.db = DatabaseConnection()
        self.user_type = main_window.current_user.get('kullanici_tipi', 'hasta')
        
        # Ölçüm saat aralıkları ve açıklamaları
        self.measurement_times = {
            'Sabah': {
                'start': 7,
                'end': 8,
                'description': 'Uyanış sonrası kan şekeri ölçümü'
            },
            'Öğle': {
                'start': 12,
                'end': 13,
                'description': 'Öğle yemeğinden önce veya öğle yemeği sonrası'
            },
            'İkindi': {
                'start': 15,
                'end': 16,
                'description': 'Ara öğün veya günün sonrasında'
            },
            'Akşam': {
                'start': 18,
                'end': 19,
                'description': 'Akşam yemeğinden önce veya akşam yemeği sonrası'
            },
            'Gece': {
                'start': 22,
                'end': 23,
                'description': 'Gece yatmadan önce'
            }
        }
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tarih seçici (en başta tanımla)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.dateChanged.connect(self.on_date_changed)
        
        # Başlık
        title = QLabel("Kan Şekeri Takibi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Ölçüm saatleri bilgisi
        info_text = """
        Günlük Kan Şekeri Ölçüm Saatleri:
        • Sabah: 07:00 - 08:00
        • Öğlen: 12:00 - 13:00
        • İkindi: 15:00 - 16:00
        • Akşam: 18:00 - 19:00
        • Gece: 22:00 - 23:00
        """
        info_label = QLabel(info_text)
        info_label.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # GÜNLÜK DEĞERLENDİRME TARİH SEÇİCİ
        daily_row = QHBoxLayout()
        daily_row.addWidget(QLabel("Günlük Değerlendirme için Tarih Seç:"))
        self.daily_date_input = QDateEdit()
        self.daily_date_input.setCalendarPopup(True)
        self.daily_date_input.setDate(QDate.currentDate())
        self.daily_date_input.dateChanged.connect(self.on_daily_date_changed)
        daily_row.addWidget(self.daily_date_input)
        layout.addLayout(daily_row)
        
        # GÜNLÜK DEĞERLENDİRME KUTUSU
        self.average_text = QTextEdit()
        self.average_text.setReadOnly(True)
        self.average_text.setStyleSheet("font-size: 14px; padding: 0px; background: #e3f2fd; border: none; border-radius: 10px; min-height: 200px; max-height: 350px;")
        layout.addWidget(self.average_text)
        
        # Yeni ölçüm formu - sadece hasta kullanıcılar için
        if self.user_type == 'hasta':
            form_container = QWidget()
            form_layout = QHBoxLayout(form_container)
            
            # Ölçüm değeri
            self.value_input = QLineEdit()
            self.value_input.setPlaceholderText("Ölçüm değeri (mg/dL)")
            form_layout.addWidget(QLabel("Ölçüm Değeri:"))
            form_layout.addWidget(self.value_input)
            
            # Ölçüm tipi
            self.type_combo = QComboBox()
            self.type_combo.addItems(["Sabah", "Öğle", "İkindi", "Akşam", "Gece"])
            form_layout.addWidget(QLabel("Ölçüm Tipi:"))
            form_layout.addWidget(self.type_combo)
            
            # Tarih ve saat
            date_time_container = QWidget()
            date_time_layout = QHBoxLayout(date_time_container)
            
            self.time_input = QTimeEdit()
            self.time_input.setDisplayFormat("HH:mm")
            self.time_input.setTime(QTime.currentTime())
            date_time_layout.addWidget(QLabel("Tarih:"))
            date_time_layout.addWidget(self.date_input)
            
            self.time_input = QTimeEdit()
            self.time_input.setDisplayFormat("HH:mm")
            self.time_input.setTime(QTime.currentTime())
            date_time_layout.addWidget(QLabel("Saat:"))
            date_time_layout.addWidget(self.time_input)
            
            form_layout.addWidget(date_time_container)
            

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
        
        # Grafik  butonu
        graph_row = QHBoxLayout()
        self.graph_date = QDateEdit()
        self.graph_date.setCalendarPopup(True)
        self.graph_date.setDate(QDate.currentDate())
        graph_row.addWidget(QLabel("Grafik için Gün Seç:"))
        graph_row.addWidget(self.graph_date)
        self.graph_button = QPushButton("Grafiği Göster")
        self.graph_button.setStyleSheet("""
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
        self.graph_button.clicked.connect(self.show_graph_for_selected_date)
        graph_row.addWidget(self.graph_button)
        layout.addLayout(graph_row)
        
        # Ölçüm listesi
        self.measurement_table = QTableWidget()
        self.measurement_table.setColumnCount(6)
        self.measurement_table.setHorizontalHeaderLabels([
            "Tarih", "Saat", "Ölçüm Tipi", "Değer", "Notlar", "İşlemler"
        ])
        layout.addWidget(self.measurement_table)
        
        self.setLayout(layout)
        self.load_measurements(self.daily_date_input.date().toPyDate())
        self.update_daily_average(self.daily_date_input.date().toPyDate())
    
    def check_measurement_time(self, measurement_type, datetime_obj):

        try:

            if isinstance(datetime_obj, datetime):
                hour = datetime_obj.hour
            elif isinstance(datetime_obj, time):
                hour = datetime_obj.hour
            else:
                hour = int(datetime_obj)
            # Ölçüm tipi için zaman aralığını al
            time_info = self.measurement_times[measurement_type]
            # Saat aralığını kontrol et
            return time_info['start'] <= hour <= time_info['end']
        except Exception as e:
            return False
    
    def get_insulin_recommendation(self, average):

        if average < 70:
            return "Yok (Hipoglisemi)"
        elif 70 <= average <= 110:
            return "Yok (Normal)"
        elif 111 <= average <= 150:
            return "1 ml (Orta Yüksek)"
        elif 151 <= average <= 200:
            return "2 ml (Yüksek)"
        else:
            return "3 ml (Çok Yüksek)"
    
    def calculate_average_for_measurement(self, measurements, current_type):

        measurement_order = ['Sabah', 'Öğle', 'İkindi', 'Akşam', 'Gece']
        current_index = measurement_order.index(current_type)
        valid_measurements = []
        
        for type_ in measurement_order[:current_index + 1]:
            for value, m_type, datetime_obj in measurements:
                if m_type == type_:
                    # MySQL'den gelen datetime string'ini datetime nesnesine çevir
                    if isinstance(datetime_obj, str):
                        datetime_obj = datetime.strptime(datetime_obj, '%Y-%m-%d %H:%M:%S')
                    if self.check_measurement_time(type_, datetime_obj):
                        valid_measurements.append(value)
                        break
        
        if not valid_measurements:
            return None, []
        
        return sum(valid_measurements) / len(valid_measurements), valid_measurements

    def update_daily_average(self, selected_date=None):

        if selected_date is None:
            if hasattr(self, 'daily_date_input'):
                selected_date = self.daily_date_input.date().toPyDate()
            elif hasattr(self, 'date_input'):
                selected_date = self.date_input.date().toPyDate()
            else:
                from datetime import date as dtdate
                selected_date = dtdate.today()
        query = """
            SELECT olcum_degeri, olcum_tipi, tarih
            FROM kan_sekeri_olcumleri 
            WHERE hasta_id = %s AND DATE(tarih) = %s
            ORDER BY tarih ASC
        """
        measurements = self.db.fetch_all(query, (self.patient_id, selected_date))
        if not measurements:
            self.average_text.setText("Bu gün için henüz ölçüm yapılmamış.")
            return
        total_valid_measurements = []
        missing_measurements = []
        out_of_time_measurements = []
        measurement_values = {}
        for type_ in ['Sabah', 'Öğle', 'İkindi', 'Akşam', 'Gece']:
            type_measurements = []
            for value, m_type, datetime_obj in measurements:
                if m_type == type_:
                    if isinstance(datetime_obj, str):
                        datetime_obj = datetime.strptime(datetime_obj, '%Y-%m-%d %H:%M:%S')
                    if self.check_measurement_time(type_, datetime_obj):
                        type_measurements.append((value, datetime_obj))
                        total_valid_measurements.append(value)
                    else:
                        out_of_time_measurements.append((type_, value, datetime_obj))
            if type_measurements:
                measurement_values[type_] = type_measurements[0]
            else:
                missing_measurements.append(type_)
        # HTML formatında mesaj oluştur
        message = """
        <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; font-family: Arial;'>
            <h2 style='color: #1565c0; text-align: center; margin-bottom: 20px;'>Günlük Kan Şekeri Değerlendirmesi</h2>
            <div style='background: #f5faff; max-height: 260px; overflow-y: auto; border-radius: 8px; border: 1px solid #bbdefb; padding: 10px; margin-bottom: 20px;'>
                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;'>
        """
        for type_ in ['Sabah', 'Öğle', 'İkindi', 'Akşam', 'Gece']:
            if type_ in measurement_values:
                value, dt = measurement_values[type_]
                insulin = self.get_insulin_recommendation(value)
                message += f"""
                    <div style='background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='color: #1976d2; margin: 0 0 10px 0;'>{type_.capitalize()}</h3>
                        <p style='margin: 5px 0;'><b>Değer:</b> {value} mg/dL</p>
                        <p style='margin: 5px 0;'><b>Saat:</b> {dt.strftime('%H:%M')}</p>
                        <p style='margin: 5px 0;'><b>İnsülin:</b> {insulin}</p>
                    </div>
                """
            else:
                message += f"""
                    <div style='background-color: #ffebee; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <h3 style='color: #c62828; margin: 0 0 10px 0;'>{type_.capitalize()}</h3>
                        <p style='margin: 5px 0; color: #c62828;'>Ölçüm yapılmamış</p>
                    </div>
                """
        message += """
                </div>
            </div>
            <div style='background-color: white; padding: 15px; border-radius: 5px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
        """
        if total_valid_measurements:
            daily_average = sum(total_valid_measurements) / len(total_valid_measurements)
            message += f"""
                <h3 style='color: #1565c0; margin-top: 0;'>Genel Değerlendirme</h3>
                <p style='margin: 5px 0;'><b>Günlük Ortalama:</b> {daily_average:.1f} mg/dL</p>
                <p style='margin: 5px 0;'><b>Toplam Geçerli Ölçüm:</b> {len(total_valid_measurements)}</p>
                <p style='margin: 5px 0;'><b>Genel İnsülin Önerisi:</b> {self.get_insulin_recommendation(daily_average)}</p>
            """
        if missing_measurements or out_of_time_measurements or len(total_valid_measurements) < 3:
            message += """
                <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;'>
                    <h3 style='color: #c62828; margin-top: 0;'>⚠️ Uyarılar</h3>
            """
            if missing_measurements:
                message += "<p style='color: #c62828; margin: 5px 0;'>Eksik Ölçümler:</p><ul style='margin: 5px 0;'>"
                for type_ in missing_measurements:
                    message += f"<li style='color: #c62828;'>{type_.capitalize()} ölçümü eksik! Ortalama alınırken bu ölçüm hesaba katılmadı.</li>"
                message += "</ul>"
            if out_of_time_measurements:
                message += "<p style='color: #c62828; margin: 5px 0;'>Zaman Aralığı Dışı Ölçümler:</p><ul style='margin: 5px 0;'>"
                for type_, value, dt in out_of_time_measurements:
                    time_info = self.measurement_times[type_]
                    message += f"<li style='color: #c62828;'>{type_.capitalize()} ölçümü ({value} mg/dL) belirtilen saat aralığında değil. Önerilen: {time_info['start']:02d}:00 - {time_info['end']:02d}:00</li>"
                message += "</ul>"
            if len(total_valid_measurements) < 3:
                message += "<p style='color: #c62828; margin: 5px 0;'>⚠️ Yetersiz veri! Ortalama hesaplaması güvenilir değildir. En az 3 geçerli ölçüm gereklidir.</p>"
            message += "</div>"
        message += """
            </div>
        </div>
        """
        self.average_text.setHtml(message)
    
    def save_measurement(self):
        try:
            if self.user_type != 'hasta':
                QMessageBox.warning(self, "Uyarı", "Sadece hastalar kan şekeri ölçümü kaydedebilir!")
                return
                
            value = float(self.value_input.text())
            measurement_type = self.type_combo.currentText()
            date = self.date_input.date().toPyDate()
            time_obj = self.time_input.time().toPyTime()
            
            # Türkiye zaman dilimini ayarla
            turkey_tz = pytz.timezone('Europe/Istanbul')
            
            # datetime oluştur ve Türkiye zaman dilimine çevir
            datetime_obj = datetime.combine(date, time_obj)
            datetime_obj = turkey_tz.localize(datetime_obj)
            
            # Saat kontrolü - uyarı ver ama yine de kaydet
            is_time_valid = self.check_measurement_time(measurement_type, datetime_obj)
            if not is_time_valid:
                time_info = self.measurement_times[measurement_type]
                reply = QMessageBox.question(
                    self,
                    "Zaman Aralığı Uyarısı",
                    f"{measurement_type.capitalize()} ölçümü için önerilen saat aralığı: {time_info['start']:02d}:00 - {time_info['end']:02d}:00\n\n"
                    f"Bu ölçüm kaydedilecek ancak günlük ortalamaya dahil edilmeyecektir.\n\n"
                    f"Devam etmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            notes = self.notes_input.toPlainText()
            
            # Günlük ölçüm sayısı kontrolü
            daily_count_query = """
                SELECT COUNT(*) FROM kan_sekeri_olcumleri 
                WHERE hasta_id = %s AND DATE(tarih) = %s
            """
            daily_count = self.db.fetch_one(daily_count_query, (self.patient_id, date))[0]
            
            if daily_count >= 5:
                QMessageBox.warning(self, "Uyarı", "Günlük maksimum ölçüm sayısına (5) ulaşıldı!")
                return
            
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
                    delete_query = """
                        DELETE FROM kan_sekeri_olcumleri 
                        WHERE hasta_id = %s AND DATE(tarih) = %s AND olcum_tipi = %s
                    """
                    self.db.execute_query(delete_query, (self.patient_id, date, measurement_type))
                else:
                    return
            
            # Yeni ölçümü kaydet
            try:
                query = """
                    INSERT INTO kan_sekeri_olcumleri (hasta_id, olcum_degeri, olcum_tipi, tarih, notlar)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                # datetime nesnesini MySQL formatına dönüştür
                mysql_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                
                self.db.execute_query(query, (
                    self.patient_id,
                    value,
                    measurement_type,
                    mysql_datetime,  # MySQL formatında datetime
                    notes
                ))
                # Kritik uyarı ekle
                self.db.add_critical_blood_sugar_warning(self.patient_id, value, datetime_obj)
                
                # Başarı mesajı - zaman uygunluğuna göre farklı
                if is_time_valid:
                    QMessageBox.information(self, "Başarılı", "Ölçüm kaydedildi ve günlük ortalamaya dahil edildi!")
                else:
                    QMessageBox.information(self, "Başarılı", "Ölçüm kaydedildi! (Not: Zaman aralığı dışında olduğu için günlük ortalamaya dahil edilmedi)")
                
                self.clear_form()
                self.load_measurements(self.daily_date_input.date().toPyDate())
                self.update_daily_average(self.daily_date_input.date().toPyDate())
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ölçüm kaydedilirken bir hata oluştu: {str(e)}")
                
        except ValueError:
            QMessageBox.critical(self, "Hata", "Lütfen geçerli bir sayı girin!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen bir hata oluştu: {str(e)}")
    
    def load_measurements(self, selected_date=None):
        if selected_date is None:
            if hasattr(self, 'daily_date_input'):
                selected_date = self.daily_date_input.date().toPyDate()
            elif hasattr(self, 'date_input'):
                selected_date = self.date_input.date().toPyDate()
            else:
                from datetime import date as dtdate
                selected_date = dtdate.today()
        query = """
            SELECT id, tarih, olcum_tipi, olcum_degeri, notlar 
            FROM kan_sekeri_olcumleri 
            WHERE hasta_id = %s AND DATE(tarih) = %s
            ORDER BY tarih DESC, olcum_tipi
        """
        measurements = self.db.fetch_all(query, (self.patient_id, selected_date))
        self.measurement_table.setRowCount(len(measurements))
        
        for row, measurement in enumerate(measurements):
            # Tarih
            date_str = measurement[1].strftime("%d.%m.%Y")
            self.measurement_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Saat
            time_str = measurement[1].strftime("%H:%M")
            self.measurement_table.setItem(row, 1, QTableWidgetItem(time_str))
            
            # Ölçüm tipi
            self.measurement_table.setItem(row, 2, QTableWidgetItem(measurement[2].capitalize()))
            
            # Değer
            value_item = QTableWidgetItem(str(measurement[3]))
            if measurement[3] > 200:
                value_item.setForeground(Qt.red)
            elif measurement[3] < 70:
                value_item.setForeground(Qt.blue)
            self.measurement_table.setItem(row, 3, value_item)
            
            # Notlar
            self.measurement_table.setItem(row, 4, QTableWidgetItem(measurement[4] or ""))
            

            if self.user_type == 'hasta':
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
                delete_button.clicked.connect(lambda checked, id=measurement[0]: self.delete_measurement(id))
                self.measurement_table.setCellWidget(row, 5, delete_button)
            else:
                self.measurement_table.setItem(row, 5, QTableWidgetItem("-"))
    
    def delete_measurement(self, measurement_id):

        if self.user_type != 'hasta':
            QMessageBox.warning(self, "Uyarı", "Sadece hastalar ölçüm silebilir!")
            return
            
        reply = QMessageBox.question(
            self, "Onay",
            "Bu ölçümü silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM kan_sekeri_olcumleri WHERE id = %s AND hasta_id = %s"
                self.db.execute_query(query, (measurement_id, self.patient_id))
                self.load_measurements(self.daily_date_input.date().toPyDate())
                QMessageBox.information(self, "Başarılı", "Ölçüm silindi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ölçüm silinirken bir hata oluştu: {str(e)}")
    
    def clear_form(self):
        self.value_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setTime(QTime.currentTime())
        self.notes_input.clear()
    
    def show_graph_for_selected_date(self):
        selected_date = self.graph_date.date().toPyDate()
        query = """
            SELECT tarih, olcum_degeri, olcum_tipi
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s AND DATE(tarih) = %s
            ORDER BY tarih ASC
        """
        measurements = self.db.fetch_all(query, (self.patient_id, selected_date))
        if not measurements:
            QMessageBox.information(self, "Bilgi", f"{selected_date} günü için veri yok.")
            return
        dates = [m[0] for m in measurements]
        values = [m[1] for m in measurements]
        types = [m[2].capitalize() for m in measurements]
        # Grafik penceresi oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{selected_date} Kan Şekeri Grafiği")
        layout = QVBoxLayout(dialog)
        fig = Figure(figsize=(10,5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.plot(dates, values, marker='o', linestyle='-', color='b')
        for i, txt in enumerate(types):
            ax.annotate(txt, (dates[i], values[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        ax.set_title(f'{selected_date} Kan Şekeri Grafiği')
        ax.set_xlabel('Saat')
        ax.set_ylabel('Değer (mg/dL)')
        ax.grid(True)
        fig.autofmt_xdate()
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def on_date_changed(self, qdate):
        selected_date = qdate.toPyDate()
        self.load_measurements(selected_date)
        self.update_daily_average(selected_date)
    
    def on_daily_date_changed(self, qdate):
        selected_date = qdate.toPyDate()
        self.load_measurements(selected_date)
        self.update_daily_average(selected_date) 