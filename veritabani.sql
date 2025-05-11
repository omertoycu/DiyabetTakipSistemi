-- 1. Veritabanı oluşturma ve karakter seti
CREATE DATABASE IF NOT EXISTS DiyabetTakipSistemi
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_turkish_ci;

USE DiyabetTakipSistemi;

-- 2. Kullanıcılar Tablosu
CREATE TABLE IF NOT EXISTS Kullanici (
                                         kullanici_id INT AUTO_INCREMENT PRIMARY KEY,
                                         tc_kimlik_no CHAR(11) UNIQUE NOT NULL,
                                         ad_soyad VARCHAR(100) NOT NULL,
                                         sifre VARCHAR(255) NOT NULL,
                                         email VARCHAR(255) NOT NULL,
                                         dogum_tarihi DATE NOT NULL,
                                         cinsiyet ENUM('Erkek', 'Kadın') NOT NULL,
                                         rol ENUM('Doktor', 'Hasta') NOT NULL -- Kullanıcı rolü eklendi
);

-- 3. Doktorlar Tablosu
CREATE TABLE IF NOT EXISTS Doktor (
                                      doktor_id INT AUTO_INCREMENT PRIMARY KEY,
                                      kullanici_id INT NOT NULL, -- Foreign Key
                                      FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. Hastalar Tablosu
CREATE TABLE IF NOT EXISTS Hasta (
                                     hasta_id INT AUTO_INCREMENT PRIMARY KEY,
                                     doktor_id INT NOT NULL, -- Hasta bir doktora bağlı
                                     kullanici_id INT NOT NULL, -- Foreign Key
                                     FOREIGN KEY (doktor_id) REFERENCES Doktor(doktor_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                     FOREIGN KEY (kullanici_id) REFERENCES Kullanici(kullanici_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS KanSekeriOlcum (
                                              olcum_id INT AUTO_INCREMENT PRIMARY KEY,
                                              hasta_id INT NOT NULL, -- Foreign Key
                                              olcum_tarihi DATETIME NOT NULL,
                                              saat_dilimi VARCHAR(50) NOT NULL, -- Yeni sütun
                                              kan_sekeri_degeri DECIMAL(5, 2) NOT NULL,
                                              FOREIGN KEY (hasta_id) REFERENCES Hasta(hasta_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 6. Diyet Türleri Tablosu
CREATE TABLE IF NOT EXISTS Diyet (
                                     diyet_id INT AUTO_INCREMENT PRIMARY KEY,
                                     diyet_adi VARCHAR(50) NOT NULL,
                                     aciklama TEXT
);

-- 7. Egzersiz Türleri Tablosu
CREATE TABLE IF NOT EXISTS Egzersiz (
                                        egzersiz_id INT AUTO_INCREMENT PRIMARY KEY,
                                        egzersiz_adi VARCHAR(50) NOT NULL,
                                        aciklama TEXT
);

-- 8. Hasta-Diyet-Egzersiz Takip Tablosu
CREATE TABLE IF NOT EXISTS HastaDiyetEgzersizTakip (
                                                       takip_id INT AUTO_INCREMENT PRIMARY KEY,
                                                       hasta_id INT NOT NULL,
                                                       diyet_id INT,
                                                       egzersiz_id INT,
                                                       durum ENUM('uygulandı', 'uygulanmadı', 'yapıldı', 'yapılmadı') NOT NULL,
                                                       FOREIGN KEY (hasta_id) REFERENCES Hasta(hasta_id) ON DELETE CASCADE ON UPDATE CASCADE,
                                                       FOREIGN KEY (diyet_id) REFERENCES Diyet(diyet_id) ON DELETE SET NULL ON UPDATE CASCADE,
                                                       FOREIGN KEY (egzersiz_id) REFERENCES Egzersiz(egzersiz_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 9. Belirtiler Tablosu
CREATE TABLE IF NOT EXISTS Belirti (
                                       belirti_id INT AUTO_INCREMENT PRIMARY KEY,
                                       belirti_adi VARCHAR(50) NOT NULL,
                                       aciklama TEXT
);

-- 10. Uyarılar Tablosu
CREATE TABLE IF NOT EXISTS Uyari (
                                     uyari_id INT AUTO_INCREMENT PRIMARY KEY,
                                     hasta_id INT NOT NULL,
                                     uyari_tipi VARCHAR(50) NOT NULL,
                                     mesaj TEXT NOT NULL,
                                     tarih DATETIME NOT NULL,
                                     FOREIGN KEY (hasta_id) REFERENCES Hasta(hasta_id) ON DELETE CASCADE ON UPDATE CASCADE
);

