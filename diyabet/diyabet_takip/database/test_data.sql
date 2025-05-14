USE diyabet_takip;

-- Önce mevcut verileri temizle
DELETE FROM doktor_hasta_iliskisi;
DELETE FROM kan_sekeri_olcumleri;
DELETE FROM egzersiz_kayitlari;
DELETE FROM diyet_kayitlari;
DELETE FROM semptom_kayitlari;
DELETE FROM belirtiler;
DELETE FROM insulin_kayitlari;
DELETE FROM uyarilar;
DELETE FROM kullanicilar;

-- Test doktoru ekle
INSERT INTO kullanicilar (tc_kimlik, ad, soyad, email, dogum_tarihi, cinsiyet, sifre, kullanici_tipi)
VALUES ('11111111111', 'Dr. Ahmet', 'Yılmaz', 'ahmet.yilmaz@example.com', '1980-01-01', 'E', '123456', 'doktor');

-- Test hastası ekle
INSERT INTO kullanicilar (tc_kimlik, ad, soyad, email, dogum_tarihi, cinsiyet, sifre, kullanici_tipi)
VALUES ('22222222222', 'Mehmet', 'Demir', 'mehmet.demir@example.com', '1990-01-01', 'E', '123456', 'hasta');

-- Doktor-Hasta ilişkisi kur
INSERT INTO doktor_hasta_iliskisi (doktor_id, hasta_id)
SELECT 
    (SELECT id FROM kullanicilar WHERE tc_kimlik = '11111111111'),
    (SELECT id FROM kullanicilar WHERE tc_kimlik = '22222222222');

-- Test verilerini kontrol et
SELECT * FROM kullanicilar;
SELECT * FROM doktor_hasta_iliskisi; 