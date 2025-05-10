import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QDialog, QFormLayout


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
        QMessageBox.information(self, "Hasta Detayı", f"Seçilen Hastanın T.C. Kimlik No'su: {tc}")
        # Burada hasta detaylarını gösteren yeni bir pencere açılabilir.


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
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
