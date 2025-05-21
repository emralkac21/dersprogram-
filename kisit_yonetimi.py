#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kısıt yönetimi arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class KisitYonetimi:
    """
    Kısıt yönetimi arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Kısıt yönetimi arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Ayarları yükle
        self.load_settings()
        
        self.logger.info("Kısıt yönetimi arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (sekmeli arayüz)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Zaman Ayarları sekmesi
        self.time_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.time_frame, text="Zaman Ayarları")
        self.create_time_settings_widgets()
        
        # Öğretmen Kısıtları sekmesi
        self.teacher_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.teacher_frame, text="Öğretmen Kısıtları")
        self.create_teacher_constraints_widgets()
        
        # Sınıf Kısıtları sekmesi
        self.class_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.class_frame, text="Sınıf Kısıtları")
        self.create_class_constraints_widgets()
        
        # Derslik Kısıtları sekmesi
        self.classroom_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.classroom_frame, text="Derslik Kısıtları")
        self.create_classroom_constraints_widgets()
        
        # Genel Kısıtlar sekmesi
        self.general_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.general_frame, text="Genel Kısıtlar")
        self.create_general_constraints_widgets()
    
    def create_time_settings_widgets(self):
        """
        Zaman ayarları sekmesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.time_frame, text="Zaman Ayarları", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Form çerçevesi
        form_frame = ttk.Frame(self.time_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Ders süresi
        ttk.Label(form_frame, text="Ders Süresi (dakika):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ders_suresi_var = tk.StringVar()
        self.ders_suresi_entry = ttk.Entry(form_frame, textvariable=self.ders_suresi_var, width=10)
        self.ders_suresi_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Teneffüs süresi
        ttk.Label(form_frame, text="Teneffüs Süresi (dakika):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.teneffus_suresi_var = tk.StringVar()
        self.teneffus_suresi_entry = ttk.Entry(form_frame, textvariable=self.teneffus_suresi_var, width=10)
        self.teneffus_suresi_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Günlük ders başlangıç saati
        ttk.Label(form_frame, text="Günlük Ders Başlangıç Saati:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.baslangic_saati_var = tk.StringVar()
        self.baslangic_saati_entry = ttk.Entry(form_frame, textvariable=self.baslangic_saati_var, width=10)
        self.baslangic_saati_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="(ÖR: 08:30)").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Günlük ders bitiş saati
        ttk.Label(form_frame, text="Günlük Ders Bitiş Saati:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.bitis_saati_var = tk.StringVar()
        self.bitis_saati_entry = ttk.Entry(form_frame, textvariable=self.bitis_saati_var, width=10)
        self.bitis_saati_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="(ÖR: 16:00)").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Öğle arası başlangıç saati
        ttk.Label(form_frame, text="Öğle Arası Başlangıç Saati:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.ogle_baslangic_var = tk.StringVar()
        self.ogle_baslangic_entry = ttk.Entry(form_frame, textvariable=self.ogle_baslangic_var, width=10)
        self.ogle_baslangic_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="(ÖR: 12:00)").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Öğle arası bitiş saati
        ttk.Label(form_frame, text="Öğle Arası Bitiş Saati:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.ogle_bitis_var = tk.StringVar()
        self.ogle_bitis_entry = ttk.Entry(form_frame, textvariable=self.ogle_bitis_var, width=10)
        self.ogle_bitis_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(form_frame, text="(ÖR: 13:00)").grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Maksimum günlük ders saati
        ttk.Label(form_frame, text="Maksimum Günlük Ders Saati:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_gunluk_ders_var = tk.StringVar()
        self.max_gunluk_ders_entry = ttk.Entry(form_frame, textvariable=self.max_gunluk_ders_var, width=10)
        self.max_gunluk_ders_entry.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Maksimum haftalık ders saati
        ttk.Label(form_frame, text="Maksimum Haftalık Ders Saati:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_haftalik_ders_var = tk.StringVar()
        self.max_haftalik_ders_entry = ttk.Entry(form_frame, textvariable=self.max_haftalik_ders_var, width=10)
        self.max_haftalik_ders_entry.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Kaydet butonu
        self.save_time_button = ttk.Button(form_frame, text="Ayarları Kaydet", command=self.save_time_settings)
        self.save_time_button.grid(row=8, column=0, columnspan=2, pady=20)
    
    def create_teacher_constraints_widgets(self):
        """
        Öğretmen kısıtları sekmesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.teacher_frame, text="Öğretmen Kısıtları", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Açıklama
        ttk.Label(self.teacher_frame, text="Öğretmenlerin uygun olmadığı zamanları belirlemek için Öğretmen Yönetimi bölümünü kullanın.").pack(pady=5)
        
        # Form çerçevesi
        form_frame = ttk.Frame(self.teacher_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Öğretmen günlük maksimum ders saati
        ttk.Label(form_frame, text="Öğretmen Günlük Maksimum Ders Saati:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ogretmen_gunluk_max_var = tk.StringVar()
        self.ogretmen_gunluk_max_entry = ttk.Entry(form_frame, textvariable=self.ogretmen_gunluk_max_var, width=10)
        self.ogretmen_gunluk_max_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Öğretmen günlük minimum ders saati
        ttk.Label(form_frame, text="Öğretmen Günlük Minimum Ders Saati:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.ogretmen_gunluk_min_var = tk.StringVar()
        self.ogretmen_gunluk_min_entry = ttk.Entry(form_frame, textvariable=self.ogretmen_gunluk_min_var, width=10)
        self.ogretmen_gunluk_min_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Öğretmen boş saat tercihi
        ttk.Label(form_frame, text="Öğretmen Boş Saat Tercihi:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.ogretmen_bos_saat_var = tk.StringVar(value="minimize")
        
        self.bos_saat_frame = ttk.Frame(form_frame)
        self.bos_saat_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.minimize_radio = ttk.Radiobutton(self.bos_saat_frame, text="Minimize Et", variable=self.ogretmen_bos_saat_var, value="minimize")
        self.minimize_radio.pack(side=tk.LEFT, padx=5)
        
        self.maximize_radio = ttk.Radiobutton(self.bos_saat_frame, text="Maximize Et", variable=self.ogretmen_bos_saat_var, value="maximize")
        self.maximize_radio.pack(side=tk.LEFT, padx=5)
        
        # Kaydet butonu
        self.save_teacher_button = ttk.Button(form_frame, text="Ayarları Kaydet", command=self.save_teacher_settings)
        self.save_teacher_button.grid(row=3, column=0, columnspan=2, pady=20)
    
    def create_class_constraints_widgets(self):
        """
        Sınıf kısıtları sekmesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.class_frame, text="Sınıf Kısıtları", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Form çerçevesi
        form_frame = ttk.Frame(self.class_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sınıf günlük maksimum ders saati
        ttk.Label(form_frame, text="Sınıf Günlük Maksimum Ders Saati:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sinif_gunluk_max_var = tk.StringVar()
        self.sinif_gunluk_max_entry = ttk.Entry(form_frame, textvariable=self.sinif_gunluk_max_var, width=10)
        self.sinif_gunluk_max_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Sınıf günlük minimum ders saati
        ttk.Label(form_frame, text="Sınıf Günlük Minimum Ders Saati:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sinif_gunluk_min_var = tk.StringVar()
        self.sinif_gunluk_min_entry = ttk.Entry(form_frame, textvariable=self.sinif_gunluk_min_var, width=10)
        self.sinif_gunluk_min_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Aynı dersin aynı günde maksimum tekrarı
        ttk.Label(form_frame, text="Aynı Dersin Aynı Günde Maksimum Tekrarı:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.ayni_ders_tekrar_var = tk.StringVar()
        self.ayni_ders_tekrar_entry = ttk.Entry(form_frame, textvariable=self.ayni_ders_tekrar_var, width=10)
        self.ayni_ders_tekrar_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Kaydet butonu
        self.save_class_button = ttk.Button(form_frame, text="Ayarları Kaydet", command=self.save_class_settings)
        self.save_class_button.grid(row=3, column=0, columnspan=2, pady=20)
    
    def create_classroom_constraints_widgets(self):
        """
        Derslik kısıtları sekmesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.classroom_frame, text="Derslik Kısıtları", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Form çerçevesi
        form_frame = ttk.Frame(self.classroom_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Özel derslik zorunluluğu
        ttk.Label(form_frame, text="Özel Derslik Zorunluluğu:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ozel_derslik_var = tk.BooleanVar(value=True)
        self.ozel_derslik_check = ttk.Checkbutton(form_frame, text="Özel derslikler için uygun derslik zorunlu", variable=self.ozel_derslik_var)
        self.ozel_derslik_check.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Derslik değişim minimizasyonu
        ttk.Label(form_frame, text="Derslik Değişim Minimizasyonu:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.derslik_degisim_var = tk.BooleanVar(value=True)
        self.derslik_degisim_check = ttk.Checkbutton(form_frame, text="Sınıfların derslik değişimini minimize et", variable=self.derslik_degisim_var)
        self.derslik_degisim_check.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Kaydet butonu
        self.save_classroom_button = ttk.Button(form_frame, text="Ayarları Kaydet", command=self.save_classroom_settings)
        self.save_classroom_button.grid(row=2, column=0, columnspan=2, pady=20)
    
    def create_general_constraints_widgets(self):
        """
        Genel kısıtlar sekmesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.general_frame, text="Genel Kısıtlar", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Form çerçevesi
        form_frame = ttk.Frame(self.general_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Blok ders tercihi
        ttk.Label(form_frame, text="Blok Ders Tercihi:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.blok_ders_var = tk.BooleanVar(value=True)
        self.blok_ders_check = ttk.Checkbutton(form_frame, text="Blok dersleri arka arkaya yerleştir", variable=self.blok_ders_var)
        self.blok_ders_check.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Maksimum blok ders sayısı
        ttk.Label(form_frame, text="Maksimum Blok Ders Sayısı:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_blok_ders_var = tk.StringVar()
        self.max_blok_ders_entry = ttk.Entry(form_frame, textvariable=self.max_blok_ders_var, width=10)
        self.max_blok_ders_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Algoritma çalışma süresi sınırı
        ttk.Label(form_frame, text="Algoritma Çalışma Süresi Sınırı (saniye):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.algoritma_sure_var = tk.StringVar()
        self.algoritma_sure_entry = ttk.Entry(form_frame, textvariable=self.algoritma_sure_var, width=10)
        self.algoritma_sure_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Kaydet butonu
        self.save_general_button = ttk.Button(form_frame, text="Ayarları Kaydet", command=self.save_general_settings)
        self.save_general_button.grid(row=3, column=0, columnspan=2, pady=20)
    
    def load_settings(self):
        """
        Ayarları veritabanından yükler
        """
        try:
            # Zaman ayarları
            self.ders_suresi_var.set(self.db.ayar_getir("ders_suresi", "40"))
            self.teneffus_suresi_var.set(self.db.ayar_getir("teneffus_suresi", "10"))
            self.baslangic_saati_var.set(self.db.ayar_getir("gunluk_ders_baslangic", "8:30"))
            self.bitis_saati_var.set(self.db.ayar_getir("gunluk_ders_bitis", "16:00"))
            self.ogle_baslangic_var.set(self.db.ayar_getir("ogle_arasi_baslangic", "12:00"))
            self.ogle_bitis_var.set(self.db.ayar_getir("ogle_arasi_bitis", "13:00"))
            self.max_gunluk_ders_var.set(self.db.ayar_getir("max_gunluk_ders", "8"))
            self.max_haftalik_ders_var.set(self.db.ayar_getir("max_haftalik_ders", "40"))
            
            # Öğretmen kısıtları
            self.ogretmen_gunluk_max_var.set(self.db.ayar_getir("ogretmen_gunluk_max_ders", "6"))
            self.ogretmen_gunluk_min_var.set(self.db.ayar_getir("ogretmen_gunluk_min_ders", "2"))
            self.ogretmen_bos_saat_var.set(self.db.ayar_getir("ogretmen_bos_saat_tercihi", "minimize"))
            
            # Sınıf kısıtları
            self.sinif_gunluk_max_var.set(self.db.ayar_getir("sinif_gunluk_max_ders", "8"))
            self.sinif_gunluk_min_var.set(self.db.ayar_getir("sinif_gunluk_min_ders", "4"))
            self.ayni_ders_tekrar_var.set(self.db.ayar_getir("ayni_ders_tekrar", "2"))
            
            # Derslik kısıtları
            self.ozel_derslik_var.set(self.db.ayar_getir("ozel_derslik_zorunlu", "1") == "1")
            self.derslik_degisim_var.set(self.db.ayar_getir("derslik_degisim_minimize", "1") == "1")
            
            # Genel kısıtlar
            self.blok_ders_var.set(self.db.ayar_getir("blok_ders_arka_arkaya", "1") == "1")
            self.max_blok_ders_var.set(self.db.ayar_getir("max_blok_ders", "2"))
            self.algoritma_sure_var.set(self.db.ayar_getir("algoritma_sure_siniri", "300"))
            
            self.logger.info("Ayarlar başarıyla yüklendi")
        except Exception as e:
            self.logger.error(f"Ayarlar yüklenirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar yüklenirken bir hata oluştu:\n{str(e)}")
    
    def save_time_settings(self):
        """
        Zaman ayarlarını kaydeder
        """
        try:
            # Veri doğrulama
            ders_suresi = int(self.ders_suresi_var.get())
            teneffus_suresi = int(self.teneffus_suresi_var.get())
            max_gunluk_ders = int(self.max_gunluk_ders_var.get())
            max_haftalik_ders = int(self.max_haftalik_ders_var.get())
            
            if ders_suresi <= 0:
                messagebox.showerror("Hata", "Ders süresi 0'dan büyük olmalıdır.")
                return
            
            if teneffus_suresi < 0:
                messagebox.showerror("Hata", "Teneffüs süresi negatif olamaz.")
                return
            
            if max_gunluk_ders <= 0:
                messagebox.showerror("Hata", "Maksimum günlük ders saati 0'dan büyük olmalıdır.")
                return
            
            if max_haftalik_ders <= 0:
                messagebox.showerror("Hata", "Maksimum haftalık ders saati 0'dan büyük olmalıdır.")
                return
            
            # Ayarları kaydet
            self.db.ayar_ekle_veya_guncelle("ders_suresi", self.ders_suresi_var.get(), "Ders süresi (dakika)")
            self.db.ayar_ekle_veya_guncelle("teneffus_suresi", self.teneffus_suresi_var.get(), "Teneffüs süresi (dakika)")
            self.db.ayar_ekle_veya_guncelle("gunluk_ders_baslangic", self.baslangic_saati_var.get(), "Günlük ders başlangıç saati")
            self.db.ayar_ekle_veya_guncelle("gunluk_ders_bitis", self.bitis_saati_var.get(), "Günlük ders bitiş saati")
            self.db.ayar_ekle_veya_guncelle("ogle_arasi_baslangic", self.ogle_baslangic_var.get(), "Öğle arası başlangıç saati")
            self.db.ayar_ekle_veya_guncelle("ogle_arasi_bitis", self.ogle_bitis_var.get(), "Öğle arası bitiş saati")
            self.db.ayar_ekle_veya_guncelle("max_gunluk_ders", self.max_gunluk_ders_var.get(), "Günlük maksimum ders saati")
            self.db.ayar_ekle_veya_guncelle("max_haftalik_ders", self.max_haftalik_ders_var.get(), "Haftalık maksimum ders saati")
            
            messagebox.showinfo("Bilgi", "Zaman ayarları başarıyla kaydedildi.")
            self.logger.info("Zaman ayarları kaydedildi")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen sayısal değerleri doğru formatta girin.")
        except Exception as e:
            self.logger.error(f"Zaman ayarları kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Zaman ayarları kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def save_teacher_settings(self):
        """
        Öğretmen kısıtlarını kaydeder
        """
        try:
            # Veri doğrulama
            ogretmen_gunluk_max = int(self.ogretmen_gunluk_max_var.get())
            ogretmen_gunluk_min = int(self.ogretmen_gunluk_min_var.get())
            
            if ogretmen_gunluk_max <= 0:
                messagebox.showerror("Hata", "Öğretmen günlük maksimum ders saati 0'dan büyük olmalıdır.")
                return
            
            if ogretmen_gunluk_min < 0:
                messagebox.showerror("Hata", "Öğretmen günlük minimum ders saati negatif olamaz.")
                return
            
            if ogretmen_gunluk_min > ogretmen_gunluk_max:
                messagebox.showerror("Hata", "Öğretmen günlük minimum ders saati, maksimum değerden büyük olamaz.")
                return
            
            # Ayarları kaydet
            self.db.ayar_ekle_veya_guncelle("ogretmen_gunluk_max_ders", self.ogretmen_gunluk_max_var.get(), "Öğretmen günlük maksimum ders saati")
            self.db.ayar_ekle_veya_guncelle("ogretmen_gunluk_min_ders", self.ogretmen_gunluk_min_var.get(), "Öğretmen günlük minimum ders saati")
            self.db.ayar_ekle_veya_guncelle("ogretmen_bos_saat_tercihi", self.ogretmen_bos_saat_var.get(), "Öğretmen boş saat tercihi")
            
            messagebox.showinfo("Bilgi", "Öğretmen kısıtları başarıyla kaydedildi.")
            self.logger.info("Öğretmen kısıtları kaydedildi")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen sayısal değerleri doğru formatta girin.")
        except Exception as e:
            self.logger.error(f"Öğretmen kısıtları kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen kısıtları kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def save_class_settings(self):
        """
        Sınıf kısıtlarını kaydeder
        """
        try:
            # Veri doğrulama
            sinif_gunluk_max = int(self.sinif_gunluk_max_var.get())
            sinif_gunluk_min = int(self.sinif_gunluk_min_var.get())
            ayni_ders_tekrar = int(self.ayni_ders_tekrar_var.get())
            
            if sinif_gunluk_max <= 0:
                messagebox.showerror("Hata", "Sınıf günlük maksimum ders saati 0'dan büyük olmalıdır.")
                return
            
            if sinif_gunluk_min < 0:
                messagebox.showerror("Hata", "Sınıf günlük minimum ders saati negatif olamaz.")
                return
            
            if sinif_gunluk_min > sinif_gunluk_max:
                messagebox.showerror("Hata", "Sınıf günlük minimum ders saati, maksimum değerden büyük olamaz.")
                return
            
            if ayni_ders_tekrar <= 0:
                messagebox.showerror("Hata", "Aynı dersin aynı günde maksimum tekrarı 0'dan büyük olmalıdır.")
                return
            
            # Ayarları kaydet
            self.db.ayar_ekle_veya_guncelle("sinif_gunluk_max_ders", self.sinif_gunluk_max_var.get(), "Sınıf günlük maksimum ders saati")
            self.db.ayar_ekle_veya_guncelle("sinif_gunluk_min_ders", self.sinif_gunluk_min_var.get(), "Sınıf günlük minimum ders saati")
            self.db.ayar_ekle_veya_guncelle("ayni_ders_tekrar", self.ayni_ders_tekrar_var.get(), "Aynı dersin aynı günde maksimum tekrarı")
            
            messagebox.showinfo("Bilgi", "Sınıf kısıtları başarıyla kaydedildi.")
            self.logger.info("Sınıf kısıtları kaydedildi")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen sayısal değerleri doğru formatta girin.")
        except Exception as e:
            self.logger.error(f"Sınıf kısıtları kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf kısıtları kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def save_classroom_settings(self):
        """
        Derslik kısıtlarını kaydeder
        """
        try:
            # Ayarları kaydet
            self.db.ayar_ekle_veya_guncelle("ozel_derslik_zorunlu", "1" if self.ozel_derslik_var.get() else "0", "Özel derslik zorunluluğu")
            self.db.ayar_ekle_veya_guncelle("derslik_degisim_minimize", "1" if self.derslik_degisim_var.get() else "0", "Derslik değişim minimizasyonu")
            
            messagebox.showinfo("Bilgi", "Derslik kısıtları başarıyla kaydedildi.")
            self.logger.info("Derslik kısıtları kaydedildi")
        except Exception as e:
            self.logger.error(f"Derslik kısıtları kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Derslik kısıtları kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def save_general_settings(self):
        """
        Genel kısıtları kaydeder
        """
        try:
            # Veri doğrulama
            max_blok_ders = int(self.max_blok_ders_var.get())
            algoritma_sure = int(self.algoritma_sure_var.get())
            
            if max_blok_ders <= 0:
                messagebox.showerror("Hata", "Maksimum blok ders sayısı 0'dan büyük olmalıdır.")
                return
            
            if algoritma_sure <= 0:
                messagebox.showerror("Hata", "Algoritma çalışma süresi sınırı 0'dan büyük olmalıdır.")
                return
            
            # Ayarları kaydet
            self.db.ayar_ekle_veya_guncelle("blok_ders_arka_arkaya", "1" if self.blok_ders_var.get() else "0", "Blok dersleri arka arkaya yerleştir")
            self.db.ayar_ekle_veya_guncelle("max_blok_ders", self.max_blok_ders_var.get(), "Maksimum blok ders sayısı")
            self.db.ayar_ekle_veya_guncelle("algoritma_sure_siniri", self.algoritma_sure_var.get(), "Algoritma çalışma süresi sınırı (saniye)")
            
            messagebox.showinfo("Bilgi", "Genel kısıtlar başarıyla kaydedildi.")
            self.logger.info("Genel kısıtlar kaydedildi")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen sayısal değerleri doğru formatta girin.")
        except Exception as e:
            self.logger.error(f"Genel kısıtlar kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Genel kısıtlar kaydedilirken bir hata oluştu:\n{str(e)}")
