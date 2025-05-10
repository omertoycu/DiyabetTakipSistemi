import sys
import mysql.connector
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QMessageBox, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QCheckBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class NewPatientDialog(QDialog):
    def __init__(self, doctor_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Hasta Ekle")
        self.setGeometry(150, 150, 400, 300)
        self.doctor_id = doctor_id

        # Form alanları
        layout = QFormLayout()
        self.tc_input = QLineEdit()
        self.name_input = QLineEdit()
        self.birth_date_input = QLineEdit()
        self.gender_input = QLineEdit()
        layout.addRow("T.C. Kimlik No:", self.tc_input)
        layout.addRow("Ad Soyad:", self.name_input)
        layout.addRow("Doğum Tarihi (YYYY-AA-GG):", self.birth_date_input)
        layout.addRow("Cinsiyet:", self.gender_input)

        # Kaydet Butonu
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_patient)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_patient(self):
        tc = self.tc_input.text()
        name = self.name_input.text()
        birth_date = self.birth_date_input.text()
        gender = self.gender_input.text()

        if not tc or not name or not birth_date or not gender:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="145323",
                database="DiyabetTakipSistemi"
            )
            cursor = connection.cursor()

            # Kullanıcı tablosuna ekle
            add_user_query = """
                INSERT INTO Kullanici (tc_kimlik_no, ad_soyad, sifre, email, dogum_tarihi, cinsiyet, rol)
                VALUES (%s, %s, %s, %s, %s, %s, 'Hasta')
            """
            cursor.execute(add_user_query, (tc, name, tc, f"{tc}@example.com", birth_date, gender))
            user_id = cursor.lastrowid  # Kullanıcı ID'sini al

            # Hasta tablosuna ekle
            add_patient_query = """
                INSERT INTO Hasta (doktor_id, kullanici_id)
                VALUES (%s, %s)
            """
            cursor.execute(add_patient_query, (self.doctor_id, user_id))
            connection.commit()

            cursor.close()
            connection.close()
            QMessageBox.information(self, "Başarılı", "Yeni hasta kaydedildi!")
            self.accept()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Hata: {err}")


