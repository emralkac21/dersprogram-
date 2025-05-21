#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı bağlantı ve işlem sınıfı
"""

import os
import sqlite3
import logging
from datetime import datetime

class Database:
    """
    SQLite veritabanı bağlantı ve işlem sınıfı
    """
    
    def __init__(self, db_path):
        """
        Veritabanı bağlantısını başlatır
        
        Args:
            db_path (str): Veritabanı dosya yolu
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)
        
        # Veritabanı dizini yoksa oluştur
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Bağlantıyı oluştur
        self.connect()
        
        # Tabloları oluştur
        self.create_tables()
    
    def connect(self):
        """
        Veritabanına bağlanır
        """
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Sonuçları sözlük olarak al
            self.cursor = self.conn.cursor()
            self.logger.info(f"Veritabanına bağlantı başarılı: {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Veritabanı bağlantı hatası: {str(e)}")
            raise
    
    def close(self):
        """
        Veritabanı bağlantısını kapatır
        """
        if self.conn:
            self.conn.close()
            self.logger.info("Veritabanı bağlantısı kapatıldı")
    
    def commit(self):
        """
        Değişiklikleri kaydeder
        """
        if self.conn:
            self.conn.commit()
    
    def create_tables(self):
        """
        Veritabanı tablolarını oluşturur
        """
        try:
            # Sınıflar tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS siniflar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    sube TEXT NOT NULL,
                    haftalik_toplam_saat INTEGER NOT NULL,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ad, sube)
                )
            ''')
            
            # Öğretmenler tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ogretmenler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_soyad TEXT NOT NULL,
                    brans TEXT NOT NULL,
                    haftalik_ders_saati INTEGER NOT NULL,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ad_soyad)
                )
            ''')
            
            # Dersler tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dersler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    haftalik_saat INTEGER NOT NULL,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ad)
                )
            ''')
            
            # Derslikler tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS derslikler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad TEXT NOT NULL,
                    tur TEXT NOT NULL DEFAULT 'normal',
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ad)
                )
            ''')
            
            # Ders-Sınıf ilişki tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ders_sinif (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ders_id INTEGER NOT NULL,
                    sinif_id INTEGER NOT NULL,
                    ogretmen_id INTEGER NOT NULL,
                    haftalik_saat INTEGER NOT NULL,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ders_id) REFERENCES dersler(id) ON DELETE CASCADE,
                    FOREIGN KEY (sinif_id) REFERENCES siniflar(id) ON DELETE CASCADE,
                    FOREIGN KEY (ogretmen_id) REFERENCES ogretmenler(id) ON DELETE CASCADE,
                    UNIQUE(ders_id, sinif_id, ogretmen_id)
                )
            ''')
            
            # Uygun olmayan zamanlar tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS uygun_olmayan_zamanlar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ogretmen_id INTEGER NOT NULL,
                    gun INTEGER NOT NULL,  -- 0: Pazartesi, 1: Salı, ...
                    saat_baslangic INTEGER NOT NULL,
                    saat_bitis INTEGER NOT NULL,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ogretmen_id) REFERENCES ogretmenler(id) ON DELETE CASCADE
                )
            ''')
            
            # Program tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS program (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sinif_id INTEGER NOT NULL,
                    ogretmen_id INTEGER NOT NULL,
                    ders_id INTEGER NOT NULL,
                    derslik_id INTEGER,
                    gun INTEGER NOT NULL,  -- 0: Pazartesi, 1: Salı, ...
                    saat INTEGER NOT NULL,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sinif_id) REFERENCES siniflar(id) ON DELETE CASCADE,
                    FOREIGN KEY (ogretmen_id) REFERENCES ogretmenler(id) ON DELETE CASCADE,
                    FOREIGN KEY (ders_id) REFERENCES dersler(id) ON DELETE CASCADE,
                    FOREIGN KEY (derslik_id) REFERENCES derslikler(id) ON DELETE SET NULL
                )
            ''')
            
            # Ayarlar tablosu
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ayarlar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anahtar TEXT NOT NULL,
                    deger TEXT NOT NULL,
                    aciklama TEXT,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(anahtar)
                )
            ''')
            
            # Varsayılan ayarları ekle
            self.cursor.execute('''
                INSERT OR IGNORE INTO ayarlar (anahtar, deger, aciklama)
                VALUES 
                ('ders_suresi', '40', 'Ders süresi (dakika)'),
                ('gunluk_ders_baslangic', '8:30', 'Günlük ders başlangıç saati'),
                ('gunluk_ders_bitis', '16:00', 'Günlük ders bitiş saati'),
                ('ogle_arasi_baslangic', '12:00', 'Öğle arası başlangıç saati'),
                ('ogle_arasi_bitis', '13:00', 'Öğle arası bitiş saati'),
                ('teneffus_suresi', '10', 'Teneffüs süresi (dakika)'),
                ('max_gunluk_ders', '8', 'Günlük maksimum ders saati'),
                ('max_haftalik_ders', '40', 'Haftalık maksimum ders saati')
            ''')
            
            self.commit()
            self.logger.info("Veritabanı tabloları başarıyla oluşturuldu")
        except sqlite3.Error as e:
            self.logger.error(f"Tablo oluşturma hatası: {str(e)}")
            raise
    
    def execute(self, query, params=None):
        """
        SQL sorgusu çalıştırır
        
        Args:
            query (str): SQL sorgusu
            params (tuple, optional): Sorgu parametreleri
            
        Returns:
            cursor: Sorgu sonucu
        """
        try:
            if params:
                return self.cursor.execute(query, params)
            else:
                return self.cursor.execute(query)
        except sqlite3.Error as e:
            self.logger.error(f"Sorgu hatası: {str(e)}")
            self.logger.error(f"Sorgu: {query}")
            self.logger.error(f"Parametreler: {params}")
            raise
    
    def fetchall(self):
        """
        Tüm sonuçları döndürür
        
        Returns:
            list: Sonuç listesi
        """
        return self.cursor.fetchall()
    
    def fetchone(self):
        """
        Tek bir sonuç döndürür
        
        Returns:
            dict: Sonuç
        """
        return self.cursor.fetchone()
    
    def lastrowid(self):
        """
        Son eklenen kaydın ID'sini döndürür
        
        Returns:
            int: Son eklenen kaydın ID'si
        """
        return self.cursor.lastrowid
    
    # Sınıf işlemleri
    def sinif_ekle(self, ad, sube, haftalik_toplam_saat):
        """
        Yeni sınıf ekler
        
        Args:
            ad (str): Sınıf adı
            sube (str): Şube
            haftalik_toplam_saat (int): Haftalık toplam ders saati
            
        Returns:
            int: Eklenen sınıfın ID'si
        """
        try:
            self.execute(
                "INSERT INTO siniflar (ad, sube, haftalik_toplam_saat) VALUES (?, ?, ?)",
                (ad, sube, haftalik_toplam_saat)
            )
            self.commit()
            return self.lastrowid()
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu sınıf zaten mevcut: {ad} {sube}")
            raise ValueError(f"Bu sınıf zaten mevcut: {ad} {sube}")
    
    def sinif_guncelle(self, id, ad, sube, haftalik_toplam_saat):
        """
        Sınıf bilgilerini günceller
        
        Args:
            id (int): Sınıf ID'si
            ad (str): Sınıf adı
            sube (str): Şube
            haftalik_toplam_saat (int): Haftalık toplam ders saati
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            self.execute(
                "UPDATE siniflar SET ad=?, sube=?, haftalik_toplam_saat=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
                (ad, sube, haftalik_toplam_saat, id)
            )
            self.commit()
            return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu sınıf zaten mevcut: {ad} {sube}")
            raise ValueError(f"Bu sınıf zaten mevcut: {ad} {sube}")
    
    def sinif_sil(self, id):
        """
        Sınıfı siler
        
        Args:
            id (int): Sınıf ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM siniflar WHERE id=?", (id,))
        self.commit()
        return True
    
    def sinif_getir(self, id):
        """
        Sınıf bilgilerini getirir
        
        Args:
            id (int): Sınıf ID'si
            
        Returns:
            dict: Sınıf bilgileri
        """
        self.execute("SELECT * FROM siniflar WHERE id=?", (id,))
        return self.fetchone()
    
    def tum_siniflari_getir(self):
        """
        Tüm sınıfları getirir
        
        Returns:
            list: Sınıf listesi
        """
        self.execute("SELECT * FROM siniflar ORDER BY ad, sube")
        return self.fetchall()
    
    # Öğretmen işlemleri
    def ogretmen_ekle(self, ad_soyad, brans, haftalik_ders_saati):
        """
        Yeni öğretmen ekler
        
        Args:
            ad_soyad (str): Ad Soyad
            brans (str): Branş
            haftalik_ders_saati (int): Haftalık ders saati
            
        Returns:
            int: Eklenen öğretmenin ID'si
        """
        try:
            self.execute(
                "INSERT INTO ogretmenler (ad_soyad, brans, haftalik_ders_saati) VALUES (?, ?, ?)",
                (ad_soyad, brans, haftalik_ders_saati)
            )
            self.commit()
            return self.lastrowid()
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu öğretmen zaten mevcut: {ad_soyad}")
            raise ValueError(f"Bu öğretmen zaten mevcut: {ad_soyad}")
    
    def ogretmen_guncelle(self, id, ad_soyad, brans, haftalik_ders_saati):
        """
        Öğretmen bilgilerini günceller
        
        Args:
            id (int): Öğretmen ID'si
            ad_soyad (str): Ad Soyad
            brans (str): Branş
            haftalik_ders_saati (int): Haftalık ders saati
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            self.execute(
                "UPDATE ogretmenler SET ad_soyad=?, brans=?, haftalik_ders_saati=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
                (ad_soyad, brans, haftalik_ders_saati, id)
            )
            self.commit()
            return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu öğretmen zaten mevcut: {ad_soyad}")
            raise ValueError(f"Bu öğretmen zaten mevcut: {ad_soyad}")
    
    def ogretmen_sil(self, id):
        """
        Öğretmeni siler
        
        Args:
            id (int): Öğretmen ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM ogretmenler WHERE id=?", (id,))
        self.commit()
        return True
    
    def ogretmen_getir(self, id):
        """
        Öğretmen bilgilerini getirir
        
        Args:
            id (int): Öğretmen ID'si
            
        Returns:
            dict: Öğretmen bilgileri
        """
        self.execute("SELECT * FROM ogretmenler WHERE id=?", (id,))
        return self.fetchone()
    
    def tum_ogretmenleri_getir(self):
        """
        Tüm öğretmenleri getirir
        
        Returns:
            list: Öğretmen listesi
        """
        self.execute("SELECT * FROM ogretmenler ORDER BY ad_soyad")
        return self.fetchall()
    
    # Ders işlemleri
    def ders_ekle(self, ad, haftalik_saat):
        """
        Yeni ders ekler
        
        Args:
            ad (str): Ders adı
            haftalik_saat (int): Haftalık ders saati
            
        Returns:
            int: Eklenen dersin ID'si
        """
        try:
            self.execute(
                "INSERT INTO dersler (ad, haftalik_saat) VALUES (?, ?)",
                (ad, haftalik_saat)
            )
            self.commit()
            return self.lastrowid()
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu ders zaten mevcut: {ad}")
            raise ValueError(f"Bu ders zaten mevcut: {ad}")
    
    def ders_guncelle(self, id, ad, haftalik_saat):
        """
        Ders bilgilerini günceller
        
        Args:
            id (int): Ders ID'si
            ad (str): Ders adı
            haftalik_saat (int): Haftalık ders saati
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            self.execute(
                "UPDATE dersler SET ad=?, haftalik_saat=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
                (ad, haftalik_saat, id)
            )
            self.commit()
            return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu ders zaten mevcut: {ad}")
            raise ValueError(f"Bu ders zaten mevcut: {ad}")
    
    def ders_sil(self, id):
        """
        Dersi siler
        
        Args:
            id (int): Ders ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM dersler WHERE id=?", (id,))
        self.commit()
        return True
    
    def ders_getir(self, id):
        """
        Ders bilgilerini getirir
        
        Args:
            id (int): Ders ID'si
            
        Returns:
            dict: Ders bilgileri
        """
        self.execute("SELECT * FROM dersler WHERE id=?", (id,))
        return self.fetchone()
    
    def tum_dersleri_getir(self):
        """
        Tüm dersleri getirir
        
        Returns:
            list: Ders listesi
        """
        self.execute("SELECT * FROM dersler ORDER BY ad")
        return self.fetchall()
    
    # Derslik işlemleri
    def derslik_ekle(self, ad, tur="normal"):
        """
        Yeni derslik ekler
        
        Args:
            ad (str): Derslik adı
            tur (str, optional): Derslik türü. Defaults to "normal".
            
        Returns:
            int: Eklenen dersliğin ID'si
        """
        try:
            self.execute(
                "INSERT INTO derslikler (ad, tur) VALUES (?, ?)",
                (ad, tur)
            )
            self.commit()
            return self.lastrowid()
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu derslik zaten mevcut: {ad}")
            raise ValueError(f"Bu derslik zaten mevcut: {ad}")
    
    def derslik_guncelle(self, id, ad, tur):
        """
        Derslik bilgilerini günceller
        
        Args:
            id (int): Derslik ID'si
            ad (str): Derslik adı
            tur (str): Derslik türü
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            self.execute(
                "UPDATE derslikler SET ad=?, tur=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
                (ad, tur, id)
            )
            self.commit()
            return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu derslik zaten mevcut: {ad}")
            raise ValueError(f"Bu derslik zaten mevcut: {ad}")
    
    def derslik_sil(self, id):
        """
        Dersliği siler
        
        Args:
            id (int): Derslik ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM derslikler WHERE id=?", (id,))
        self.commit()
        return True
    
    def derslik_getir(self, id):
        """
        Derslik bilgilerini getirir
        
        Args:
            id (int): Derslik ID'si
            
        Returns:
            dict: Derslik bilgileri
        """
        self.execute("SELECT * FROM derslikler WHERE id=?", (id,))
        return self.fetchone()
    
    def tum_derslikleri_getir(self):
        """
        Tüm derslikleri getirir
        
        Returns:
            list: Derslik listesi
        """
        self.execute("SELECT * FROM derslikler ORDER BY ad")
        return self.fetchall()
    
    # Ders-Sınıf ilişki işlemleri
    def ders_sinif_iliskisi_ekle(self, ders_id, sinif_id, ogretmen_id, haftalik_saat):
        """
        Ders-Sınıf ilişkisi ekler
        
        Args:
            ders_id (int): Ders ID'si
            sinif_id (int): Sınıf ID'si
            ogretmen_id (int): Öğretmen ID'si
            haftalik_saat (int): Haftalık ders saati
            
        Returns:
            int: Eklenen ilişkinin ID'si
        """
        try:
            self.execute(
                "INSERT INTO ders_sinif (ders_id, sinif_id, ogretmen_id, haftalik_saat) VALUES (?, ?, ?, ?)",
                (ders_id, sinif_id, ogretmen_id, haftalik_saat)
            )
            self.commit()
            return self.lastrowid()
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu ders-sınıf ilişkisi zaten mevcut: Ders ID: {ders_id}, Sınıf ID: {sinif_id}, Öğretmen ID: {ogretmen_id}")
            raise ValueError(f"Bu ders-sınıf ilişkisi zaten mevcut")
    
    def ders_sinif_iliskisi_guncelle(self, id, ders_id, sinif_id, ogretmen_id, haftalik_saat):
        """
        Ders-Sınıf ilişkisini günceller
        
        Args:
            id (int): İlişki ID'si
            ders_id (int): Ders ID'si
            sinif_id (int): Sınıf ID'si
            ogretmen_id (int): Öğretmen ID'si
            haftalik_saat (int): Haftalık ders saati
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            self.execute(
                "UPDATE ders_sinif SET ders_id=?, sinif_id=?, ogretmen_id=?, haftalik_saat=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
                (ders_id, sinif_id, ogretmen_id, haftalik_saat, id)
            )
            self.commit()
            return True
        except sqlite3.IntegrityError:
            self.logger.warning(f"Bu ders-sınıf ilişkisi zaten mevcut: Ders ID: {ders_id}, Sınıf ID: {sinif_id}, Öğretmen ID: {ogretmen_id}")
            raise ValueError(f"Bu ders-sınıf ilişkisi zaten mevcut")
    
    def ders_sinif_iliskisi_sil(self, id):
        """
        Ders-Sınıf ilişkisini siler
        
        Args:
            id (int): İlişki ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM ders_sinif WHERE id=?", (id,))
        self.commit()
        return True
    
    def ders_sinif_iliskisi_getir(self, id):
        """
        Ders-Sınıf ilişkisini getirir
        
        Args:
            id (int): İlişki ID'si
            
        Returns:
            dict: İlişki bilgileri
        """
        self.execute("SELECT * FROM ders_sinif WHERE id=?", (id,))
        return self.fetchone()
    
    def sinifin_derslerini_getir(self, sinif_id):
        """
        Sınıfın derslerini getirir
        
        Args:
            sinif_id (int): Sınıf ID'si
            
        Returns:
            list: Ders listesi
        """
        self.execute("""
            SELECT ds.*, d.ad as ders_adi, o.ad_soyad as ogretmen_adi
            FROM ders_sinif ds
            JOIN dersler d ON ds.ders_id = d.id
            JOIN ogretmenler o ON ds.ogretmen_id = o.id
            WHERE ds.sinif_id = ?
            ORDER BY d.ad
        """, (sinif_id,))
        return self.fetchall()
    
    def ogretmenin_derslerini_getir(self, ogretmen_id):
        """
        Öğretmenin derslerini getirir
        
        Args:
            ogretmen_id (int): Öğretmen ID'si
            
        Returns:
            list: Ders listesi
        """
        self.execute("""
            SELECT ds.*, d.ad as ders_adi, s.ad as sinif_adi, s.sube as sinif_sube
            FROM ders_sinif ds
            JOIN dersler d ON ds.ders_id = d.id
            JOIN siniflar s ON ds.sinif_id = s.id
            WHERE ds.ogretmen_id = ?
            ORDER BY s.ad, s.sube, d.ad
        """, (ogretmen_id,))
        return self.fetchall()
    
    def tum_ders_sinif_iliskilerini_getir(self):
        """
        Tüm ders-sınıf ilişkilerini getirir
        
        Returns:
            list: İlişki listesi
        """
        self.execute("""
            SELECT ds.*, d.ad as ders_adi, s.ad as sinif_adi, s.sube as sinif_sube, o.ad_soyad as ogretmen_adi
            FROM ders_sinif ds
            JOIN dersler d ON ds.ders_id = d.id
            JOIN siniflar s ON ds.sinif_id = s.id
            JOIN ogretmenler o ON ds.ogretmen_id = o.id
            ORDER BY s.ad, s.sube, d.ad
        """)
        return self.fetchall()
    
    # Uygun olmayan zaman işlemleri
    def uygun_olmayan_zaman_ekle(self, ogretmen_id, gun, saat_baslangic, saat_bitis):
        """
        Öğretmen için uygun olmayan zaman ekler
        
        Args:
            ogretmen_id (int): Öğretmen ID'si
            gun (int): Gün (0: Pazartesi, 1: Salı, ...)
            saat_baslangic (int): Başlangıç saati
            saat_bitis (int): Bitiş saati
            
        Returns:
            int: Eklenen kaydın ID'si
        """
        self.execute(
            "INSERT INTO uygun_olmayan_zamanlar (ogretmen_id, gun, saat_baslangic, saat_bitis) VALUES (?, ?, ?, ?)",
            (ogretmen_id, gun, saat_baslangic, saat_bitis)
        )
        self.commit()
        return self.lastrowid()
    
    def uygun_olmayan_zaman_guncelle(self, id, ogretmen_id, gun, saat_baslangic, saat_bitis):
        """
        Uygun olmayan zamanı günceller
        
        Args:
            id (int): Kayıt ID'si
            ogretmen_id (int): Öğretmen ID'si
            gun (int): Gün (0: Pazartesi, 1: Salı, ...)
            saat_baslangic (int): Başlangıç saati
            saat_bitis (int): Bitiş saati
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute(
            "UPDATE uygun_olmayan_zamanlar SET ogretmen_id=?, gun=?, saat_baslangic=?, saat_bitis=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
            (ogretmen_id, gun, saat_baslangic, saat_bitis, id)
        )
        self.commit()
        return True
    
    def uygun_olmayan_zaman_sil(self, id):
        """
        Uygun olmayan zamanı siler
        
        Args:
            id (int): Kayıt ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM uygun_olmayan_zamanlar WHERE id=?", (id,))
        self.commit()
        return True
    
    def ogretmenin_uygun_olmayan_zamanlarini_getir(self, ogretmen_id):
        """
        Öğretmenin uygun olmayan zamanlarını getirir
        
        Args:
            ogretmen_id (int): Öğretmen ID'si
            
        Returns:
            list: Uygun olmayan zaman listesi
        """
        self.execute("SELECT * FROM uygun_olmayan_zamanlar WHERE ogretmen_id=? ORDER BY gun, saat_baslangic", (ogretmen_id,))
        return self.fetchall()
    
    def tum_uygun_olmayan_zamanlari_getir(self):
        """
        Tüm uygun olmayan zamanları getirir
        
        Returns:
            list: Uygun olmayan zaman listesi
        """
        self.execute("""
            SELECT uz.*, o.ad_soyad as ogretmen_adi
            FROM uygun_olmayan_zamanlar uz
            JOIN ogretmenler o ON uz.ogretmen_id = o.id
            ORDER BY o.ad_soyad, uz.gun, uz.saat_baslangic
        """)
        return self.fetchall()
    
    # Program işlemleri
    def program_ekle(self, sinif_id, ogretmen_id, ders_id, derslik_id, gun, saat):
        """
        Program kaydı ekler
        
        Args:
            sinif_id (int): Sınıf ID'si
            ogretmen_id (int): Öğretmen ID'si
            ders_id (int): Ders ID'si
            derslik_id (int): Derslik ID'si
            gun (int): Gün (0: Pazartesi, 1: Salı, ...)
            saat (int): Saat
            
        Returns:
            int: Eklenen kaydın ID'si
        """
        self.execute(
            "INSERT INTO program (sinif_id, ogretmen_id, ders_id, derslik_id, gun, saat) VALUES (?, ?, ?, ?, ?, ?)",
            (sinif_id, ogretmen_id, ders_id, derslik_id, gun, saat)
        )
        self.commit()
        return self.lastrowid()
    
    def program_guncelle(self, id, sinif_id, ogretmen_id, ders_id, derslik_id, gun, saat):
        """
        Program kaydını günceller
        
        Args:
            id (int): Kayıt ID'si
            sinif_id (int): Sınıf ID'si
            ogretmen_id (int): Öğretmen ID'si
            ders_id (int): Ders ID'si
            derslik_id (int): Derslik ID'si
            gun (int): Gün (0: Pazartesi, 1: Salı, ...)
            saat (int): Saat
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute(
            "UPDATE program SET sinif_id=?, ogretmen_id=?, ders_id=?, derslik_id=?, gun=?, saat=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE id=?",
            (sinif_id, ogretmen_id, ders_id, derslik_id, gun, saat, id)
        )
        self.commit()
        return True
    
    def program_sil(self, id):
        """
        Program kaydını siler
        
        Args:
            id (int): Kayıt ID'si
            
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM program WHERE id=?", (id,))
        self.commit()
        return True
    
    def tum_programi_temizle(self):
        """
        Tüm program kayıtlarını siler
        
        Returns:
            bool: Başarılı ise True
        """
        self.execute("DELETE FROM program")
        self.commit()
        return True
    
    def sinifin_programini_getir(self, sinif_id):
        """
        Sınıfın programını getirir
        
        Args:
            sinif_id (int): Sınıf ID'si
            
        Returns:
            list: Program listesi
        """
        self.execute("""
            SELECT p.*, d.ad as ders_adi, o.ad_soyad as ogretmen_adi, dr.ad as derslik_adi
            FROM program p
            JOIN dersler d ON p.ders_id = d.id
            JOIN ogretmenler o ON p.ogretmen_id = o.id
            LEFT JOIN derslikler dr ON p.derslik_id = dr.id
            WHERE p.sinif_id = ?
            ORDER BY p.gun, p.saat
        """, (sinif_id,))
        return self.fetchall()
    
    def ogretmenin_programini_getir(self, ogretmen_id):
        """
        Öğretmenin programını getirir
        
        Args:
            ogretmen_id (int): Öğretmen ID'si
            
        Returns:
            list: Program listesi
        """
        self.execute("""
            SELECT p.*, d.ad as ders_adi, s.ad as sinif_adi, s.sube as sinif_sube, dr.ad as derslik_adi
            FROM program p
            JOIN dersler d ON p.ders_id = d.id
            JOIN siniflar s ON p.sinif_id = s.id
            LEFT JOIN derslikler dr ON p.derslik_id = dr.id
            WHERE p.ogretmen_id = ?
            ORDER BY p.gun, p.saat
        """, (ogretmen_id,))
        return self.fetchall()
    
    def dersligin_programini_getir(self, derslik_id):
        """
        Dersliğin programını getirir
        
        Args:
            derslik_id (int): Derslik ID'si
            
        Returns:
            list: Program listesi
        """
        self.execute("""
            SELECT p.*, d.ad as ders_adi, s.ad as sinif_adi, s.sube as sinif_sube, o.ad_soyad as ogretmen_adi
            FROM program p
            JOIN dersler d ON p.ders_id = d.id
            JOIN siniflar s ON p.sinif_id = s.id
            JOIN ogretmenler o ON p.ogretmen_id = o.id
            WHERE p.derslik_id = ?
            ORDER BY p.gun, p.saat
        """, (derslik_id,))
        return self.fetchall()
    
    def tum_programi_getir(self):
        """
        Tüm programı getirir
        
        Returns:
            list: Program listesi
        """
        self.execute("""
            SELECT p.*, d.ad as ders_adi, s.ad as sinif_adi, s.sube as sinif_sube, o.ad_soyad as ogretmen_adi, dr.ad as derslik_adi
            FROM program p
            JOIN dersler d ON p.ders_id = d.id
            JOIN siniflar s ON p.sinif_id = s.id
            JOIN ogretmenler o ON p.ogretmen_id = o.id
            LEFT JOIN derslikler dr ON p.derslik_id = dr.id
            ORDER BY s.ad, s.sube, p.gun, p.saat
        """)
        return self.fetchall()
    
    # Ayar işlemleri
    def ayar_ekle_veya_guncelle(self, anahtar, deger, aciklama=None):
        """
        Ayar ekler veya günceller
        
        Args:
            anahtar (str): Ayar anahtarı
            deger (str): Ayar değeri
            aciklama (str, optional): Açıklama. Defaults to None.
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            # Önce ayarın var olup olmadığını kontrol et
            self.execute("SELECT id FROM ayarlar WHERE anahtar=?", (anahtar,))
            ayar = self.fetchone()
            
            if ayar:
                # Ayar varsa güncelle
                if aciklama:
                    self.execute(
                        "UPDATE ayarlar SET deger=?, aciklama=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE anahtar=?",
                        (deger, aciklama, anahtar)
                    )
                else:
                    self.execute(
                        "UPDATE ayarlar SET deger=?, guncelleme_tarihi=CURRENT_TIMESTAMP WHERE anahtar=?",
                        (deger, anahtar)
                    )
            else:
                # Ayar yoksa ekle
                if aciklama:
                    self.execute(
                        "INSERT INTO ayarlar (anahtar, deger, aciklama) VALUES (?, ?, ?)",
                        (anahtar, deger, aciklama)
                    )
                else:
                    self.execute(
                        "INSERT INTO ayarlar (anahtar, deger) VALUES (?, ?)",
                        (anahtar, deger)
                    )
            
            self.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ayar ekleme/güncelleme hatası: {str(e)}")
            raise
    
    def ayar_getir(self, anahtar, varsayilan=None):
        """
        Ayar değerini getirir
        
        Args:
            anahtar (str): Ayar anahtarı
            varsayilan (any, optional): Ayar bulunamazsa döndürülecek değer. Defaults to None.
            
        Returns:
            str: Ayar değeri
        """
        self.execute("SELECT deger FROM ayarlar WHERE anahtar=?", (anahtar,))
        ayar = self.fetchone()
        
        if ayar:
            return ayar['deger']
        else:
            return varsayilan
    
    def tum_ayarlari_getir(self):
        """
        Tüm ayarları getirir
        
        Returns:
            list: Ayar listesi
        """
        self.execute("SELECT * FROM ayarlar ORDER BY anahtar")
        return self.fetchall()
