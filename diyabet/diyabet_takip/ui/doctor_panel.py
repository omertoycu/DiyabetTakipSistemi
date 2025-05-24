from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialog, QLineEdit, QDateEdit,
                             QComboBox, QFormLayout, QTabWidget, QFileDialog,
                             QInputDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap
import sys
import os
from datetime import datetime
import bcrypt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connection import DatabaseConnection
from ui.patient_detail_page import PatientDetailPage
from ui.genel_blood_sugar_page import GenelBloodSugarPage

class AddPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.init_ui()
    
    def hash_password(self, password):
        #Şifreyi bcrypt ile hashler
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def validate_tc(self, tc):
        #TC Kimlik numarası doğrulama
        if not tc.isdigit() or len(tc) != 11:
            return False
        return True
    
    def validate_email(self, email):
        #E-posta doğrulama
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password(self, password):
        #Şifre doğrulama
        if len(password) < 6:
            return False
        return True
    
    def init_ui(self):
        self.setWindowTitle("Yeni Hasta Ekle")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # TC Kimlik
        self.tc_input = QLineEdit()
        self.tc_input.setMaxLength(11)
        self.tc_input.setPlaceholderText("11 haneli TC Kimlik No")
        layout.addRow("TC Kimlik:", self.tc_input)
        
        # Ad
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Hastanın adı")
        layout.addRow("Ad:", self.name_input)
        
        # Soyad
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Hastanın soyadı")
        layout.addRow("Soyad:", self.surname_input)
        
        # E-posta
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@email.com")
        layout.addRow("E-posta:", self.email_input)
        
        # Doğum Tarihi
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate.currentDate())
        layout.addRow("Doğum Tarihi:", self.birth_date)
        
        # Cinsiyet
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Erkek", "Kadın"])
        layout.addRow("Cinsiyet:", self.gender_combo)
        
        # Şifre
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("En az 6 karakter")
        layout.addRow("Şifre:", self.password_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
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
        save_button.clicked.connect(self.save_patient)
        
        cancel_button = QPushButton("İptal")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
    
    def save_patient(self):
        try:
            tc = self.tc_input.text().strip()
            name = self.name_input.text().strip()
            surname = self.surname_input.text().strip()
            email = self.email_input.text().strip()
            birth_date = self.birth_date.date().toPyDate()
            gender = 'E' if self.gender_combo.currentText() == "Erkek" else 'K'
            password = self.password_input.text()
            
            # Boş alan kontrolü
            if not all([tc, name, surname, email, password]):
                QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
                return
            
            # TC Kimlik kontrolü
            if not self.validate_tc(tc):
                QMessageBox.warning(self, "Uyarı", "Geçersiz TC Kimlik numarası! 11 haneli sayısal değer giriniz.")
                return
            
            # E-posta kontrolü
            if not self.validate_email(email):
                QMessageBox.warning(self, "Uyarı", "Geçersiz e-posta adresi!")
                return
            
            # Şifre kontrolü
            if not self.validate_password(password):
                QMessageBox.warning(self, "Uyarı", "Şifre en az 6 karakter olmalıdır!")
                return
            
            # TC ve e-posta kontrolü
            check_query = """
                SELECT id FROM kullanicilar
                WHERE tc_kimlik = %s OR email = %s
            """
            existing_user = self.db.fetch_one(check_query, (tc, email))
            
            if existing_user:
                QMessageBox.warning(self, "Uyarı", "Bu TC Kimlik veya E-posta adresi zaten kullanılıyor!")
                return
            
            # Şifreyi hashle
            hashed_password = self.hash_password(password)
            
            # Hasta ekle
            insert_query = """
                INSERT INTO kullanicilar (tc_kimlik, ad, soyad, email, dogum_tarihi, cinsiyet, sifre, kullanici_tipi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'hasta')
            """
            
            self.db.execute_query(insert_query, (
                tc, name, surname, email, birth_date, gender, hashed_password.decode('utf-8')
            ))
            
            # Doktor-Hasta ilişkisi kur
            patient_id = self.db.fetch_one("SELECT LAST_INSERT_ID()")[0]
            doctor_id = self.parent().main_window.current_user['id']
            
            relation_query = """
                INSERT INTO doktor_hasta_iliskisi (doktor_id, hasta_id)
                VALUES (%s, %s)
            """
            
            self.db.execute_query(relation_query, (doctor_id, patient_id))
            
            QMessageBox.information(self, "Başarılı", "Hasta başarıyla eklendi!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hasta eklenirken bir hata oluştu: {str(e)}")

class RecommendationDialog(QDialog):
    def __init__(self, patient_id, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.patient_id = patient_id
        self.setWindowTitle("Günlük Öneri Özeti")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        today = datetime.now().date()

        # Kan şekeri ortalaması
        avg_query = """
            SELECT AVG(olcum_degeri)
            FROM kan_sekeri_olcumleri
            WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        avg_result = self.db.fetch_one(avg_query, (self.patient_id, today))
        average = avg_result[0] if avg_result and avg_result[0] else None
        avg_label = QLabel(f"Kan Şekeri Ortalaması: {average:.1f} mg/dL" if average else "Bugün ölçüm yok.")
        layout.addWidget(avg_label)

        # Belirtiler
        symptoms_query = """
            SELECT semptom
            FROM semptom_takibi
            WHERE hasta_id = %s AND DATE(tarih) = %s
        """
        symptoms_result = self.db.fetch_all(symptoms_query, (self.patient_id, today))
        symptoms = [s[0] for s in symptoms_result]
        symptoms_label = QLabel(f"Belirtiler: {', '.join(symptoms) if symptoms else 'Yok'}")
        layout.addWidget(symptoms_label)

        # Diyet önerisi
        diet_query = """
            SELECT oneriler
            FROM diyet_onerileri
            WHERE hasta_id = %s AND tarih = %s
        """
        diet_result = self.db.fetch_one(diet_query, (self.patient_id, today))
        diet_text = diet_result[0] if diet_result and diet_result[0] else "Yok"
        diet_label = QLabel(f"Diyet Önerisi: {diet_text}")
        layout.addWidget(diet_label)

        # Egzersiz önerisi
        exercise_query = """
            SELECT oneriler
            FROM egzersiz_onerileri
            WHERE hasta_id = %s AND tarih = %s
        """
        exercise_result = self.db.fetch_one(exercise_query, (self.patient_id, today))
        exercise_text = exercise_result[0] if exercise_result and exercise_result[0] else "Yok"
        exercise_label = QLabel(f"Egzersiz Önerisi: {exercise_text}")
        layout.addWidget(exercise_label)

        # Kapat butonu
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)

class WarningsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseConnection()
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Uyarılar")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.warning_table = QTableWidget()
        self.warning_table.setColumnCount(4)
        self.warning_table.setHorizontalHeaderLabels(["Hasta Adı", "Uyarı Tipi", "Mesaj", "Okundu"]) 
        layout.addWidget(self.warning_table)
        self.setLayout(layout)
        self.load_warnings()
    def load_warnings(self):
        doctor_id = self.main_window.current_user['id']
        query = '''
            SELECT u.id, u.hasta_id, k.ad, k.soyad, u.uyari_tipi, u.mesaj, u.okundu
            FROM uyarilar u
            JOIN doktor_hasta_iliskisi d ON d.hasta_id = u.hasta_id
            JOIN kullanicilar k ON k.id = u.hasta_id
            WHERE d.doktor_id = %s AND u.okundu = FALSE
            ORDER BY u.tarih DESC
        '''
        warnings = self.db.fetch_all(query, (doctor_id,))
        self.warning_table.setRowCount(len(warnings))
        for row, w in enumerate(warnings):
            self.warning_table.setItem(row, 0, QTableWidgetItem(f"{w[2]} {w[3]}"))
            self.warning_table.setItem(row, 1, QTableWidgetItem(w[4]))
            self.warning_table.setItem(row, 2, QTableWidgetItem(w[5]))
            okundu_button = QPushButton("Okundu")
            okundu_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #219150;
                }
            """)
            okundu_button.clicked.connect(lambda checked, uid=w[0]: self.mark_as_read(uid))
            self.warning_table.setCellWidget(row, 3, okundu_button)
    def mark_as_read(self, warning_id):
        query = "UPDATE uyarilar SET okundu = TRUE WHERE id = %s"
        self.db.execute_query(query, (warning_id,))
        self.load_warnings()

class DoctorPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseConnection()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        # Profil resmi ve buton
        profile_row = QHBoxLayout()
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(80, 80)
        self.profile_pic_label.setStyleSheet("border: 2px solid #2980b9; border-radius: 40px; background: #f0f0f0;")
        self.load_profile_pic()
        profile_row.addWidget(self.profile_pic_label)
        profile_btn = QPushButton("Profil Resmi Ekle/Güncelle")
        profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2471a3;
            }
        """)
        profile_btn.clicked.connect(self.change_profile_pic)
        profile_row.addWidget(profile_btn)
        profile_row.addStretch()
        main_layout.addLayout(profile_row)
        # Sekmeler
        self.tabs = QTabWidget()
        # Ana panel sekmesi
        self.panel_widget = QWidget()
        panel_layout = QVBoxLayout(self.panel_widget)
        
        # Başlık
        title = QLabel("Doktor Paneli")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(title)
        
        # Filtreler ve uyarı paneli
        filter_layout = QHBoxLayout()
        self.sugar_filter = QComboBox()
        self.sugar_filter.addItems(["Tümü", "Yüksek (>180)", "Normal (70-180)", "Düşük (<70)"])
        self.sugar_filter.currentIndexChanged.connect(self.load_patients)
        filter_layout.addWidget(QLabel("Kan Şekeri Filtresi:"))
        filter_layout.addWidget(self.sugar_filter)
        self.symptom_filter = QLineEdit()
        self.symptom_filter.setPlaceholderText("Semptom ara (örn. Yorgunluk)")
        self.symptom_filter.textChanged.connect(self.load_patients)
        filter_layout.addWidget(QLabel("Semptom Filtresi:"))
        filter_layout.addWidget(self.symptom_filter)
        panel_layout.addLayout(filter_layout)
        # Toplu uyarı paneli
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("background-color: #f8d7da; color: #721c24; padding: 8px; border-radius: 5px; border: 1px solid #f5c6cb;")
        panel_layout.addWidget(self.warning_label)
        
        # Hoş geldin mesajı
        if self.main_window.current_user:
            welcome_text = f"Hoş geldiniz, Dr. {self.main_window.current_user['ad']} {self.main_window.current_user['soyad']}"
        else:
            welcome_text = "Hoş geldiniz"
        welcome_label = QLabel(welcome_text)
        welcome_label.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(welcome_label)
        
        # Yeni hasta ekle butonu
        add_patient_button = QPushButton("Yeni Hasta Ekle")
        add_patient_button.setStyleSheet("""
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
        add_patient_button.clicked.connect(self.add_patient)
        panel_layout.addWidget(add_patient_button)
        
        # Hasta listesi
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(6)
        self.patient_table.setHorizontalHeaderLabels([
            "TC Kimlik", "Ad Soyad", "E-posta", "Son Ölçüm", "Durum", "İşlemler"
        ])
        panel_layout.addWidget(self.patient_table)
        
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
        panel_layout.addWidget(logout_button)
        
        # Sonra panel_widget'ı sekmeye ekle
        self.tabs.addTab(self.panel_widget, "Hastalar")
        # Uyarılar sekmesi
        self.warnings_page = WarningsPage(self.main_window)
        self.tabs.addTab(self.warnings_page, "Uyarılar")
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        self.check_daily_measurement_warnings()
        self.load_patients()
    
    def check_daily_measurement_warnings(self):
        today = datetime.now().date()
        query = """
            SELECT k.id FROM kullanicilar k
            JOIN doktor_hasta_iliskisi d ON d.hasta_id = k.id
            WHERE d.doktor_id = %s
        """
        doctor_id = self.main_window.current_user['id']
        patients = self.db.fetch_all(query, (doctor_id,))
        for (hasta_id,) in patients:
            # Bugünkü ölçüm sayısı
            count_query = """
                SELECT COUNT(*) FROM kan_sekeri_olcumleri WHERE hasta_id = %s AND DATE(tarih) = %s
            """
            count = self.db.fetch_one(count_query, (hasta_id, today))[0]
            # Aynı gün ve tipte uyarı var mı?
            warning_exists = lambda tip: self.db.fetch_one(
                "SELECT id FROM uyarilar WHERE hasta_id = %s AND uyari_tipi = %s AND DATE(tarih) = %s",
                (hasta_id, tip, today)
            )
            if count == 0 and not warning_exists('Ölçüm Eksik'):
                mesaj = "Hasta gün boyunca kan şekeri ölçümü yapmamıştır. Acil takip önerilir."
                self.db.execute_query(
                    "INSERT INTO uyarilar (hasta_id, uyari_tipi, mesaj, tarih) VALUES (%s, %s, %s, NOW())",
                    (hasta_id, 'Ölçüm Eksik', mesaj)
                )
            elif 0 < count < 3 and not warning_exists('Ölçüm Yetersiz'):
                mesaj = "Hastanın günlük kan şekeri ölçüm sayısı yetersiz (<3). Durum izlenmelidir."
                self.db.execute_query(
                    "INSERT INTO uyarilar (hasta_id, uyari_tipi, mesaj, tarih) VALUES (%s, %s, %s, NOW())",
                    (hasta_id, 'Ölçüm Yetersiz', mesaj)
                )

    def add_patient(self):
        dialog = AddPatientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_patients()
    
    def delete_patient(self, patient_id):
        reply = QMessageBox.question(
            self,
            "Hasta Silme Onayı",
            "Bu hastayı silmek istediğinizden emin misiniz?\nBu işlem geri alınamaz ve hastanın tüm verileri silinecektir.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # İlişkili tüm verileri sil
                tables = [
                    "uyarilar",
                    "kan_sekeri_olcumleri",
                    "genel_kan_sekeri",
                    "egzersiz_takibi",
                    "egzersiz_onerileri",
                    "diyet_takibi",
                    "diyet_onerileri",
                    "semptom_takibi",
                    "belirtiler",
                    "insulin_kayitlari",
                    "doktor_hasta_iliskisi"
                ]
                
                for table in tables:
                    query = f"DELETE FROM {table} WHERE hasta_id = %s"
                    self.db.execute_query(query, (patient_id,))
                
                # Hastayı sil
                query = "DELETE FROM kullanicilar WHERE id = %s AND kullanici_tipi = 'hasta'"
                self.db.execute_query(query, (patient_id,))
                
                QMessageBox.information(self, "Başarılı", "Hasta ve ilgili tüm veriler başarıyla silindi!")
                self.load_patients()
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Hasta silinirken bir hata oluştu: {str(e)}")
    
    def load_patients(self):
        # Filtreleri al
        sugar_filter = self.sugar_filter.currentText()
        symptom_filter = self.symptom_filter.text().strip().lower()
        # Hastaları çek
        query = """
            SELECT k.tc_kimlik, k.ad, k.soyad, k.email, k.id
            FROM kullanicilar k
            JOIN doktor_hasta_iliskisi d ON d.hasta_id = k.id
            WHERE d.doktor_id = %s
        """
        doctor_id = self.main_window.current_user['id']
        patients = self.db.fetch_all(query, (doctor_id,))
        filtered = []
        warnings = []
        for p in patients:
            # Son kan şekeri ölçümünü al
            sugar_query = """
                SELECT olcum_degeri, tarih FROM kan_sekeri_olcumleri WHERE hasta_id = %s ORDER BY tarih DESC LIMIT 1
            """
            sugar = self.db.fetch_one(sugar_query, (p[4],))
            sugar_val = sugar[0] if sugar else None
            
            # Bugünkü tüm semptomları al
            today = datetime.now().date()
            symptoms_query = """
                SELECT DISTINCT semptom FROM semptom_takibi 
                WHERE hasta_id = %s AND DATE(tarih) = %s
            """
            symptoms_result = self.db.fetch_all(symptoms_query, (p[4], today))
            todays_symptoms = [s[0].lower() for s in symptoms_result]
            
            # Son semptomu da al (gösterim için)
            last_symptom_query = """
                SELECT semptom FROM semptom_takibi WHERE hasta_id = %s ORDER BY tarih DESC LIMIT 1
            """
            symptom = self.db.fetch_one(last_symptom_query, (p[4],))
            symptom_val = symptom[0].lower() if symptom else ""
            
            # Filtre uygula
            sugar_ok = (
                sugar_filter == "Tümü" or
                (sugar_filter == "Yüksek (>180)" and sugar_val is not None and sugar_val > 180) or
                (sugar_filter == "Normal (70-180)" and sugar_val is not None and 70 <= sugar_val <= 180) or
                (sugar_filter == "Düşük (<70)" and sugar_val is not None and sugar_val < 70)
            )
            
            # Semptom filtresi: o günkü herhangi bir belirtide arama yapılsın
            symptom_ok = (not symptom_filter or any(symptom_filter in symptom for symptom in todays_symptoms))
            
            if sugar_ok and symptom_ok:
                filtered.append((p, sugar_val, symptom_val))
            # Kritik uyarı
            if sugar_val is not None and (sugar_val > 180 or sugar_val < 70):
                warnings.append(f"{p[1]} {p[2]}: Son kan şekeri {sugar_val} mg/dL")
            if symptom_filter and any(symptom_filter in symptom for symptom in todays_symptoms):
                warnings.append(f"{p[1]} {p[2]}: Bugünkü belirtilerde '{symptom_filter}' bulundu")
        # Tabloyu doldur
        self.patient_table.setRowCount(len(filtered))
        for row, (p, sugar_val, symptom_val) in enumerate(filtered):
            self.patient_table.setItem(row, 0, QTableWidgetItem(p[0]))
            self.patient_table.setItem(row, 1, QTableWidgetItem(f"{p[1]} {p[2]}"))
            self.patient_table.setItem(row, 2, QTableWidgetItem(p[3]))
            self.patient_table.setItem(row, 3, QTableWidgetItem(str(sugar_val) if sugar_val is not None else "-"))
            durum = "Kritik" if sugar_val is not None and (sugar_val > 180 or sugar_val < 70) else "Normal"
            durum_item = QTableWidgetItem(durum)
            if durum == "Kritik":
                durum_item.setForeground(Qt.red)
            else:
                durum_item.setForeground(Qt.green)
            self.patient_table.setItem(row, 4, durum_item)
            
            # İşlemler butonları için container
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            
            # Detay butonu
            view_btn = QPushButton("Detay")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            view_btn.clicked.connect(lambda checked, tc=p[0]: self.view_patient(tc))
            buttons_layout.addWidget(view_btn)
            
            # Sil butonu
            delete_btn = QPushButton("Sil")
            delete_btn.setStyleSheet("""
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
            delete_btn.clicked.connect(lambda checked, pid=p[4]: self.delete_patient(pid))
            buttons_layout.addWidget(delete_btn)
            
            self.patient_table.setCellWidget(row, 5, buttons_widget)
            
            # Okunmamış uyarı göster
            unread_query = "SELECT COUNT(*) FROM uyarilar WHERE hasta_id = %s AND okundu = 0"
            unread_count = self.db.fetch_one(unread_query, (p[4],))[0]
            if unread_count > 0:
                self.patient_table.setVerticalHeaderItem(row, QTableWidgetItem(f"! {unread_count} Uyarı"))
            else:
                self.patient_table.setVerticalHeaderItem(row, QTableWidgetItem(""))
        
        # Uyarı panelini güncelle
        if warnings:
            self.warning_label.setText("Kritik hastalar: " + "; ".join(warnings))
        else:
            self.warning_label.setText("")
    
    def view_patient(self, patient_tc):
        patient_detail = PatientDetailPage(self.main_window, patient_tc)
        self.main_window.stacked_widget.addWidget(patient_detail)
        self.main_window.stacked_widget.setCurrentWidget(patient_detail)
    
    def logout(self):
        self.main_window.current_user = None
        self.main_window.stacked_widget.setCurrentIndex(0)
    
    def load_profile_pic(self):
        doctor_id = self.main_window.current_user['id']
        query = "SELECT profil_resmi FROM kullanicilar WHERE id = %s"
        result = self.db.fetch_one(query, (doctor_id,))
        if result and result[0]:
            path = result[0]
            if path.startswith('http'):
                # URL ise
                from urllib.request import urlopen
                from PyQt5.QtCore import QByteArray
                try:
                    data = urlopen(path).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(data))
                    self.profile_pic_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                except Exception:
                    self.profile_pic_label.setText("Resim yüklenemedi")
            else:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self.profile_pic_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.profile_pic_label.setText("Resim yok")
        else:
            self.profile_pic_label.setText("Resim yok")
    
    def change_profile_pic(self):
        # Dosya seç veya URL gir
        choice, ok = QInputDialog.getItem(self, "Profil Resmi", "Resim ekleme yöntemi seçin:", ["Bilgisayardan Yükle", "URL Gir"], 0, False)
        if not ok:
            return
        if choice == "Bilgisayardan Yükle":
            file_path, _ = QFileDialog.getOpenFileName(self, "Profil Resmi Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
            if file_path:
                self.save_profile_pic(file_path)
        else:
            url, ok = QInputDialog.getText(self, "Profil Resmi URL", "Resim URL'si girin:")
            if ok and url:
                self.save_profile_pic(url)
    
    def save_profile_pic(self, path):
        doctor_id = self.main_window.current_user['id']
        query = "UPDATE kullanicilar SET profil_resmi = %s WHERE id = %s"
        self.db.execute_query(query, (path, doctor_id))
        self.load_profile_pic() 