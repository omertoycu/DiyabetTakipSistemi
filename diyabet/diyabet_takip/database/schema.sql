CREATE DATABASE IF NOT EXISTS diyabet_takip
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_turkish_ci;

USE diyabet_takip;

-- Kullanıcılar tablosu
CREATE TABLE IF NOT EXISTS kullanicilar (
                                            id INT AUTO_INCREMENT PRIMARY KEY,
                                            tc_kimlik VARCHAR(11) UNIQUE NOT NULL,
                                            ad VARCHAR(50) NOT NULL,
                                            soyad VARCHAR(50) NOT NULL,
                                            email VARCHAR(100) UNIQUE NOT NULL,
                                            sifre VARCHAR(255) NOT NULL,
                                            dogum_tarihi DATE NOT NULL,
                                            cinsiyet ENUM('E', 'K') NOT NULL,
                                            kullanici_tipi ENUM('doktor', 'hasta') NOT NULL,
                                            profil_resmi VARCHAR(255),
                                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doktor-Hasta ilişki tablosu
CREATE TABLE IF NOT EXISTS doktor_hasta_iliskisi (
                                                     id INT AUTO_INCREMENT PRIMARY KEY,
                                                     doktor_id INT NOT NULL,
                                                     hasta_id INT NOT NULL,
                                                     olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                     FOREIGN KEY (doktor_id) REFERENCES kullanicilar(id),
                                                     FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id),
                                                     UNIQUE KEY unique_doktor_hasta (doktor_id, hasta_id)
);

-- Kan şekeri ölçümleri tablosu
CREATE TABLE IF NOT EXISTS kan_sekeri_olcumleri (
                                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                                    hasta_id INT NOT NULL,
                                                    olcum_degeri DECIMAL(5,2) NOT NULL,
                                                    olcum_tipi ENUM('Sabah', 'Öğle', 'İkindi', 'Akşam', 'Gece') NOT NULL,
                                                    tarih TIMESTAMP NOT NULL,
                                                    notlar TEXT,
                                                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                    FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);

-- Genel kan şekeri tablosu (sadece doktor kayıt yapabilir)
CREATE TABLE IF NOT EXISTS genel_kan_sekeri (
                                                id INT AUTO_INCREMENT PRIMARY KEY,
                                                hasta_id INT NOT NULL,
                                                doktor_id INT NOT NULL,
                                                deger DECIMAL(5,2) NOT NULL,
                                                tarih DATE NOT NULL,
                                                notlar TEXT,
                                                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id),
                                                FOREIGN KEY (doktor_id) REFERENCES kullanicilar(id)
);

-- Egzersiz takibi tablosu
CREATE TABLE IF NOT EXISTS egzersiz_takibi (
                                               id INT AUTO_INCREMENT PRIMARY KEY,
                                               hasta_id INT NOT NULL,
                                               egzersiz_tipi ENUM('Yürüyüş', 'Bisiklet', 'Klinik Egzersiz') NOT NULL,
                                               tarih DATE NOT NULL,
                                               durum ENUM('Yapıldı', 'Yapılmadı') NOT NULL,
                                               olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                               FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);

-- Egzersiz önerileri tablosu
CREATE TABLE IF NOT EXISTS egzersiz_onerileri (
                                                  id INT AUTO_INCREMENT PRIMARY KEY,
                                                  hasta_id INT NOT NULL,
                                                  tarih DATE NOT NULL,
                                                  oneriler TEXT NOT NULL,
                                                  FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id),
                                                  UNIQUE KEY unique_daily_exercise (hasta_id, tarih)
);

-- Diyet takibi tablosu
CREATE TABLE IF NOT EXISTS diyet_takibi (
                                            id INT AUTO_INCREMENT PRIMARY KEY,
                                            hasta_id INT NOT NULL,
                                            ogun ENUM('Kahvaltı', 'Öğle Yemeği', 'İkindi', 'Akşam Yemeği', 'Gece') NOT NULL,
                                            tarih DATE NOT NULL,
                                            durum ENUM('Uygulandı', 'Uygulanmadı') NOT NULL,
                                            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                            FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);

-- Diyet önerileri tablosu
CREATE TABLE IF NOT EXISTS diyet_onerileri (
                                               id INT AUTO_INCREMENT PRIMARY KEY,
                                               hasta_id INT NOT NULL,
                                               tarih DATE NOT NULL,
                                               oneriler TEXT NOT NULL,
                                               FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id),
                                               UNIQUE KEY unique_daily_diet (hasta_id, tarih)
);

-- Semptom takibi tablosu
CREATE TABLE IF NOT EXISTS semptom_takibi (
                                              id INT AUTO_INCREMENT PRIMARY KEY,
                                              hasta_id INT NOT NULL,
                                              semptom ENUM(
                                                  'Nöropati', 'Polifaji', 'Yorgunluk', 'Kilo Kaybı',
                                                  'Polidipsi', 'Bulanık Görme', 'Poliüri',
                                                  'Yaraların Yavaş İyileşmesi'
                                                  ) NOT NULL,
                                              tarih DATE NOT NULL,
                                              olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                              FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);

-- Belirtiler tablosu
CREATE TABLE IF NOT EXISTS belirtiler (
                                          id INT AUTO_INCREMENT PRIMARY KEY,
                                          hasta_id INT NOT NULL,
                                          belirti_tipi ENUM(
                                              'Nöropati', 'Polifaji', 'Yorgunluk', 'Kilo Kaybı',
                                              'Polidipsi', 'Bulanık Görme', 'Poliüri',
                                              'Yaraların Yavaş İyileşmesi'
                                              ) NOT NULL,
                                          tarih DATE NOT NULL,
                                          notlar TEXT,
                                          olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                          FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);

-- İnsülin kayıtları tablosu
CREATE TABLE IF NOT EXISTS insulin_kayitlari (
                                                 id INT AUTO_INCREMENT PRIMARY KEY,
                                                 hasta_id INT NOT NULL,
                                                 doz DECIMAL(3,1) NOT NULL,
                                                 uygulama_zamani TIMESTAMP NOT NULL,
                                                 notlar TEXT,
                                                 olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                                 FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);

-- Uyarılar tablosu
CREATE TABLE IF NOT EXISTS uyarilar (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        hasta_id INT NOT NULL,
                                        uyari_tipi ENUM('Ölçüm Eksik', 'Ölçüm Yetersiz', 'Kritik Seviye') NOT NULL,
                                        mesaj TEXT NOT NULL,
                                        tarih DATETIME NOT NULL,
                                        okundu BOOLEAN DEFAULT FALSE,
                                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (hasta_id) REFERENCES kullanicilar(id)
);