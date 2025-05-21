#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program oluşturma arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import time

from algorithm.scheduler import ProgramOlusturucu

class ProgramOlusturma:
    """
    Program oluşturma arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Program oluşturma arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Program oluşturucu
        self.scheduler = ProgramOlusturucu(self.db, self.config)
        
        # İş parçacığı
        self.thread = None
        self.is_running = False
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        self.logger.info("Program oluşturma arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Başlık
        ttk.Label(self.main_frame, text="Program Oluşturma", font=("TkDefaultFont", 16, "bold")).pack(pady=10)
        
        # Bilgi çerçevesi
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Bilgiler")
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sınıf sayısı
        ttk.Label(self.info_frame, text="Sınıf Sayısı:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.sinif_sayisi_label = ttk.Label(self.info_frame, text="0")
        self.sinif_sayisi_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Öğretmen sayısı
        ttk.Label(self.info_frame, text="Öğretmen Sayısı:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.ogretmen_sayisi_label = ttk.Label(self.info_frame, text="0")
        self.ogretmen_sayisi_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Ders sayısı
        ttk.Label(self.info_frame, text="Ders Sayısı:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.ders_sayisi_label = ttk.Label(self.info_frame, text="0")
        self.ders_sayisi_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Derslik sayısı
        ttk.Label(self.info_frame, text="Derslik Sayısı:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.derslik_sayisi_label = ttk.Label(self.info_frame, text="0")
        self.derslik_sayisi_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # İlişki sayısı
        ttk.Label(self.info_frame, text="İlişki Sayısı:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.iliski_sayisi_label = ttk.Label(self.info_frame, text="0")
        self.iliski_sayisi_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Kısıt sayısı
        ttk.Label(self.info_frame, text="Kısıt Sayısı:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.kisit_sayisi_label = ttk.Label(self.info_frame, text="0")
        self.kisit_sayisi_label.grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Ayarlar çerçevesi
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Ayarlar")
        self.settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Algoritma çalışma süresi sınırı
        ttk.Label(self.settings_frame, text="Algoritma Çalışma Süresi Sınırı (saniye):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sure_siniri_var = tk.StringVar()
        self.sure_siniri_entry = ttk.Entry(self.settings_frame, textvariable=self.sure_siniri_var, width=10)
        self.sure_siniri_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Ayarları yükle
        self.sure_siniri_var.set(self.db.ayar_getir("algoritma_sure_siniri", "300"))
        
        # Kaydet butonu
        self.save_settings_button = ttk.Button(self.settings_frame, text="Ayarları Kaydet", command=self.save_settings)
        self.save_settings_button.grid(row=0, column=2, padx=5, pady=5)
        
        # İlerleme çerçevesi
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="İlerleme")
        self.progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Durum etiketi
        self.status_label = ttk.Label(self.progress_frame, text="Hazır")
        self.status_label.pack(pady=5)
        
        # Butonlar çerçevesi
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Yenile butonu
        self.refresh_button = ttk.Button(self.button_frame, text="Bilgileri Yenile", command=self.refresh_info)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Program oluştur butonu
        self.create_button = ttk.Button(self.button_frame, text="Program Oluştur", command=self.create_schedule)
        self.create_button.pack(side=tk.RIGHT, padx=5)
        
        # İptal butonu
        self.cancel_button = ttk.Button(self.button_frame, text="İptal", command=self.cancel_schedule, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Sonuç çerçevesi
        self.result_frame = ttk.LabelFrame(self.main_frame, text="Sonuç")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sonuç metni
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text.config(state=tk.DISABLED)
        
        # Bilgileri yenile
        self.refresh_info()
    
    def refresh_info(self):
        """
        Bilgileri yeniler
        """
        try:
            # Sınıf sayısı
            self.db.execute("SELECT COUNT(*) as count FROM siniflar")
            sinif_sayisi = self.db.fetchone()["count"]
            self.sinif_sayisi_label.config(text=str(sinif_sayisi))
            
            # Öğretmen sayısı
            self.db.execute("SELECT COUNT(*) as count FROM ogretmenler")
            ogretmen_sayisi = self.db.fetchone()["count"]
            self.ogretmen_sayisi_label.config(text=str(ogretmen_sayisi))
            
            # Ders sayısı
            self.db.execute("SELECT COUNT(*) as count FROM dersler")
            ders_sayisi = self.db.fetchone()["count"]
            self.ders_sayisi_label.config(text=str(ders_sayisi))
            
            # Derslik sayısı
            self.db.execute("SELECT COUNT(*) as count FROM derslikler")
            derslik_sayisi = self.db.fetchone()["count"]
            self.derslik_sayisi_label.config(text=str(derslik_sayisi))
            
            # İlişki sayısı
            self.db.execute("SELECT COUNT(*) as count FROM ders_sinif")
            iliski_sayisi = self.db.fetchone()["count"]
            self.iliski_sayisi_label.config(text=str(iliski_sayisi))
            
            # Kısıt sayısı
            self.db.execute("SELECT COUNT(*) as count FROM uygun_olmayan_zamanlar")
            kisit_sayisi = self.db.fetchone()["count"]
            self.kisit_sayisi_label.config(text=str(kisit_sayisi))
            
            self.logger.info("Bilgiler başarıyla yenilendi")
        except Exception as e:
            self.logger.error(f"Bilgiler yenilenirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Bilgiler yenilenirken bir hata oluştu:\n{str(e)}")
    
    def save_settings(self):
        """
        Ayarları kaydeder
        """
        try:
            # Algoritma çalışma süresi sınırı
            sure_siniri = int(self.sure_siniri_var.get())
            
            if sure_siniri <= 0:
                messagebox.showerror("Hata", "Algoritma çalışma süresi sınırı 0'dan büyük olmalıdır.")
                return
            
            # Ayarları kaydet
            self.db.ayar_ekle_veya_guncelle("algoritma_sure_siniri", str(sure_siniri), "Algoritma çalışma süresi sınırı (saniye)")
            
            messagebox.showinfo("Bilgi", "Ayarlar başarıyla kaydedildi.")
            self.logger.info("Ayarlar kaydedildi")
        except ValueError:
            messagebox.showerror("Hata", "Lütfen sayısal değerleri doğru formatta girin.")
        except Exception as e:
            self.logger.error(f"Ayarlar kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def create_schedule(self):
        """
        Program oluşturma işlemini başlatır
        """
        if self.is_running:
            messagebox.showwarning("Uyarı", "Program oluşturma işlemi zaten çalışıyor.")
            return
        
        # Veri doğrulama
        try:
            # Sınıf sayısı
            self.db.execute("SELECT COUNT(*) as count FROM siniflar")
            sinif_sayisi = self.db.fetchone()["count"]
            if sinif_sayisi == 0:
                messagebox.showerror("Hata", "Hiç sınıf tanımlanmamış.")
                return
            
            # Öğretmen sayısı
            self.db.execute("SELECT COUNT(*) as count FROM ogretmenler")
            ogretmen_sayisi = self.db.fetchone()["count"]
            if ogretmen_sayisi == 0:
                messagebox.showerror("Hata", "Hiç öğretmen tanımlanmamış.")
                return
            
            # Ders sayısı
            self.db.execute("SELECT COUNT(*) as count FROM dersler")
            ders_sayisi = self.db.fetchone()["count"]
            if ders_sayisi == 0:
                messagebox.showerror("Hata", "Hiç ders tanımlanmamış.")
                return
            
            # İlişki sayısı
            self.db.execute("SELECT COUNT(*) as count FROM ders_sinif")
            iliski_sayisi = self.db.fetchone()["count"]
            if iliski_sayisi == 0:
                messagebox.showerror("Hata", "Hiç ders-sınıf ilişkisi tanımlanmamış.")
                return
            
            # Derslik sayısı
            self.db.execute("SELECT COUNT(*) as count FROM derslikler")
            derslik_sayisi = self.db.fetchone()["count"]
            if derslik_sayisi == 0:
                messagebox.showerror("Hata", "Hiç derslik tanımlanmamış.")
                return
        except Exception as e:
            self.logger.error(f"Veri doğrulama hatası: {str(e)}")
            messagebox.showerror("Hata", f"Veri doğrulama sırasında bir hata oluştu:\n{str(e)}")
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Program oluşturma işlemi başlatılacak. Bu işlem mevcut programı silecektir. Devam etmek istiyor musunuz?"):
            return
        
        # İş parçacığını başlat
        self.is_running = True
        self.thread = threading.Thread(target=self.run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        # Arayüzü güncelle
        self.update_ui_running()
    
    def run_scheduler(self):
        """
        Program oluşturucuyu çalıştırır
        """
        try:
            # Durum etiketini güncelle
            self.update_status("Program oluşturuluyor...")
            
            # İlerleme çubuğunu güncelle
            self.update_progress(10)
            
            # Verileri yükle
            self.update_status("Veriler yükleniyor...")
            self.scheduler.load_data()
            self.update_progress(20)
            
            # Modeli oluştur
            self.update_status("Model oluşturuluyor...")
            self.scheduler.create_model()
            self.update_progress(30)
            
            # Modeli çöz
            self.update_status("Model çözülüyor...")
            start_time = time.time()
            success = self.scheduler.solve()
            end_time = time.time()
            self.update_progress(80)
            
            if success:
                # Çözümü kaydet
                self.update_status("Çözüm kaydediliyor...")
                self.scheduler.save_solution()
                self.update_progress(100)
                
                # Sonuç metnini güncelle
                self.update_result(f"Program başarıyla oluşturuldu!\n\nÇözüm süresi: {end_time - start_time:.2f} saniye")
                
                # Durum etiketini güncelle
                self.update_status("Program oluşturuldu")
            else:
                # Sonuç metnini güncelle
                self.update_result(f"Program oluşturulamadı!\n\nÇalışma süresi: {end_time - start_time:.2f} saniye\n\nNedeni: Verilen kısıtlar altında uygun bir çözüm bulunamadı.")
                
                # Durum etiketini güncelle
                self.update_status("Program oluşturulamadı")
        except Exception as e:
            self.logger.error(f"Program oluşturma hatası: {str(e)}")
            self.update_result(f"Program oluşturulurken bir hata oluştu:\n\n{str(e)}")
            self.update_status("Hata oluştu")
        finally:
            # İş parçacığını sonlandır
            self.is_running = False
            
            # Arayüzü güncelle
            self.parent.after(0, self.update_ui_stopped)
    
    def cancel_schedule(self):
        """
        Program oluşturma işlemini iptal eder
        """
        if not self.is_running:
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Program oluşturma işlemi iptal edilecek. Emin misiniz?"):
            return
        
        # İş parçacığını sonlandır
        self.is_running = False
        
        # Durum etiketini güncelle
        self.update_status("İptal edildi")
    
    def update_ui_running(self):
        """
        Arayüzü çalışma durumuna göre günceller
        """
        # Butonları güncelle
        self.create_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.DISABLED)
        self.save_settings_button.config(state=tk.DISABLED)
        
        # Giriş alanlarını devre dışı bırak
        self.sure_siniri_entry.config(state=tk.DISABLED)
        
        # İlerleme çubuğunu sıfırla
        self.progress_var.set(0)
        
        # Sonuç metnini temizle
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
    
    def update_ui_stopped(self):
        """
        Arayüzü durma durumuna göre günceller
        """
        # Butonları güncelle
        self.create_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.NORMAL)
        self.save_settings_button.config(state=tk.NORMAL)
        
        # Giriş alanlarını etkinleştir
        self.sure_siniri_entry.config(state=tk.NORMAL)
    
    def update_status(self, text):
        """
        Durum etiketini günceller
        
        Args:
            text (str): Durum metni
        """
        self.parent.after(0, lambda: self.status_label.config(text=text))
    
    def update_progress(self, value):
        """
        İlerleme çubuğunu günceller
        
        Args:
            value (int): İlerleme değeri (0-100)
        """
        self.parent.after(0, lambda: self.progress_var.set(value))
    
    def update_result(self, text):
        """
        Sonuç metnini günceller
        
        Args:
            text (str): Sonuç metni
        """
        def _update():
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, text)
            self.result_text.config(state=tk.DISABLED)
        
        self.parent.after(0, _update)