class PatientDetailWindow(QWidget):
    def __init__(self, tc):
        super().__init__()
        self.tc = tc
        self.setWindowTitle(f"Hasta Detayları - {self.tc}")
        self.setGeometry(100, 100, 800, 800)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Başlık
        self.title = QLabel(f"Hasta T.C.: {self.tc}")
        layout.addWidget(self.title)

        # Kan Şekeri Ölçüm Tablosu
        self.blood_sugar_table = QTableWidget()
        self.blood_sugar_table.setColumnCount(2)  # Saat Dilimi ve Kan Şekeri Değeri
        self.blood_sugar_table.setHorizontalHeaderLabels(["Saat Dilimi", "Kan Şekeri Değeri"])
        layout.addWidget(self.blood_sugar_table)

        # Kan Şekeri Grafiği
        self.graph_canvas = FigureCanvas(plt.figure())
        layout.addWidget(self.graph_canvas)

        # Kan Şekeri Giriş Formu
        form_layout = QFormLayout()

        # Ölçüm Saatleri
        self.time_selector = QComboBox()
        self.time_selector.addItems([
            "Sabah (07:00-08:00)", "Öğlen (12:00-13:00)",
            "İkindi (15:00-16:00)", "Akşam (18:00-19:00)",
            "Gece (22:00-23:00)"
        ])
        form_layout.addRow("Ölçüm Saatini Seçin:", self.time_selector)

        # Kan Şekeri Değeri
        self.blood_sugar_input = QLineEdit()
        form_layout.addRow("Kan Şekeri Değeri (mg/dL):", self.blood_sugar_input)

        # Kaydet Butonu
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_blood_sugar)
        form_layout.addWidget(self.save_button)

        layout.addLayout(form_layout)

        # Belirtiler
        self.symptoms_layout = QVBoxLayout()
        self.symptom_checkboxes = {}
        symptoms = [
            "Poliüri", "Polifaji", "Polidipsi", "Nöropati",
            "Kilo kaybı", "Yorgunluk", "Yaraların yavaş iyileşmesi", "Bulanık görme"
        ]
        for symptom in symptoms:
            checkbox = QCheckBox(symptom)
            self.symptoms_layout.addWidget(checkbox)
            self.symptom_checkboxes[symptom] = checkbox

        symptoms_widget = QWidget()
        symptoms_widget.setLayout(self.symptoms_layout)
        layout.addWidget(QLabel("Belirtiler:"))
        layout.addWidget(symptoms_widget)

        # Diyet ve Egzersiz Önerileri
        self.diet_label = QLabel("Diyet Önerisi: -")
        layout.addWidget(self.diet_label)
        self.exercise_label = QLabel("Egzersiz Önerisi: -")
        layout.addWidget(self.exercise_label)

        # Ortalama Kan Şekeri
        self.average_label = QLabel("Günlük Ortalama Kan Şekeri: Henüz hesaplanmadı")
        layout.addWidget(self.average_label)

        self.setLayout(layout)
        self.load_blood_sugar_data()

    def save_blood_sugar(self):
        selected_time = self.time_selector.currentText().split(" ")[0]
        blood_sugar_value = self.blood_sugar_input.text()

        if not blood_sugar_value.isdigit():
            QMessageBox.warning(self, "Hata", "Kan şekeri değeri geçerli bir sayı olmalıdır!")
            return

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="145323",
                database="DiyabetTakipSistemi"
            )
            cursor = connection.cursor()

            # Hasta ID'sini al
            cursor.execute("""
                SELECT hasta_id FROM Kullanici k
                JOIN Hasta h ON k.kullanici_id = h.kullanici_id
                WHERE tc_kimlik_no = %s
            """, (self.tc,))
            result = cursor.fetchone()
            if not result:
                QMessageBox.critical(self, "Hata", "Hasta bulunamadı!")
                return
            patient_id = result[0]

            # Aynı saat diliminde zaten bir ölçüm varsa güncelle
            cursor.execute("""
                SELECT * FROM KanSekeriOlcum
                WHERE hasta_id = %s AND DATE(olcum_tarihi) = CURDATE() AND saat_dilimi = %s
            """, (patient_id, selected_time))
            existing_measurement = cursor.fetchone()

            if existing_measurement:
                cursor.execute("""
                    UPDATE KanSekeriOlcum
                    SET kan_sekeri_degeri = %s
                    WHERE hasta_id = %s AND DATE(olcum_tarihi) = CURDATE() AND saat_dilimi = %s
                """, (blood_sugar_value, patient_id, selected_time))
                QMessageBox.information(self, "Başarılı", "Ölçüm güncellendi!")
            else:
                cursor.execute("""
                    INSERT INTO KanSekeriOlcum (hasta_id, olcum_tarihi, saat_dilimi, kan_sekeri_degeri)
                    VALUES (%s, NOW(), %s, %s)
                """, (patient_id, selected_time, blood_sugar_value))
                QMessageBox.information(self, "Başarılı", "Ölçüm kaydedildi!")

            connection.commit()
            self.load_blood_sugar_data()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Hata: {err}")
        finally:
            cursor.close()
            connection.close()

    def load_blood_sugar_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="145323",
                database="DiyabetTakipSistemi"
            )
            cursor = connection.cursor()

            # Hasta ID'sini al
            cursor.execute("""
                SELECT hasta_id FROM Kullanici k
                JOIN Hasta h ON k.kullanici_id = h.kullanici_id
                WHERE tc_kimlik_no = %s
            """, (self.tc,))
            result = cursor.fetchone()
            if not result:
                QMessageBox.critical(self, "Hata", "Hasta bulunamadı!")
                return
            patient_id = result[0]

            # Kan şekeri ölçümlerini getir
            cursor.execute("""
                SELECT saat_dilimi, kan_sekeri_degeri
                FROM KanSekeriOlcum
                WHERE hasta_id = %s AND DATE(olcum_tarihi) = CURDATE()
            """, (patient_id,))
            measurements = cursor.fetchall()

            self.blood_sugar_table.setRowCount(len(measurements))
            total = 0
            count = 0
            times = []
            values = []

            for row_idx, (time_slot, value) in enumerate(measurements):
                self.blood_sugar_table.setItem(row_idx, 0, QTableWidgetItem(time_slot))
                self.blood_sugar_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))
                times.append(time_slot)
                values.append(value)
                total += value
                count += 1

            # Ortalama hesaplama
            if count > 0:
                average = total / count
                self.average_label.setText(f"Günlük Ortalama Kan Şekeri: {average:.2f} mg/dL")
                self.generate_recommendations(average)
            else:
                self.average_label.setText("Günlük Ortalama Kan Şekeri: Henüz ölçüm yok")

            # Kan şekeri grafiğini güncelle
            if values:
                ax = self.graph_canvas.figure.add_subplot(111)
                ax.clear()
                ax.bar(times, values, color='blue')
                ax.set_title("Günlük Kan Şekeri Değişimi")
                ax.set_xlabel("Saat Dilimi")
                ax.set_ylabel("Kan Şekeri Değeri (mg/dL)")
                self.graph_canvas.draw()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Hata: {err}")
        finally:
            cursor.close()
            connection.close()

    def generate_recommendations(self, average):
        """Generate diet and exercise recommendations based on average blood sugar."""
        selected_symptoms = [symptom for symptom, checkbox in self.symptom_checkboxes.items() if checkbox.isChecked()]

        # Belirtiler ve kan şekeri seviyesine göre öneriler
        if average < 70 and any(symptom in selected_symptoms for symptom in ["Nöropati", "Polifaji", "Yorgunluk"]):
            self.diet_label.setText("Diyet Önerisi: Dengeli Beslenme")
            self.exercise_label.setText("Egzersiz Önerisi: Yok")
        elif 70 <= average <= 110 and "Yorgunluk" in selected_symptoms and "Kilo kaybı" in selected_symptoms:
            self.diet_label.setText("Diyet Önerisi: Az Şekerli Diyet")
            self.exercise_label.setText("Egzersiz Önerisi: Yürüyüş")
        elif 70 <= average <= 110 and "Polifaji" in selected_symptoms and "Polidipsi" in selected_symptoms:
            self.diet_label.setText("Diyet Önerisi: Dengeli Beslenme")
            self.exercise_label.setText("Egzersiz Önerisi: Yürüyüş")
        elif 110 <= average <= 180 and "Bulanık görme" in selected_symptoms and "Nöropati" in selected_symptoms:
            self.diet_label.setText("Diyet Önerisi: Az Şekerli Diyet")
            self.exercise_label.setText("Egzersiz Önerisi: Klinik Egzersiz")
        elif 110 <= average <= 180 and "Poliüri" in selected_symptoms and "Polidipsi" in selected_symptoms:
            self.diet_label.setText("Diyet Önerisi: Şekersiz Diyet")
            self.exercise_label.setText("Egzersiz Önerisi: Klinik Egzersiz")
        elif 110 <= average <= 180 and all(symptom in selected_symptoms for symptom in ["Yorgunluk", "Nöropati", "Bulanık görme"]):
            self.diet_label.setText("Diyet Önerisi: Az Şekerli Diyet")
            self.exercise_label.setText("Egzersiz Önerisi: Yürüyüş")
        elif average > 180 and all(symptom in selected_symptoms for symptom in ["Yaraların yavaş iyileşmesi", "Polifaji", "Polidipsi"]):
            self.diet_label.setText("Diyet Önerisi: Şekersiz Diyet")
            self.exercise_label.setText("Egzersiz Önerisi: Klinik Egzersiz")
        elif average > 180 and all(symptom in selected_symptoms for symptom in ["Yaraların yavaş iyileşmesi", "Kilo kaybı"]):
            self.diet_label.setText("Diyet Önerisi: Şekersiz Diyet")
            self.exercise_label.setText("Egzersiz Önerisi: Yürüyüş")
        else:
            self.diet_label.setText("Diyet Önerisi: -")
            self.exercise_label.setText("Egzersiz Önerisi: -")


