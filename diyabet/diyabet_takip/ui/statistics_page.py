from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QDateEdit, QPushButton
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database.db_connection import DatabaseConnection
from datetime import datetime, timedelta
import pytz


class StatisticsPage(QWidget):
    def __init__(self, main_window, patient_id):
        super().__init__()
        self.main_window = main_window
        self.patient_id = patient_id
        self.db = DatabaseConnection()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("İstatistikler ve İlişki Grafiği")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tarih aralığı seçici
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Başlangıç:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-6))
        date_row.addWidget(self.start_date)
        date_row.addWidget(QLabel("Bitiş:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_row.addWidget(self.end_date)
        show_btn = QPushButton("Göster")
        show_btn.clicked.connect(self.update_stats)
        date_row.addWidget(show_btn)
        layout.addLayout(date_row)


        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        layout.addWidget(self.stats_label)

        # Grafik
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.update_stats()

    def update_stats(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        # Diyet uygulama oranı
        diet_query = """
            SELECT COUNT(*) FROM diyet_takibi WHERE hasta_id = %s AND tarih BETWEEN %s AND %s
        """
        applied_query = """
            SELECT COUNT(*) FROM diyet_takibi WHERE hasta_id = %s AND tarih BETWEEN %s AND %s AND durum = 'Uygulandı'
        """
        total_diet = self.db.fetch_one(diet_query, (self.patient_id, start, end))[0]
        applied_diet = self.db.fetch_one(applied_query, (self.patient_id, start, end))[0]
        diet_percent = (applied_diet / total_diet * 100) if total_diet else 0

        # Egzersiz uygulama oranı
        ex_query = """
            SELECT COUNT(*) FROM egzersiz_takibi WHERE hasta_id = %s AND tarih BETWEEN %s AND %s
        """
        ex_applied_query = """
            SELECT COUNT(*) FROM egzersiz_takibi WHERE hasta_id = %s AND tarih BETWEEN %s AND %s AND durum = 'Yapıldı'
        """
        total_ex = self.db.fetch_one(ex_query, (self.patient_id, start, end))[0]
        applied_ex = self.db.fetch_one(ex_applied_query, (self.patient_id, start, end))[0]
        ex_percent = (applied_ex / total_ex * 100) if total_ex else 0

        # İstatistik etiketini güncelle
        stats_text = f"""
        <div style='text-align: center;'>
            <p><b>Diyet Uygulama Oranı:</b> %{diet_percent:.1f}</p>
            <p><b>Egzersiz Uygulama Oranı:</b> %{ex_percent:.1f}</p>
        </div>
        """
        self.stats_label.setText(stats_text)

        # Grafiği güncelle
        self.plot_graph()

    def plot_graph(self):
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            turkey_tz = pytz.timezone('Europe/Istanbul')

            # Kan şekeri ölçümleri (tarih, vakit, değer)
            query = """
                SELECT tarih, olcum_tipi, olcum_degeri 
                FROM kan_sekeri_olcumleri 
                WHERE hasta_id = %s AND DATE(tarih) BETWEEN %s AND %s 
                ORDER BY tarih ASC
            """
            results = self.db.fetch_all(query, (self.patient_id, start_date, end_date))
            if not results:
                self.show_no_data_message()
                return

            sugar_points = []  # (datetime, vakit, değer)
            for tarih, vakit, deger in results:

                if isinstance(tarih, str):
                    try:
                        tarih = datetime.strptime(tarih, '%Y-%m-%d %H:%M:%S')
                    except:
                        tarih = datetime.strptime(tarih, '%Y-%m-%d')
                if tarih.tzinfo is None:
                    tarih = turkey_tz.localize(tarih)
                sugar_points.append((tarih, vakit, deger))


            diet_query = """
                SELECT tarih FROM diyet_takibi 
                WHERE hasta_id = %s AND tarih BETWEEN %s AND %s AND durum = 'Uygulandı'
            """
            diet_days = set(d[0] for d in self.db.fetch_all(diet_query, (self.patient_id, start_date, end_date)))


            ex_query = """
                SELECT tarih FROM egzersiz_takibi 
                WHERE hasta_id = %s AND tarih BETWEEN %s AND %s AND durum = 'Yapıldı'
            """
            ex_days = set(d[0] for d in self.db.fetch_all(ex_query, (self.patient_id, start_date, end_date)))

            # Grafik verileri
            x = list(range(len(sugar_points)))
            y = []  # kan şekeri
            gunler = []
            x_labels = []
            for idx, (tarih, vakit, deger) in enumerate(sugar_points):
                y.append(deger)
                gunler.append(tarih.date())
                x_labels.append(tarih.strftime('%d.%m.%Y') + '\n' + vakit)

            fig = self.canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            # Kan şekeri çizgisi
            ax.plot(x, y, 'b-', label='Kan Şekeri (mg/dL)', linewidth=2)
            ax.scatter(x, y, color='blue', s=50)


            min_y = min(y) if y else 50
            islenmis_gunler = set()
            for i, (val, gun) in enumerate(zip(y, gunler)):
                if gun in diet_days and gun not in islenmis_gunler:
                    ax.scatter(x[i], min_y-10, color='green', marker='s', s=120, label='Diyet Uygulandı' if i==0 else "")
                    islenmis_gunler.add(gun)


            islenmis_gunler_ex = set()
            for i, (val, gun) in enumerate(zip(y, gunler)):
                if gun in ex_days and gun not in islenmis_gunler_ex:
                    ax.scatter(x[i], min_y-25, color='orange', marker='v', s=120, label='Egzersiz Yapıldı' if i==0 else "")
                    islenmis_gunler_ex.add(gun)


            handles, labels = ax.get_legend_handles_labels()
            unique = dict(zip(labels, handles))
            ax.legend(unique.values(), unique.keys(), loc='upper right')

            ax.set_title('Kan Şekeri, Diyet ve Egzersiz İlişkisi', pad=20)
            ax.set_xlabel('Tarih ve Vakit')
            ax.set_ylabel('Kan Şekeri (mg/dL)')
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xticks(x)
            ax.set_xticklabels(x_labels, rotation=90, ha='center', fontsize=9)
            fig.subplots_adjust(bottom=0.28)
            if y:
                ax.set_ylim(min(y)-40, max(y)+30)
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            self.canvas.draw()
        except Exception as e:
            self.show_no_data_message()

    def show_no_data_message(self):
        self.stats_label.setText("Seçilen tarih aralığında veri bulunamadı")
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Seçilen tarih aralığında veri bulunamadı',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw() 