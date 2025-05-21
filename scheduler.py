#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program oluşturma algoritması modülü
Google OR-Tools kütüphanesini kullanarak kısıt programlama ile ders programı oluşturur
"""

import time
import logging
from datetime import datetime
from ortools.sat.python import cp_model

class ProgramOlusturucu:
    """
    Program oluşturma algoritması sınıfı
    """
    
    def __init__(self, db, config):
        """
        Program oluşturucu sınıfını başlatır
        
        Args:
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Ayarları yükle
        self.load_settings()
        
        # Veri yapıları
        self.siniflar = []
        self.ogretmenler = []
        self.dersler = []
        self.derslikler = []
        self.ders_sinif_iliskileri = []
        self.uygun_olmayan_zamanlar = []
        
        # Model değişkenleri
        self.model = None
        self.ders_degiskenleri = {}
        self.solver = None
        self.cozum = None
        
        self.logger.info("Program oluşturucu başlatıldı")
    
    def load_settings(self):
        """
        Ayarları veritabanından yükler
        """
        try:
            # Zaman ayarları
            self.ders_suresi = int(self.db.ayar_getir("ders_suresi", "40"))
            self.teneffus_suresi = int(self.db.ayar_getir("teneffus_suresi", "10"))
            self.max_gunluk_ders = int(self.db.ayar_getir("max_gunluk_ders", "8"))
            self.max_haftalik_ders = int(self.db.ayar_getir("max_haftalik_ders", "40"))
            
            # Öğretmen kısıtları
            self.ogretmen_gunluk_max = int(self.db.ayar_getir("ogretmen_gunluk_max_ders", "6"))
            self.ogretmen_gunluk_min = int(self.db.ayar_getir("ogretmen_gunluk_min_ders", "2"))
            self.ogretmen_bos_saat_tercihi = self.db.ayar_getir("ogretmen_bos_saat_tercihi", "minimize")
            
            # Sınıf kısıtları
            self.sinif_gunluk_max = int(self.db.ayar_getir("sinif_gunluk_max_ders", "8"))
            self.sinif_gunluk_min = int(self.db.ayar_getir("sinif_gunluk_min_ders", "4"))
            self.ayni_ders_tekrar = int(self.db.ayar_getir("ayni_ders_tekrar", "2"))
            
            # Derslik kısıtları
            self.ozel_derslik_zorunlu = self.db.ayar_getir("ozel_derslik_zorunlu", "1") == "1"
            self.derslik_degisim_minimize = self.db.ayar_getir("derslik_degisim_minimize", "1") == "1"
            
            # Genel kısıtlar
            self.blok_ders_arka_arkaya = self.db.ayar_getir("blok_ders_arka_arkaya", "1") == "1"
            self.max_blok_ders = int(self.db.ayar_getir("max_blok_ders", "2"))
            self.algoritma_sure_siniri = int(self.db.ayar_getir("algoritma_sure_siniri", "300"))
            
            # Gün ve saat bilgileri
            self.gun_sayisi = 5  # Pazartesi-Cuma
            self.saat_sayisi = self.max_gunluk_ders  # Günlük maksimum ders saati
            
            self.logger.info("Ayarlar başarıyla yüklendi")
        except Exception as e:
            self.logger.error(f"Ayarlar yüklenirken hata oluştu: {str(e)}")
            raise
    
    def load_data(self):
        """
        Veritabanından verileri yükler
        """
        try:
            # Sınıfları yükle
            self.siniflar = self.db.tum_siniflari_getir()
            self.logger.info(f"{len(self.siniflar)} sınıf yüklendi")
            
            # Öğretmenleri yükle
            self.ogretmenler = self.db.tum_ogretmenleri_getir()
            self.logger.info(f"{len(self.ogretmenler)} öğretmen yüklendi")
            
            # Dersleri yükle
            self.dersler = self.db.tum_dersleri_getir()
            self.logger.info(f"{len(self.dersler)} ders yüklendi")
            
            # Derslikleri yükle
            self.derslikler = self.db.tum_derslikleri_getir()
            self.logger.info(f"{len(self.derslikler)} derslik yüklendi")
            
            # Ders-sınıf ilişkilerini yükle
            self.ders_sinif_iliskileri = self.db.tum_ders_sinif_iliskilerini_getir()
            self.logger.info(f"{len(self.ders_sinif_iliskileri)} ders-sınıf ilişkisi yüklendi")
            
            # Uygun olmayan zamanları yükle
            self.uygun_olmayan_zamanlar = self.db.tum_uygun_olmayan_zamanlari_getir()
            self.logger.info(f"{len(self.uygun_olmayan_zamanlar)} uygun olmayan zaman yüklendi")
            
            # Veri doğrulama
            if not self.siniflar:
                raise ValueError("Hiç sınıf tanımlanmamış")
            
            if not self.ogretmenler:
                raise ValueError("Hiç öğretmen tanımlanmamış")
            
            if not self.dersler:
                raise ValueError("Hiç ders tanımlanmamış")
            
            if not self.ders_sinif_iliskileri:
                raise ValueError("Hiç ders-sınıf ilişkisi tanımlanmamış")
            
            return True
        except Exception as e:
            self.logger.error(f"Veriler yüklenirken hata oluştu: {str(e)}")
            raise
    
    def create_model(self):
        """
        CP-SAT modeli oluşturur
        """
        try:
            # Yeni model oluştur
            self.model = cp_model.CpModel()
            
            # Değişkenleri oluştur
            self.create_variables()
            
            # Kısıtları ekle
            self.add_constraints()
            
            # Amaç fonksiyonunu ekle
            self.add_objective()
            
            self.logger.info("Model başarıyla oluşturuldu")
            return True
        except Exception as e:
            self.logger.error(f"Model oluşturulurken hata oluştu: {str(e)}")
            raise
    
    def create_variables(self):
        """
        Model değişkenlerini oluşturur
        """
        try:
            # Her ders-sınıf ilişkisi için değişkenler oluştur
            for iliski in self.ders_sinif_iliskileri:
                iliski_id = iliski["id"]
                sinif_id = iliski["sinif_id"]
                ogretmen_id = iliski["ogretmen_id"]
                ders_id = iliski["ders_id"]
                haftalik_saat = iliski["haftalik_saat"]
                
                # Her ders saati için ayrı değişken oluştur
                for ders_saati in range(haftalik_saat):
                    for gun in range(self.gun_sayisi):
                        for saat in range(self.saat_sayisi):
                            # Derslik değişkenleri
                            for derslik in self.derslikler:
                                derslik_id = derslik["id"]
                                
                                # Değişken adı: iliski_id_ders_saati_gun_saat_derslik_id
                                var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                
                                # Boolean değişken: 1 = bu ders bu gün, saat ve derslikte yapılıyor, 0 = yapılmıyor
                                self.ders_degiskenleri[var_name] = self.model.NewBoolVar(var_name)
            
            self.logger.info(f"{len(self.ders_degiskenleri)} değişken oluşturuldu")
        except Exception as e:
            self.logger.error(f"Değişkenler oluşturulurken hata oluştu: {str(e)}")
            raise
    
    def add_constraints(self):
        """
        Modele kısıtları ekler
        """
        try:
            # Her ders-sınıf ilişkisi için haftalık ders saati kadar ders olmalı
            self.add_weekly_hours_constraints()
            
            # Bir öğretmen aynı anda birden fazla derse giremez
            self.add_teacher_conflicts_constraints()
            
            # Bir sınıf aynı anda birden fazla ders alamaz
            self.add_class_conflicts_constraints()
            
            # Bir derslik aynı anda birden fazla ders için kullanılamaz
            self.add_classroom_conflicts_constraints()
            
            # Öğretmenin uygun olmadığı saatlerde ders atanamaz
            self.add_teacher_unavailability_constraints()
            
            # Öğretmenin günlük maksimum ve minimum ders saati kısıtları
            self.add_teacher_daily_hours_constraints()
            
            # Sınıfın günlük maksimum ve minimum ders saati kısıtları
            self.add_class_daily_hours_constraints()
            
            # Aynı dersin aynı günde maksimum tekrarı
            self.add_same_course_daily_constraints()
            
            # Özel derslik zorunluluğu
            if self.ozel_derslik_zorunlu:
                self.add_special_classroom_constraints()
            
            # Blok dersler arka arkaya olmalı
            if self.blok_ders_arka_arkaya:
                self.add_block_course_constraints()
            
            self.logger.info("Kısıtlar başarıyla eklendi")
        except Exception as e:
            self.logger.error(f"Kısıtlar eklenirken hata oluştu: {str(e)}")
            raise
    
    def add_weekly_hours_constraints(self):
        """
        Her ders-sınıf ilişkisi için haftalık ders saati kadar ders olmalı
        """
        for iliski in self.ders_sinif_iliskileri:
            iliski_id = iliski["id"]
            haftalik_saat = iliski["haftalik_saat"]
            
            # Her ders saati için değişkenleri topla
            for ders_saati in range(haftalik_saat):
                # Bu ders saati için tüm olası gün, saat ve derslik kombinasyonlarını topla
                ders_saati_degiskenleri = []
                
                for gun in range(self.gun_sayisi):
                    for saat in range(self.saat_sayisi):
                        for derslik in self.derslikler:
                            derslik_id = derslik["id"]
                            var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                            if var_name in self.ders_degiskenleri:
                                ders_saati_degiskenleri.append(self.ders_degiskenleri[var_name])
                
                # Her ders saati tam olarak bir kez yapılmalı
                self.model.Add(sum(ders_saati_degiskenleri) == 1)
    
    def add_teacher_conflicts_constraints(self):
        """
        Bir öğretmen aynı anda birden fazla derse giremez
        """
        # Her öğretmen, gün ve saat için
        for ogretmen in self.ogretmenler:
            ogretmen_id = ogretmen["id"]
            
            for gun in range(self.gun_sayisi):
                for saat in range(self.saat_sayisi):
                    # Bu öğretmenin bu gün ve saatteki tüm olası derslerini bul
                    ogretmen_ders_degiskenleri = []
                    
                    for iliski in self.ders_sinif_iliskileri:
                        if iliski["ogretmen_id"] == ogretmen_id:
                            iliski_id = iliski["id"]
                            haftalik_saat = iliski["haftalik_saat"]
                            
                            for ders_saati in range(haftalik_saat):
                                for derslik in self.derslikler:
                                    derslik_id = derslik["id"]
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        ogretmen_ders_degiskenleri.append(self.ders_degiskenleri[var_name])
                    
                    # Öğretmen aynı anda en fazla bir derse girebilir
                    if ogretmen_ders_degiskenleri:
                        self.model.Add(sum(ogretmen_ders_degiskenleri) <= 1)
    
    def add_class_conflicts_constraints(self):
        """
        Bir sınıf aynı anda birden fazla ders alamaz
        """
        # Her sınıf, gün ve saat için
        for sinif in self.siniflar:
            sinif_id = sinif["id"]
            
            for gun in range(self.gun_sayisi):
                for saat in range(self.saat_sayisi):
                    # Bu sınıfın bu gün ve saatteki tüm olası derslerini bul
                    sinif_ders_degiskenleri = []
                    
                    for iliski in self.ders_sinif_iliskileri:
                        if iliski["sinif_id"] == sinif_id:
                            iliski_id = iliski["id"]
                            haftalik_saat = iliski["haftalik_saat"]
                            
                            for ders_saati in range(haftalik_saat):
                                for derslik in self.derslikler:
                                    derslik_id = derslik["id"]
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        sinif_ders_degiskenleri.append(self.ders_degiskenleri[var_name])
                    
                    # Sınıf aynı anda en fazla bir ders alabilir
                    if sinif_ders_degiskenleri:
                        self.model.Add(sum(sinif_ders_degiskenleri) <= 1)
    
    def add_classroom_conflicts_constraints(self):
        """
        Bir derslik aynı anda birden fazla ders için kullanılamaz
        """
        # Her derslik, gün ve saat için
        for derslik in self.derslikler:
            derslik_id = derslik["id"]
            
            for gun in range(self.gun_sayisi):
                for saat in range(self.saat_sayisi):
                    # Bu dersliğin bu gün ve saatteki tüm olası derslerini bul
                    derslik_ders_degiskenleri = []
                    
                    for iliski in self.ders_sinif_iliskileri:
                        iliski_id = iliski["id"]
                        haftalik_saat = iliski["haftalik_saat"]
                        
                        for ders_saati in range(haftalik_saat):
                            var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                            if var_name in self.ders_degiskenleri:
                                derslik_ders_degiskenleri.append(self.ders_degiskenleri[var_name])
                    
                    # Derslik aynı anda en fazla bir ders için kullanılabilir
                    if derslik_ders_degiskenleri:
                        self.model.Add(sum(derslik_ders_degiskenleri) <= 1)
    
    def add_teacher_unavailability_constraints(self):
        """
        Öğretmenin uygun olmadığı saatlerde ders atanamaz
        """
        # Her uygun olmayan zaman için
        for zaman in self.uygun_olmayan_zamanlar:
            ogretmen_id = zaman["ogretmen_id"]
            gun = zaman["gun"]
            saat_baslangic = zaman["saat_baslangic"]
            saat_bitis = zaman["saat_bitis"]
            
            # Bu öğretmenin bu zaman aralığındaki tüm olası derslerini bul
            for saat in range(saat_baslangic, saat_bitis):
                if saat >= self.saat_sayisi:
                    continue
                
                ogretmen_ders_degiskenleri = []
                
                for iliski in self.ders_sinif_iliskileri:
                    if iliski["ogretmen_id"] == ogretmen_id:
                        iliski_id = iliski["id"]
                        haftalik_saat = iliski["haftalik_saat"]
                        
                        for ders_saati in range(haftalik_saat):
                            for derslik in self.derslikler:
                                derslik_id = derslik["id"]
                                var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                if var_name in self.ders_degiskenleri:
                                    ogretmen_ders_degiskenleri.append(self.ders_degiskenleri[var_name])
                
                # Bu zaman aralığında ders atanamaz
                if ogretmen_ders_degiskenleri:
                    self.model.Add(sum(ogretmen_ders_degiskenleri) == 0)
    
    def add_teacher_daily_hours_constraints(self):
        """
        Öğretmenin günlük maksimum ve minimum ders saati kısıtları
        """
        # Her öğretmen ve gün için
        for ogretmen in self.ogretmenler:
            ogretmen_id = ogretmen["id"]
            
            for gun in range(self.gun_sayisi):
                # Bu öğretmenin bu gündeki tüm olası derslerini bul
                ogretmen_gun_ders_degiskenleri = []
                
                for iliski in self.ders_sinif_iliskileri:
                    if iliski["ogretmen_id"] == ogretmen_id:
                        iliski_id = iliski["id"]
                        haftalik_saat = iliski["haftalik_saat"]
                        
                        for ders_saati in range(haftalik_saat):
                            for saat in range(self.saat_sayisi):
                                for derslik in self.derslikler:
                                    derslik_id = derslik["id"]
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        ogretmen_gun_ders_degiskenleri.append(self.ders_degiskenleri[var_name])
                
                # Öğretmenin günlük ders saati kısıtları
                if ogretmen_gun_ders_degiskenleri:
                    # Maksimum kısıt
                    self.model.Add(sum(ogretmen_gun_ders_degiskenleri) <= self.ogretmen_gunluk_max)
                    
                    # Minimum kısıt - eğer o gün hiç dersi yoksa minimum kısıt uygulanmaz
                    # Bunun için bir boolean değişken kullanılır
                    has_lessons = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_has_lessons")
                    
                    # Eğer toplam ders sayısı > 0 ise has_lessons = 1, değilse has_lessons = 0
                    self.model.Add(sum(ogretmen_gun_ders_degiskenleri) == 0).OnlyEnforceIf(has_lessons.Not())
                    self.model.Add(sum(ogretmen_gun_ders_degiskenleri) > 0).OnlyEnforceIf(has_lessons)
                    
                    # Eğer has_lessons = 1 ise, minimum kısıt uygulanır
                    self.model.Add(sum(ogretmen_gun_ders_degiskenleri) >= self.ogretmen_gunluk_min).OnlyEnforceIf(has_lessons)
    
    def add_class_daily_hours_constraints(self):
        """
        Sınıfın günlük maksimum ve minimum ders saati kısıtları
        """
        # Her sınıf ve gün için
        for sinif in self.siniflar:
            sinif_id = sinif["id"]
            
            for gun in range(self.gun_sayisi):
                # Bu sınıfın bu gündeki tüm olası derslerini bul
                sinif_gun_ders_degiskenleri = []
                
                for iliski in self.ders_sinif_iliskileri:
                    if iliski["sinif_id"] == sinif_id:
                        iliski_id = iliski["id"]
                        haftalik_saat = iliski["haftalik_saat"]
                        
                        for ders_saati in range(haftalik_saat):
                            for saat in range(self.saat_sayisi):
                                for derslik in self.derslikler:
                                    derslik_id = derslik["id"]
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        sinif_gun_ders_degiskenleri.append(self.ders_degiskenleri[var_name])
                
                # Sınıfın günlük ders saati kısıtları
                if sinif_gun_ders_degiskenleri:
                    # Maksimum kısıt
                    self.model.Add(sum(sinif_gun_ders_degiskenleri) <= self.sinif_gunluk_max)
                    
                    # Minimum kısıt
                    self.model.Add(sum(sinif_gun_ders_degiskenleri) >= self.sinif_gunluk_min)
    
    def add_same_course_daily_constraints(self):
        """
        Aynı dersin aynı günde maksimum tekrarı
        """
        # Her sınıf, ders ve gün için
        for sinif in self.siniflar:
            sinif_id = sinif["id"]
            
            # Bu sınıfın aldığı dersleri bul
            sinif_dersleri = {}
            for iliski in self.ders_sinif_iliskileri:
                if iliski["sinif_id"] == sinif_id:
                    ders_id = iliski["ders_id"]
                    if ders_id not in sinif_dersleri:
                        sinif_dersleri[ders_id] = []
                    sinif_dersleri[ders_id].append(iliski)
            
            # Her ders için
            for ders_id, iliskiler in sinif_dersleri.items():
                for gun in range(self.gun_sayisi):
                    # Bu dersin bu gündeki tüm olası saatlerini bul
                    ders_gun_degiskenleri = []
                    
                    for iliski in iliskiler:
                        iliski_id = iliski["id"]
                        haftalik_saat = iliski["haftalik_saat"]
                        
                        for ders_saati in range(haftalik_saat):
                            for saat in range(self.saat_sayisi):
                                for derslik in self.derslikler:
                                    derslik_id = derslik["id"]
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        ders_gun_degiskenleri.append(self.ders_degiskenleri[var_name])
                    
                    # Aynı dersin aynı günde maksimum tekrarı
                    if ders_gun_degiskenleri:
                        self.model.Add(sum(ders_gun_degiskenleri) <= self.ayni_ders_tekrar)
    
    def add_special_classroom_constraints(self):
        """
        Özel derslik zorunluluğu
        """
        # Özel derslikler
        ozel_derslikler = [derslik for derslik in self.derslikler if derslik["tur"] == "ozel"]
        ozel_derslik_ids = [derslik["id"] for derslik in ozel_derslikler]
        
        # Normal derslikler
        normal_derslikler = [derslik for derslik in self.derslikler if derslik["tur"] == "normal"]
        normal_derslik_ids = [derslik["id"] for derslik in normal_derslikler]
        
        # Her ders-sınıf ilişkisi için
        for iliski in self.ders_sinif_iliskileri:
            iliski_id = iliski["id"]
            ders_id = iliski["ders_id"]
            haftalik_saat = iliski["haftalik_saat"]
            
            # Dersin özel derslik gerektirip gerektirmediğini belirle
            # Burada basit bir örnek olarak, ders adında "lab" geçen dersler özel derslik gerektirir varsayalım
            ders = next((d for d in self.dersler if d["id"] == ders_id), None)
            if ders and ("lab" in ders["ad"].lower() or "laboratuvar" in ders["ad"].lower()):
                # Bu ders özel derslik gerektirir
                for ders_saati in range(haftalik_saat):
                    for gun in range(self.gun_sayisi):
                        for saat in range(self.saat_sayisi):
                            # Normal dersliklerdeki değişkenleri bul
                            normal_derslik_degiskenleri = []
                            for derslik_id in normal_derslik_ids:
                                var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                if var_name in self.ders_degiskenleri:
                                    normal_derslik_degiskenleri.append(self.ders_degiskenleri[var_name])
                            
                            # Normal dersliklerde bu ders yapılamaz
                            if normal_derslik_degiskenleri:
                                self.model.Add(sum(normal_derslik_degiskenleri) == 0)
    
    def add_block_course_constraints(self):
        """
        Blok dersler arka arkaya olmalı
        """
        # Her ders-sınıf ilişkisi için
        for iliski in self.ders_sinif_iliskileri:
            iliski_id = iliski["id"]
            haftalik_saat = iliski["haftalik_saat"]
            
            # Eğer haftalık ders saati 1'den fazla ise
            if haftalik_saat > 1:
                # Her gün için
                for gun in range(self.gun_sayisi):
                    # Her ders saati için (son ders saati hariç)
                    for ders_saati in range(haftalik_saat - 1):
                        # Bu ders saatinin yapıldığı saat ve derslik
                        for saat in range(self.saat_sayisi - 1):  # Son saatte blok ders başlayamaz
                            for derslik in self.derslikler:
                                derslik_id = derslik["id"]
                                var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                
                                if var_name in self.ders_degiskenleri:
                                    # Bir sonraki ders saatinin aynı gün, bir sonraki saat ve aynı derslikte olması gerekir
                                    next_var_name = f"{iliski_id}_{ders_saati+1}_{gun}_{saat+1}_{derslik_id}"
                                    
                                    if next_var_name in self.ders_degiskenleri:
                                        # Eğer bu ders saati bu gün, saat ve derslikte yapılıyorsa,
                                        # bir sonraki ders saati de bir sonraki saatte aynı derslikte yapılmalı
                                        self.model.Add(self.ders_degiskenleri[next_var_name] >= self.ders_degiskenleri[var_name])
    
    def add_objective(self):
        """
        Amaç fonksiyonunu ekler
        """
        try:
            # Amaç fonksiyonu bileşenleri
            objective_terms = []
            
            # 1. Öğretmen boş saat minimizasyonu/maksimizasyonu
            if self.ogretmen_bos_saat_tercihi == "minimize":
                objective_terms.extend(self.get_teacher_idle_hours_terms(minimize=True))
            else:
                objective_terms.extend(self.get_teacher_idle_hours_terms(minimize=False))
            
            # 2. Derslik değişim minimizasyonu
            if self.derslik_degisim_minimize:
                objective_terms.extend(self.get_classroom_change_terms())
            
            # Amaç fonksiyonunu ekle
            if objective_terms:
                self.model.Minimize(sum(objective_terms))
            
            self.logger.info("Amaç fonksiyonu başarıyla eklendi")
        except Exception as e:
            self.logger.error(f"Amaç fonksiyonu eklenirken hata oluştu: {str(e)}")
            raise
    
    def get_teacher_idle_hours_terms(self, minimize=True):
        """
        Öğretmen boş saat terimlerini döndürür
        
        Args:
            minimize (bool): True ise boş saatler minimize edilir, False ise maximize edilir
            
        Returns:
            list: Amaç fonksiyonu terimleri
        """
        terms = []
        
        # Her öğretmen ve gün için
        for ogretmen in self.ogretmenler:
            ogretmen_id = ogretmen["id"]
            
            for gun in range(self.gun_sayisi):
                # Bu öğretmenin bu gündeki her saat için ders değişkenleri
                ogretmen_saat_degiskenleri = {}
                
                for saat in range(self.saat_sayisi):
                    ogretmen_saat_degiskenleri[saat] = []
                    
                    for iliski in self.ders_sinif_iliskileri:
                        if iliski["ogretmen_id"] == ogretmen_id:
                            iliski_id = iliski["id"]
                            haftalik_saat = iliski["haftalik_saat"]
                            
                            for ders_saati in range(haftalik_saat):
                                for derslik in self.derslikler:
                                    derslik_id = derslik["id"]
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        ogretmen_saat_degiskenleri[saat].append(self.ders_degiskenleri[var_name])
                
                # Öğretmenin ilk ve son dersi arasındaki boş saatleri hesapla
                # İlk ders saati
                ilk_ders_var = self.model.NewIntVar(0, self.saat_sayisi, f"ogretmen_{ogretmen_id}_gun_{gun}_ilk_ders")
                ilk_ders_degiskenleri = []
                
                for saat in range(self.saat_sayisi):
                    # Bu saatte ders var mı?
                    has_lesson = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_saat_{saat}_has_lesson")
                    
                    if ogretmen_saat_degiskenleri[saat]:
                        self.model.Add(sum(ogretmen_saat_degiskenleri[saat]) > 0).OnlyEnforceIf(has_lesson)
                        self.model.Add(sum(ogretmen_saat_degiskenleri[saat]) == 0).OnlyEnforceIf(has_lesson.Not())
                    else:
                        self.model.Add(has_lesson == 0)
                    
                    # Bu saat ilk ders saati mi?
                    is_first = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_saat_{saat}_is_first")
                    ilk_ders_degiskenleri.append(is_first)
                    
                    # Eğer bu saatte ders var ve önceki saatlerde ders yoksa, bu saat ilk ders saatidir
                    if saat == 0:
                        self.model.AddImplication(has_lesson, is_first)
                        self.model.AddImplication(has_lesson.Not(), is_first.Not())
                    else:
                        # Önceki saatlerde ders var mı?
                        has_previous_lesson = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_saat_{saat}_has_previous_lesson")
                        previous_lessons = []
                        
                        for prev_saat in range(saat):
                            if ogretmen_saat_degiskenleri[prev_saat]:
                                previous_lessons.extend(ogretmen_saat_degiskenleri[prev_saat])
                        
                        if previous_lessons:
                            self.model.Add(sum(previous_lessons) > 0).OnlyEnforceIf(has_previous_lesson)
                            self.model.Add(sum(previous_lessons) == 0).OnlyEnforceIf(has_previous_lesson.Not())
                        else:
                            self.model.Add(has_previous_lesson == 0)
                        
                        # Bu saat ilk ders saati mi?
                        self.model.AddBoolAnd([has_lesson, has_previous_lesson.Not()]).OnlyEnforceIf(is_first)
                        self.model.AddBoolOr([has_lesson.Not(), has_previous_lesson]).OnlyEnforceIf(is_first.Not())
                    
                    # İlk ders saati değerini ayarla
                    self.model.Add(ilk_ders_var == saat).OnlyEnforceIf(is_first)
                
                # En fazla bir saat ilk ders saati olabilir
                self.model.Add(sum(ilk_ders_degiskenleri) <= 1)
                
                # Son ders saati
                son_ders_var = self.model.NewIntVar(0, self.saat_sayisi, f"ogretmen_{ogretmen_id}_gun_{gun}_son_ders")
                son_ders_degiskenleri = []
                
                for saat in range(self.saat_sayisi):
                    # Bu saatte ders var mı?
                    has_lesson = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_saat_{saat}_has_lesson_last")
                    
                    if ogretmen_saat_degiskenleri[saat]:
                        self.model.Add(sum(ogretmen_saat_degiskenleri[saat]) > 0).OnlyEnforceIf(has_lesson)
                        self.model.Add(sum(ogretmen_saat_degiskenleri[saat]) == 0).OnlyEnforceIf(has_lesson.Not())
                    else:
                        self.model.Add(has_lesson == 0)
                    
                    # Bu saat son ders saati mi?
                    is_last = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_saat_{saat}_is_last")
                    son_ders_degiskenleri.append(is_last)
                    
                    # Eğer bu saatte ders var ve sonraki saatlerde ders yoksa, bu saat son ders saatidir
                    if saat == self.saat_sayisi - 1:
                        self.model.AddImplication(has_lesson, is_last)
                        self.model.AddImplication(has_lesson.Not(), is_last.Not())
                    else:
                        # Sonraki saatlerde ders var mı?
                        has_next_lesson = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_saat_{saat}_has_next_lesson")
                        next_lessons = []
                        
                        for next_saat in range(saat + 1, self.saat_sayisi):
                            if ogretmen_saat_degiskenleri[next_saat]:
                                next_lessons.extend(ogretmen_saat_degiskenleri[next_saat])
                        
                        if next_lessons:
                            self.model.Add(sum(next_lessons) > 0).OnlyEnforceIf(has_next_lesson)
                            self.model.Add(sum(next_lessons) == 0).OnlyEnforceIf(has_next_lesson.Not())
                        else:
                            self.model.Add(has_next_lesson == 0)
                        
                        # Bu saat son ders saati mi?
                        self.model.AddBoolAnd([has_lesson, has_next_lesson.Not()]).OnlyEnforceIf(is_last)
                        self.model.AddBoolOr([has_lesson.Not(), has_next_lesson]).OnlyEnforceIf(is_last.Not())
                    
                    # Son ders saati değerini ayarla
                    self.model.Add(son_ders_var == saat).OnlyEnforceIf(is_last)
                
                # En fazla bir saat son ders saati olabilir
                self.model.Add(sum(son_ders_degiskenleri) <= 1)
                
                # Öğretmenin bu gün dersi var mı?
                has_lessons_today = self.model.NewBoolVar(f"ogretmen_{ogretmen_id}_gun_{gun}_has_lessons")
                all_lessons = []
                
                for saat in range(self.saat_sayisi):
                    if ogretmen_saat_degiskenleri[saat]:
                        all_lessons.extend(ogretmen_saat_degiskenleri[saat])
                
                if all_lessons:
                    self.model.Add(sum(all_lessons) > 0).OnlyEnforceIf(has_lessons_today)
                    self.model.Add(sum(all_lessons) == 0).OnlyEnforceIf(has_lessons_today.Not())
                else:
                    self.model.Add(has_lessons_today == 0)
                
                # Boş saat sayısı = son ders saati - ilk ders saati + 1 - ders sayısı
                ders_sayisi = self.model.NewIntVar(0, self.saat_sayisi, f"ogretmen_{ogretmen_id}_gun_{gun}_ders_sayisi")
                self.model.Add(ders_sayisi == sum(all_lessons))
                
                bos_saat_sayisi = self.model.NewIntVar(0, self.saat_sayisi, f"ogretmen_{ogretmen_id}_gun_{gun}_bos_saat_sayisi")
                
                # Eğer bu gün dersi varsa, boş saat sayısını hesapla
                self.model.Add(bos_saat_sayisi == son_ders_var - ilk_ders_var + 1 - ders_sayisi).OnlyEnforceIf(has_lessons_today)
                self.model.Add(bos_saat_sayisi == 0).OnlyEnforceIf(has_lessons_today.Not())
                
                # Amaç fonksiyonuna ekle
                if minimize:
                    terms.append(bos_saat_sayisi)
                else:
                    # Maksimize etmek için negatif ekle
                    terms.append(self.model.NewIntVar(-self.saat_sayisi, 0, f"ogretmen_{ogretmen_id}_gun_{gun}_neg_bos_saat"))
                    self.model.Add(terms[-1] == -bos_saat_sayisi)
        
        return terms
    
    def get_classroom_change_terms(self):
        """
        Derslik değişim terimlerini döndürür
        
        Returns:
            list: Amaç fonksiyonu terimleri
        """
        terms = []
        
        # Her sınıf ve gün için
        for sinif in self.siniflar:
            sinif_id = sinif["id"]
            
            for gun in range(self.gun_sayisi):
                # Bu sınıfın bu gündeki her saat için derslik değişkenleri
                sinif_saat_derslik = {}
                
                for saat in range(self.saat_sayisi):
                    sinif_saat_derslik[saat] = {}
                    
                    for derslik in self.derslikler:
                        derslik_id = derslik["id"]
                        sinif_saat_derslik[saat][derslik_id] = []
                        
                        for iliski in self.ders_sinif_iliskileri:
                            if iliski["sinif_id"] == sinif_id:
                                iliski_id = iliski["id"]
                                haftalik_saat = iliski["haftalik_saat"]
                                
                                for ders_saati in range(haftalik_saat):
                                    var_name = f"{iliski_id}_{ders_saati}_{gun}_{saat}_{derslik_id}"
                                    if var_name in self.ders_degiskenleri:
                                        sinif_saat_derslik[saat][derslik_id].append(self.ders_degiskenleri[var_name])
                
                # Her saat için derslik değişimi hesapla
                for saat in range(1, self.saat_sayisi):
                    # Önceki saatteki derslik
                    for prev_derslik in self.derslikler:
                        prev_derslik_id = prev_derslik["id"]
                        
                        # Bu saatteki derslik
                        for curr_derslik in self.derslikler:
                            curr_derslik_id = curr_derslik["id"]
                            
                            # Eğer derslik değişimi varsa
                            if prev_derslik_id != curr_derslik_id:
                                # Önceki saatte bu derslikte ders var mı?
                                prev_derslik_vars = sinif_saat_derslik[saat-1].get(prev_derslik_id, [])
                                
                                # Bu saatte bu derslikte ders var mı?
                                curr_derslik_vars = sinif_saat_derslik[saat].get(curr_derslik_id, [])
                                
                                if prev_derslik_vars and curr_derslik_vars:
                                    # Derslik değişimi var mı?
                                    has_change = self.model.NewBoolVar(f"sinif_{sinif_id}_gun_{gun}_saat_{saat}_derslik_degisimi_{prev_derslik_id}_{curr_derslik_id}")
                                    
                                    # Eğer önceki saatte bu derslikte ve bu saatte diğer derslikte ders varsa, değişim var
                                    self.model.Add(sum(prev_derslik_vars) > 0).OnlyEnforceIf(has_change)
                                    self.model.Add(sum(curr_derslik_vars) > 0).OnlyEnforceIf(has_change)
                                    
                                    # Amaç fonksiyonuna ekle
                                    terms.append(has_change)
        
        return terms
    
    def solve(self):
        """
        Modeli çözer
        
        Returns:
            bool: Çözüm bulundu mu?
        """
        try:
            # Çözücüyü oluştur
            self.solver = cp_model.CpSolver()
            
            # Zaman sınırı
            self.solver.parameters.max_time_in_seconds = self.algoritma_sure_siniri
            
            # Çözümü bul
            start_time = time.time()
            status = self.solver.Solve(self.model)
            end_time = time.time()
            
            # Çözüm durumunu kontrol et
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                self.cozum = self.solver
                self.logger.info(f"Çözüm bulundu! Süre: {end_time - start_time:.2f} saniye")
                return True
            else:
                self.logger.warning(f"Çözüm bulunamadı! Durum: {status}")
                return False
        except Exception as e:
            self.logger.error(f"Model çözülürken hata oluştu: {str(e)}")
            raise
    
    def save_solution(self):
        """
        Çözümü veritabanına kaydeder
        
        Returns:
            bool: Başarılı mı?
        """
        if not self.cozum:
            self.logger.error("Kaydedilecek çözüm bulunamadı")
            return False
        
        try:
            # Önce mevcut programı temizle
            self.db.tum_programi_temizle()
            
            # Çözümü kaydet
            for var_name, var in self.ders_degiskenleri.items():
                # Değişken değeri 1 ise (bu ders bu gün, saat ve derslikte yapılıyor)
                if self.cozum.Value(var) == 1:
                    # Değişken adını parçala: iliski_id_ders_saati_gun_saat_derslik_id
                    parts = var_name.split("_")
                    iliski_id = int(parts[0])
                    gun = int(parts[2])
                    saat = int(parts[3])
                    derslik_id = int(parts[4])
                    
                    # İlişki bilgilerini al
                    iliski = next((i for i in self.ders_sinif_iliskileri if i["id"] == iliski_id), None)
                    if iliski:
                        sinif_id = iliski["sinif_id"]
                        ogretmen_id = iliski["ogretmen_id"]
                        ders_id = iliski["ders_id"]
                        
                        # Programa ekle
                        self.db.program_ekle(sinif_id, ogretmen_id, ders_id, derslik_id, gun, saat)
            
            self.logger.info("Çözüm başarıyla kaydedildi")
            return True
        except Exception as e:
            self.logger.error(f"Çözüm kaydedilirken hata oluştu: {str(e)}")
            raise
    
    def create_schedule(self):
        """
        Ders programı oluşturur
        
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Verileri yükle
            self.load_data()
            
            # Modeli oluştur
            self.create_model()
            
            # Modeli çöz
            if self.solve():
                # Çözümü kaydet
                return self.save_solution()
            else:
                return False
        except Exception as e:
            self.logger.error(f"Program oluşturulurken hata oluştu: {str(e)}")
            raise