class DoctorWindow(QWidget):
    def __init__(self, doctor_id):
        super().__init__()
        self.setWindowTitle("Doktor Paneli")
        self.setGeometry(100, 100, 600, 400)
        self.doctor_id = doctor_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Başlık
        self.title = QLabel("Takip Ettiğiniz Hastalar")
        layout.addWidget(self.title)

        # Hasta Listesi Tablosu
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(3)  # T.C., Ad Soyad, Detay
        self.patient_table.setHorizontalHeaderLabels(["T.C. Kimlik No", "Ad Soyad", "Detay"])
        layout.addWidget(self.patient_table)

        # Yeni Hasta Ekle Butonu
        self.add_patient_button = QPushButton("Yeni Hasta Ekle")
        self.add_patient_button.clicked.connect(self.open_new_patient_dialog)
        layout.addWidget(self.add_patient_button)

        # Veritabanından hastaları getirme
        self.load_patients()

        self.setLayout(layout)

    def load_patients(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="145323",
                database="DiyabetTakipSistemi"
            )
            cursor = connection.cursor()
            query = """
                SELECT k.tc_kimlik_no, k.ad_soyad
                FROM Hasta h
                JOIN Kullanici k ON h.kullanici_id = k.kullanici_id
                WHERE h.doktor_id = %s
            """
            cursor.execute(query, (self.doctor_id,))
            patients = cursor.fetchall()

            self.patient_table.setRowCount(len(patients))
            for row_idx, (tc, name) in enumerate(patients):
                self.patient_table.setItem(row_idx, 0, QTableWidgetItem(tc))
                self.patient_table.setItem(row_idx, 1, QTableWidgetItem(name))

                # Detay Butonu
                detail_button = QPushButton("Detay")
                detail_button.clicked.connect(self.create_detail_callback(tc))
                self.patient_table.setCellWidget(row_idx, 2, detail_button)

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Hata: {err}")

    def create_detail_callback(self, tc):
        # Lambda hatasını önlemek için bir fonksiyon oluşturuyoruz
        def detail_callback():
            self.show_patient_details(tc)
        return detail_callback

    def open_new_patient_dialog(self):
        dialog = NewPatientDialog(self.doctor_id, self)
        if dialog.exec_():
            self.load_patients()  # Yeni hasta eklendiğinde listeyi yenile

    def show_patient_details(self, tc):
        self.detail_window = PatientDetailWindow(tc)
        self.detail_window.show()


class PatientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hasta Paneli")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Hasta Paneline Hoş Geldiniz!"))
        self.setLayout(layout)


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Diyabet Takip Sistemi - Giriş")
        self.setGeometry(100, 100, 400, 300)

        self.label_tc = QLabel("T.C. Kimlik No:", self)
        self.label_tc.move(50, 50)
        self.input_tc = QLineEdit(self)
        self.input_tc.move(150, 50)
        self.input_tc.setPlaceholderText("T.C. Kimlik Numaranızı Girin")

        self.label_password = QLabel("Şifre:", self)
        self.label_password.move(50, 100)
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.move(150, 100)
        self.input_password.setPlaceholderText("Şifrenizi Girin")

        self.login_button = QPushButton("Giriş Yap", self)
        self.login_button.move(150, 150)
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        tc = self.input_tc.text()
        password = self.input_password.text()

        if not tc or not password:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="145323",
                database="DiyabetTakipSistemi"
            )
            cursor = connection.cursor()
            query = "SELECT sifre, rol, kullanici_id FROM Kullanici WHERE tc_kimlik_no = %s"
            cursor.execute(query, (tc,))
            result = cursor.fetchone()

            if result:
                stored_password, role, user_id = result
                if password == stored_password:
                    QMessageBox.information(self, "Başarılı", f"Giriş Başarılı! Rol: {role}")
                    self.open_panel(role, user_id)
                else:
                    QMessageBox.critical(self, "Hata", "Şifre hatalı!")
            else:
                QMessageBox.critical(self, "Hata", "Kullanıcı bulunamadı!")

            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Hata: {err}")

    def open_panel(self, role, user_id):
        if role == "Doktor":
            self.doctor_window = DoctorWindow(user_id)
            self.doctor_window.show()
            self.close()
        elif role == "Hasta":
            self.patient_window = PatientWindow()
            self.patient_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Hata", "Tanımsız rol!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
