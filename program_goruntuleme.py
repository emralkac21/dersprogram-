#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program görüntüleme ve düzenleme arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

class ProgramGoruntuleme:
    """
    Program görüntüleme ve düzenleme arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Program görüntüleme ve düzenleme arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Seçili program öğesi
        self.selected_id = None
        
        # Görünüm modu (sinif, ogretmen, derslik)
        self.view_mode = tk.StringVar(value="sinif")
        
        # Seçili filtre değerleri
        self.selected_sinif_id = None
        self.selected_ogretmen_id = None
        self.selected_derslik_id = None
        
        # Zaman ayarları
        self.load_time_settings()
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Programı yükle
        self.refresh_schedule()
        
        self.logger.info("Program görüntüleme ve düzenleme arayüzü oluşturuldu")
    
    def load_time_settings(self):
        """
        Zaman ayarlarını yükler
        """
        try:
            # Ders süresi
            self.ders_suresi = int(self.db.ayar_getir("ders_suresi", "40"))
            
            # Teneffüs süresi
            self.teneffus_suresi = int(self.db.ayar_getir("teneffus_suresi", "10"))
            
            # Günlük ders başlangıç saati
            self.baslangic_saati = self.db.ayar_getir("gunluk_ders_baslangic", "08:30")
            
            # Günlük ders bitiş saati
            self.bitis_saati = self.db.ayar_getir("gunluk_ders_bitis", "16:00")
            
            # Öğle arası başlangıç saati
            self.ogle_baslangic = self.db.ayar_getir("ogle_arasi_baslangic", "12:00")
            
            # Öğle arası bitiş saati
            self.ogle_bitis = self.db.ayar_getir("ogle_arasi_bitis", "13:00")
            
            # Maksimum günlük ders saati
            self.max_gunluk_ders = int(self.db.ayar_getir("max_gunluk_ders", "8"))
            
            # Gün adları
            self.gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
            
            self.logger.info("Zaman ayarları başarıyla yüklendi")
        except Exception as e:
            self.logger.error(f"Zaman ayarları yüklenirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Zaman ayarları yüklenirken bir hata oluştu:\n{str(e)}")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Üst panel - Filtreler ve kontroller
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Görünüm modu seçimi
        ttk.Label(self.top_frame, text="Görünüm:").pack(side=tk.LEFT, padx=5)
        
        self.sinif_radio = ttk.Radiobutton(self.top_frame, text="Sınıf", variable=self.view_mode, value="sinif", command=self.change_view_mode)
        self.sinif_radio.pack(side=tk.LEFT, padx=5)
        
        self.ogretmen_radio = ttk.Radiobutton(self.top_frame, text="Öğretmen", variable=self.view_mode, value="ogretmen", command=self.change_view_mode)
        self.ogretmen_radio.pack(side=tk.LEFT, padx=5)
        
        self.derslik_radio = ttk.Radiobutton(self.top_frame, text="Derslik", variable=self.view_mode, value="derslik", command=self.change_view_mode)
        self.derslik_radio.pack(side=tk.LEFT, padx=5)
        
        # Filtre seçimi
        ttk.Label(self.top_frame, text="Filtre:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.top_frame, textvariable=self.filter_var, state="readonly", width=30)
        self.filter_combobox.pack(side=tk.LEFT, padx=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # Yenile butonu
        self.refresh_button = ttk.Button(self.top_frame, text="Yenile", command=self.refresh_schedule)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Orta panel - Program tablosu
        self.schedule_frame = ttk.LabelFrame(self.main_frame, text="Haftalık Program")
        self.schedule_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Program tablosu
        self.create_schedule_table()
        
        # Alt panel - Düzenleme kontrolleri
        self.edit_frame = ttk.LabelFrame(self.main_frame, text="Program Düzenleme")
        self.edit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Seçili ders bilgileri
        self.info_frame = ttk.Frame(self.edit_frame)
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.info_frame, text="Seçili Ders:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.selected_info_label = ttk.Label(self.info_frame, text="-")
        self.selected_info_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Düzenleme kontrolleri
        self.edit_controls_frame = ttk.Frame(self.edit_frame)
        self.edit_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Gün seçimi
        ttk.Label(self.edit_controls_frame, text="Gün:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.gun_var = tk.StringVar()
        self.gun_combobox = ttk.Combobox(self.edit_controls_frame, textvariable=self.gun_var, state="readonly", width=15)
        self.gun_combobox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.gun_combobox["values"] = self.gun_adlari
        
        # Saat seçimi
        ttk.Label(self.edit_controls_frame, text="Saat:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.saat_var = tk.StringVar()
        self.saat_combobox = ttk.Combobox(self.edit_controls_frame, textvariable=self.saat_var, state="readonly", width=10)
        self.saat_combobox.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.saat_combobox["values"] = [str(i+1) for i in range(self.max_gunluk_ders)]
        
        # Derslik seçimi
        ttk.Label(self.edit_controls_frame, text="Derslik:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        self.derslik_var = tk.StringVar()
        self.derslik_combobox = ttk.Combobox(self.edit_controls_frame, textvariable=self.derslik_var, state="readonly", width=20)
        self.derslik_combobox.grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)
        
        # Derslikleri yükle
        self.load_derslikler()
        
        # Düzenleme butonları
        self.edit_buttons_frame = ttk.Frame(self.edit_frame)
        self.edit_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.move_button = ttk.Button(self.edit_buttons_frame, text="Dersi Taşı", command=self.move_lesson, state=tk.DISABLED)
        self.move_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(self.edit_buttons_frame, text="Dersi Sil", command=self.delete_lesson, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Filtreleri yükle
        self.load_filters()
    
    def create_schedule_table(self):
        """
        Program tablosunu oluşturur
        """
        # Mevcut tabloyu temizle
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        # Tablo çerçevesi
        self.table_frame = ttk.Frame(self.schedule_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Saat başlıkları
        ttk.Label(self.table_frame, text="Saat / Gün", width=15, anchor=tk.CENTER, 
                 borderwidth=1, relief="solid").grid(row=0, column=0, sticky=tk.NSEW)
        
        # Gün başlıkları
        for i, gun in enumerate(self.gun_adlari):
            ttk.Label(self.table_frame, text=gun, width=20, anchor=tk.CENTER, 
                     borderwidth=1, relief="solid").grid(row=0, column=i+1, sticky=tk.NSEW)
        
        # Saat etiketleri ve ders hücreleri
        for saat in range(self.max_gunluk_ders):
            # Saat etiketi
            saat_baslangic = self.calculate_time(saat)
            saat_bitis = self.calculate_time(saat + 1, teneffus=True)
            
            ttk.Label(self.table_frame, text=f"{saat+1}. Ders\n{saat_baslangic}-{saat_bitis}", 
                     width=15, anchor=tk.CENTER, borderwidth=1, relief="solid").grid(
                     row=saat+1, column=0, sticky=tk.NSEW)
            
            # Ders hücreleri
            for gun in range(len(self.gun_adlari)):
                frame = ttk.Frame(self.table_frame, borderwidth=1, relief="solid")
                frame.grid(row=saat+1, column=gun+1, sticky=tk.NSEW)
                
                # Hücre içeriği
                self.create_cell_content(frame, gun, saat)
                
                # Hücre tıklama olayı
                frame.bind("<Button-1>", lambda e, g=gun, s=saat: self.on_cell_click(g, s))
        
        # Sütunları genişlet
        for i in range(len(self.gun_adlari) + 1):
            self.table_frame.columnconfigure(i, weight=1)
        
        # Satırları genişlet
        for i in range(self.max_gunluk_ders + 1):
            self.table_frame.rowconfigure(i, weight=1)
    
    def create_cell_content(self, frame, gun, saat):
        """
        Hücre içeriğini oluşturur
        
        Args:
            frame (ttk.Frame): Hücre çerçevesi
            gun (int): Gün indeksi
            saat (int): Saat indeksi
        """
        # Hücre içeriğini temizle
        for widget in frame.winfo_children():
            widget.destroy()
        
        # Ders bilgisini al
        ders_bilgisi = self.get_ders_bilgisi(gun, saat)
        
        if ders_bilgisi:
            # Ders bilgisi varsa
            bg_color = self.get_ders_color(ders_bilgisi["ders_id"])
            
            # Çerçeve arka plan rengi
            cell_frame = tk.Frame(frame, bg=bg_color)
            cell_frame.pack(fill=tk.BOTH, expand=True)
            
            # Ders adı
            ders_label = tk.Label(cell_frame, text=ders_bilgisi["ders_adi"], 
                                 font=("TkDefaultFont", 9, "bold"), bg=bg_color)
            ders_label.pack(pady=(2, 0))
            
            # Görünüm moduna göre ek bilgiler
            if self.view_mode.get() == "sinif":
                # Öğretmen adı
                ogretmen_label = tk.Label(cell_frame, text=ders_bilgisi["ogretmen_adi"], 
                                         font=("TkDefaultFont", 8), bg=bg_color)
                ogretmen_label.pack()
                
                # Derslik adı
                derslik_label = tk.Label(cell_frame, text=ders_bilgisi["derslik_adi"], 
                                        font=("TkDefaultFont", 8), bg=bg_color)
                derslik_label.pack()
            
            elif self.view_mode.get() == "ogretmen":
                # Sınıf adı
                sinif_label = tk.Label(cell_frame, text=f"{ders_bilgisi['sinif_adi']} {ders_bilgisi['sinif_sube']}", 
                                      font=("TkDefaultFont", 8), bg=bg_color)
                sinif_label.pack()
                
                # Derslik adı
                derslik_label = tk.Label(cell_frame, text=ders_bilgisi["derslik_adi"], 
                                        font=("TkDefaultFont", 8), bg=bg_color)
                derslik_label.pack()
            
            elif self.view_mode.get() == "derslik":
                # Sınıf adı
                sinif_label = tk.Label(cell_frame, text=f"{ders_bilgisi['sinif_adi']} {ders_bilgisi['sinif_sube']}", 
                                      font=("TkDefaultFont", 8), bg=bg_color)
                sinif_label.pack()
                
                # Öğretmen adı
                ogretmen_label = tk.Label(cell_frame, text=ders_bilgisi["ogretmen_adi"], 
                                         font=("TkDefaultFont", 8), bg=bg_color)
                ogretmen_label.pack()
            
            # Hücre tıklama olayı
            cell_frame.bind("<Button-1>", lambda e, id=ders_bilgisi["id"]: self.on_lesson_click(id))
            for child in cell_frame.winfo_children():
                child.bind("<Button-1>", lambda e, id=ders_bilgisi["id"]: self.on_lesson_click(id))
    
    def get_ders_bilgisi(self, gun, saat):
        """
        Belirli bir gün ve saatteki ders bilgisini döndürür
        
        Args:
            gun (int): Gün indeksi
            saat (int): Saat indeksi
            
        Returns:
            dict: Ders bilgisi
        """
        try:
            # Görünüm moduna göre sorgu
            if self.view_mode.get() == "sinif" and self.selected_sinif_id:
                # Sınıf görünümü
                self.db.execute("""
                    SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                           o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                           dr.ad as derslik_adi
                    FROM program p
                    JOIN siniflar s ON p.sinif_id = s.id
                    JOIN ogretmenler o ON p.ogretmen_id = o.id
                    JOIN dersler d ON p.ders_id = d.id
                    JOIN derslikler dr ON p.derslik_id = dr.id
                    WHERE p.sinif_id = ? AND p.gun = ? AND p.saat = ?
                """, (self.selected_sinif_id, gun, saat))
            
            elif self.view_mode.get() == "ogretmen" and self.selected_ogretmen_id:
                # Öğretmen görünümü
                self.db.execute("""
                    SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                           o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                           dr.ad as derslik_adi
                    FROM program p
                    JOIN siniflar s ON p.sinif_id = s.id
                    JOIN ogretmenler o ON p.ogretmen_id = o.id
                    JOIN dersler d ON p.ders_id = d.id
                    JOIN derslikler dr ON p.derslik_id = dr.id
                    WHERE p.ogretmen_id = ? AND p.gun = ? AND p.saat = ?
                """, (self.selected_ogretmen_id, gun, saat))
            
            elif self.view_mode.get() == "derslik" and self.selected_derslik_id:
                # Derslik görünümü
                self.db.execute("""
                    SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                           o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                           dr.ad as derslik_adi
                    FROM program p
                    JOIN siniflar s ON p.sinif_id = s.id
                    JOIN ogretmenler o ON p.ogretmen_id = o.id
                    JOIN dersler d ON p.ders_id = d.id
                    JOIN derslikler dr ON p.derslik_id = dr.id
                    WHERE p.derslik_id = ? AND p.gun = ? AND p.saat = ?
                """, (self.selected_derslik_id, gun, saat))
            
            else:
                return None
            
            return self.db.fetchone()
        except Exception as e:
            self.logger.error(f"Ders bilgisi alınırken hata oluştu: {str(e)}")
            return None
    
    def get_ders_color(self, ders_id):
        """
        Ders ID'sine göre renk döndürür
        
        Args:
            ders_id (int): Ders ID'si
            
        Returns:
            str: Renk kodu
        """
        # Ders ID'sine göre sabit bir renk üret
        colors = [
            "#FFD6D6", "#D6FFD6", "#D6D6FF", "#FFFFD6", "#FFD6FF", "#D6FFFF",
            "#FFE0D6", "#D6FFE0", "#E0D6FF", "#FFFFE0", "#FFE0FF", "#E0FFFF"
        ]
        
        return colors[ders_id % len(colors)]
    
    def calculate_time(self, period_index, teneffus=False):
        """
        Ders saatini hesaplar
        
        Args:
            period_index (int): Ders indeksi
            teneffus (bool): Teneffüs dahil mi?
            
        Returns:
            str: Saat formatında zaman
        """
        try:
            # Başlangıç saatini parse et
            hour, minute = map(int, self.baslangic_saati.split(":"))
            
            # Toplam dakika
            total_minutes = hour * 60 + minute
            
            # Ders indeksine göre dakika ekle
            if period_index > 0:
                for i in range(period_index):
                    # Ders süresi ekle
                    total_minutes += self.ders_suresi
                    
                    # Teneffüs süresi ekle (son ders için teneffüs eklenmez)
                    if i < period_index - 1 or teneffus:
                        total_minutes += self.teneffus_suresi
            
            # Öğle arası kontrolü
            ogle_baslangic_hour, ogle_baslangic_minute = map(int, self.ogle_baslangic.split(":"))
            ogle_bitis_hour, ogle_bitis_minute = map(int, self.ogle_bitis.split(":"))
            
            ogle_baslangic_minutes = ogle_baslangic_hour * 60 + ogle_baslangic_minute
            ogle_bitis_minutes = ogle_bitis_hour * 60 + ogle_bitis_minute
            
            # Eğer hesaplanan zaman öğle arası içindeyse, öğle arası sonrasına kaydır
            if ogle_baslangic_minutes <= total_minutes < ogle_bitis_minutes:
                total_minutes = ogle_bitis_minutes
            
            # Dakikayı saat ve dakika olarak dönüştür
            hour = total_minutes // 60
            minute = total_minutes % 60
            
            # Saat formatında döndür
            return f"{hour:02d}:{minute:02d}"
        except Exception as e:
            self.logger.error(f"Saat hesaplanırken hata oluştu: {str(e)}")
            return "00:00"
    
    def load_filters(self):
        """
        Filtre seçeneklerini yükler
        """
        try:
            # Görünüm moduna göre filtre seçeneklerini yükle
            if self.view_mode.get() == "sinif":
                # Sınıfları yükle
                self.db.execute("SELECT id, ad, sube FROM siniflar ORDER BY ad, sube")
                siniflar = self.db.fetchall()
                
                # Combobox değerlerini ayarla
                self.filter_combobox["values"] = [f"{sinif['ad']} {sinif['sube']}" for sinif in siniflar]
                
                # Sınıf ID'lerini sakla
                self.filter_combobox.sinif_ids = {f"{sinif['ad']} {sinif['sube']}": sinif["id"] for sinif in siniflar}
                
                # İlk sınıfı seç
                if siniflar:
                    self.filter_var.set(f"{siniflar[0]['ad']} {siniflar[0]['sube']}")
                    self.selected_sinif_id = siniflar[0]["id"]
                else:
                    self.filter_var.set("")
                    self.selected_sinif_id = None
            
            elif self.view_mode.get() == "ogretmen":
                # Öğretmenleri yükle
                self.db.execute("SELECT id, ad_soyad FROM ogretmenler ORDER BY ad_soyad")
                ogretmenler = self.db.fetchall()
                
                # Combobox değerlerini ayarla
                self.filter_combobox["values"] = [ogretmen["ad_soyad"] for ogretmen in ogretmenler]
                
                # Öğretmen ID'lerini sakla
                self.filter_combobox.ogretmen_ids = {ogretmen["ad_soyad"]: ogretmen["id"] for ogretmen in ogretmenler}
                
                # İlk öğretmeni seç
                if ogretmenler:
                    self.filter_var.set(ogretmenler[0]["ad_soyad"])
                    self.selected_ogretmen_id = ogretmenler[0]["id"]
                else:
                    self.filter_var.set("")
                    self.selected_ogretmen_id = None
            
            elif self.view_mode.get() == "derslik":
                # Derslikleri yükle
                self.db.execute("SELECT id, ad FROM derslikler ORDER BY ad")
                derslikler = self.db.fetchall()
                
                # Combobox değerlerini ayarla
                self.filter_combobox["values"] = [derslik["ad"] for derslik in derslikler]
                
                # Derslik ID'lerini sakla
                self.filter_combobox.derslik_ids = {derslik["ad"]: derslik["id"] for derslik in derslikler}
                
                # İlk dersliği seç
                if derslikler:
                    self.filter_var.set(derslikler[0]["ad"])
                    self.selected_derslik_id = derslikler[0]["id"]
                else:
                    self.filter_var.set("")
                    self.selected_derslik_id = None
            
            self.logger.info(f"Filtreler başarıyla yüklendi: {self.view_mode.get()}")
        except Exception as e:
            self.logger.error(f"Filtreler yüklenirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Filtreler yüklenirken bir hata oluştu:\n{str(e)}")
    
    def load_derslikler(self):
        """
        Derslikleri yükler
        """
        try:
            # Derslikleri yükle
            self.db.execute("SELECT id, ad FROM derslikler ORDER BY ad")
            derslikler = self.db.fetchall()
            
            # Combobox değerlerini ayarla
            self.derslik_combobox["values"] = [derslik["ad"] for derslik in derslikler]
            
            # Derslik ID'lerini sakla
            self.derslik_combobox.derslik_ids = {derslik["ad"]: derslik["id"] for derslik in derslikler}
            
            self.logger.info(f"{len(derslikler)} derslik yüklendi")
        except Exception as e:
            self.logger.error(f"Derslikler yüklenirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Derslikler yüklenirken bir hata oluştu:\n{str(e)}")
    
    def change_view_mode(self):
        """
        Görünüm modunu değiştirir
        """
        # Filtreleri yükle
        self.load_filters()
        
        # Programı yenile
        self.refresh_schedule()
        
        # Seçili dersi temizle
        self.clear_selection()
        
        self.logger.info(f"Görünüm modu değiştirildi: {self.view_mode.get()}")
    
    def on_filter_change(self, event):
        """
        Filtre değiştiğinde çağrılır
        
        Args:
            event: Combobox seçim olayı
        """
        # Seçili filtreyi güncelle
        selected_value = self.filter_var.get()
        
        if self.view_mode.get() == "sinif" and hasattr(self.filter_combobox, "sinif_ids"):
            self.selected_sinif_id = self.filter_combobox.sinif_ids.get(selected_value)
        
        elif self.view_mode.get() == "ogretmen" and hasattr(self.filter_combobox, "ogretmen_ids"):
            self.selected_ogretmen_id = self.filter_combobox.ogretmen_ids.get(selected_value)
        
        elif self.view_mode.get() == "derslik" and hasattr(self.filter_combobox, "derslik_ids"):
            self.selected_derslik_id = self.filter_combobox.derslik_ids.get(selected_value)
        
        # Programı yenile
        self.refresh_schedule()
        
        # Seçili dersi temizle
        self.clear_selection()
        
        self.logger.info(f"Filtre değiştirildi: {selected_value}")
    
    def refresh_schedule(self):
        """
        Program tablosunu yeniler
        """
        # Program tablosunu yeniden oluştur
        self.create_schedule_table()
        
        self.logger.info("Program tablosu yenilendi")
    
    def on_cell_click(self, gun, saat):
        """
        Hücre tıklandığında çağrılır
        
        Args:
            gun (int): Gün indeksi
            saat (int): Saat indeksi
        """
        # Ders bilgisini al
        ders_bilgisi = self.get_ders_bilgisi(gun, saat)
        
        if ders_bilgisi:
            # Ders varsa, seç
            self.on_lesson_click(ders_bilgisi["id"])
        else:
            # Ders yoksa, seçimi temizle
            self.clear_selection()
    
    def on_lesson_click(self, program_id):
        """
        Ders tıklandığında çağrılır
        
        Args:
            program_id (int): Program ID'si
        """
        try:
            # Program bilgisini al
            self.db.execute("""
                SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                       o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                       dr.ad as derslik_adi
                FROM program p
                JOIN siniflar s ON p.sinif_id = s.id
                JOIN ogretmenler o ON p.ogretmen_id = o.id
                JOIN dersler d ON p.ders_id = d.id
                JOIN derslikler dr ON p.derslik_id = dr.id
                WHERE p.id = ?
            """, (program_id,))
            
            program = self.db.fetchone()
            
            if program:
                # Seçili ID'yi güncelle
                self.selected_id = program_id
                
                # Seçili ders bilgisini güncelle
                self.selected_info_label.config(
                    text=f"{program['ders_adi']} - {program['sinif_adi']} {program['sinif_sube']} - {program['ogretmen_adi']} - {program['derslik_adi']}"
                )
                
                # Düzenleme kontrollerini güncelle
                self.gun_var.set(self.gun_adlari[program["gun"]])
                self.saat_var.set(str(program["saat"] + 1))
                self.derslik_var.set(program["derslik_adi"])
                
                # Düzenleme butonlarını etkinleştir
                self.move_button.config(state=tk.NORMAL)
                self.delete_button.config(state=tk.NORMAL)
                
                self.logger.info(f"Ders seçildi: {program_id}")
            else:
                self.clear_selection()
        except Exception as e:
            self.logger.error(f"Ders seçilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ders seçilirken bir hata oluştu:\n{str(e)}")
    
    def clear_selection(self):
        """
        Seçimi temizler
        """
        # Seçili ID'yi temizle
        self.selected_id = None
        
        # Seçili ders bilgisini temizle
        self.selected_info_label.config(text="-")
        
        # Düzenleme kontrollerini temizle
        self.gun_var.set("")
        self.saat_var.set("")
        self.derslik_var.set("")
        
        # Düzenleme butonlarını devre dışı bırak
        self.move_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
    
    def move_lesson(self):
        """
        Seçili dersi taşır
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen taşınacak dersi seçin.")
            return
        
        # Seçili değerleri al
        gun = self.gun_adlari.index(self.gun_var.get()) if self.gun_var.get() in self.gun_adlari else -1
        saat = int(self.saat_var.get()) - 1 if self.saat_var.get().isdigit() else -1
        derslik_adi = self.derslik_var.get()
        
        # Değerleri kontrol et
        if gun == -1 or saat == -1 or not derslik_adi:
            messagebox.showerror("Hata", "Lütfen geçerli bir gün, saat ve derslik seçin.")
            return
        
        # Derslik ID'sini al
        derslik_id = self.derslik_combobox.derslik_ids.get(derslik_adi)
        if not derslik_id:
            messagebox.showerror("Hata", "Geçerli bir derslik seçin.")
            return
        
        try:
            # Hedef konumda ders var mı kontrol et
            self.db.execute("""
                SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                       o.ad_soyad as ogretmen_adi, d.ad as ders_adi
                FROM program p
                JOIN siniflar s ON p.sinif_id = s.id
                JOIN ogretmenler o ON p.ogretmen_id = o.id
                JOIN dersler d ON p.ders_id = d.id
                WHERE p.gun = ? AND p.saat = ? AND p.derslik_id = ?
            """, (gun, saat, derslik_id))
            
            existing = self.db.fetchone()
            
            if existing:
                # Hedef konumda ders varsa, uyar
                if not messagebox.askyesno("Uyarı", 
                    f"Hedef konumda zaten bir ders var:\n\n"
                    f"{existing['ders_adi']} - {existing['sinif_adi']} {existing['sinif_sube']} - {existing['ogretmen_adi']}\n\n"
                    f"Bu dersi silip, seçili dersi taşımak istiyor musunuz?"):
                    return
                
                # Mevcut dersi sil
                self.db.execute("DELETE FROM program WHERE id = ?", (existing["id"],))
            
            # Seçili dersin bilgilerini al
            self.db.execute("""
                SELECT * FROM program WHERE id = ?
            """, (self.selected_id,))
            
            program = self.db.fetchone()
            
            # Dersi taşı
            self.db.execute("""
                UPDATE program
                SET gun = ?, saat = ?, derslik_id = ?
                WHERE id = ?
            """, (gun, saat, derslik_id, self.selected_id))
            
            # Çakışma kontrolü - Sınıf
            self.db.execute("""
                SELECT COUNT(*) as count
                FROM program
                WHERE sinif_id = ? AND gun = ? AND saat = ? AND id != ?
            """, (program["sinif_id"], gun, saat, self.selected_id))
            
            sinif_conflict = self.db.fetchone()["count"] > 0
            
            # Çakışma kontrolü - Öğretmen
            self.db.execute("""
                SELECT COUNT(*) as count
                FROM program
                WHERE ogretmen_id = ? AND gun = ? AND saat = ? AND id != ?
            """, (program["ogretmen_id"], gun, saat, self.selected_id))
            
            ogretmen_conflict = self.db.fetchone()["count"] > 0
            
            # Çakışma uyarısı
            if sinif_conflict or ogretmen_conflict:
                warning_message = "Ders taşındı, ancak aşağıdaki çakışmalar oluştu:\n\n"
                
                if sinif_conflict:
                    warning_message += "- Aynı sınıfın bu saatte başka bir dersi var!\n"
                
                if ogretmen_conflict:
                    warning_message += "- Aynı öğretmenin bu saatte başka bir dersi var!\n"
                
                messagebox.showwarning("Çakışma Uyarısı", warning_message)
            else:
                messagebox.showinfo("Bilgi", "Ders başarıyla taşındı.")
            
            # Programı yenile
            self.refresh_schedule()
            
            # Seçimi temizle
            self.clear_selection()
            
            self.logger.info(f"Ders taşındı: {self.selected_id} -> Gün: {gun}, Saat: {saat}, Derslik: {derslik_id}")
        except Exception as e:
            self.logger.error(f"Ders taşınırken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ders taşınırken bir hata oluştu:\n{str(e)}")
    
    def delete_lesson(self):
        """
        Seçili dersi siler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen silinecek dersi seçin.")
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili dersi silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # Dersi sil
            self.db.execute("DELETE FROM program WHERE id = ?", (self.selected_id,))
            
            messagebox.showinfo("Bilgi", "Ders başarıyla silindi.")
            
            # Programı yenile
            self.refresh_schedule()
            
            # Seçimi temizle
            self.clear_selection()
            
            self.logger.info(f"Ders silindi: {self.selected_id}")
        except Exception as e:
            self.logger.error(f"Ders silinirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ders silinirken bir hata oluştu:\n{str(e)}")
