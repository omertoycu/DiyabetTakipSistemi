# Diyabet Takip Sistemi

Bu proje, diyabet hastalarının sağlık verilerini etkili bir biçimde izlemek, yorumlamak ve hem hastaya hem de hekime zamanında uyarılar sağlamak amacıyla geliştirilmiştir.

## Özellikler

- Doktor ve hasta girişi
- Kan şekeri takibi
- Egzersiz ve diyet takibi
- Belirti takibi
- Otomatik uyarı sistemi
- Detaylı raporlama
- Grafiksel veri analizi

## Gereksinimler

- Python 3.8+
- MySQL 8.0+
- PyQt5
- Diğer bağımlılıklar (requirements.txt dosyasında listelenmiştir)

## Kurulum

1. Projeyi klonlayın:
```bash
git clone [proje-url]
cd diyabet_takip
```

2. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

3. MySQL veritabanını oluşturun:
```bash
mysql -u root -p < database/schema.sql
```

4. Uygulamayı başlatın:
```bash
python main.py
```

## Kullanım

1. Uygulama başlatıldığında giriş ekranı açılır
2. TC Kimlik No ve şifre ile giriş yapın
3. Kullanıcı tipine göre (doktor/hasta) ilgili panele yönlendirilirsiniz
4. Sol menüden istediğiniz işlemi seçin

## Veritabanı Yapısı

Veritabanı şeması `database/schema.sql` dosyasında tanımlanmıştır. Temel tablolar:

- kullanicilar
- doktor_hasta
- kan_sekeri_olcumleri
- egzersiz_kayitlari
- diyet_kayitlari
- belirtiler
- insulin_kayitlari
- uyarilar

## Güvenlik

- Şifreler bcrypt ile hashlenerek saklanır
- Veritabanı bağlantısı SSL/TLS ile şifrelenir
- Kullanıcı yetkilendirmesi rol tabanlıdır

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 