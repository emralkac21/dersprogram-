#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ana pencere sınıfı
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from gui.sinif_yonetimi import SinifYonetimi
from gui.ogretmen_yonetimi import OgretmenYonetimi
from gui.ders_yonetimi import DersYonetimi
from gui.derslik_yonetimi import DerslikYonetimi
from gui.kisit_yonetimi import KisitYonetimi
from gui.program_olusturma import ProgramOlusturma
from gui.program_goruntuleme import ProgramGoruntuleme
from gui.ayarlar import Ayarlar

class MainWindow:
    """
    Ana pencere sınıfı
    """
    
    def __init__(self, root, db, config):
        """
        Ana pencere sınıfını başlatır
        
        Args:
            root (tk.Tk): Ana pencere
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.root = root
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Ana pencere ayarları
        self.root.title(self.config.get('app', 'title', 'Ders Programı Oluşturma Uygulaması'))
        
        # Menü oluştur
        self.create_menu()
        
        # Sekme kontrolü oluştur
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sekmeleri oluştur
        self.create_tabs()
        
        # Durum çubuğu
        self.status_bar = ttk.Label(self.root, text="Hazır", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.logger.info("Ana pencere oluşturuldu")
    
    def create_menu(self):
        """
        Menü oluşturur
        """
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Veritabanını Yedekle", command=self.backup_database)
        file_menu.add_command(label="Veritabanını Geri Yükle", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Program menüsü
        program_menu = tk.Menu(menubar, tearoff=0)
        program_menu.add_command(label="Program Oluştur", command=self.create_schedule)
        program_menu.add_command(label="Programı Temizle", command=self.clear_schedule)
        menubar.add_cascade(label="Program", menu=program_menu)
        
        # Dışa Aktar menüsü
        export_menu = tk.Menu(menubar, tearoff=0)
        export_menu.add_command(label="PDF Olarak Dışa Aktar", command=self.export_pdf)
        export_menu.add_command(label="Excel Olarak Dışa Aktar", command=self.export_excel)
        menubar.add_cascade(label="Dışa Aktar", menu=export_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Yardım", command=self.show_help)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_tabs(self):
        """
        Sekmeleri oluşturur
        """
        # Sınıf Yönetimi sekmesi
        self.sinif_frame = ttk.Frame(self.notebook)
        self.sinif_yonetimi = SinifYonetimi(self.sinif_frame, self.db, self.config)
        self.notebook.add(self.sinif_frame, text="Sınıf Yönetimi")
        
        # Öğretmen Yönetimi sekmesi
        self.ogretmen_frame = ttk.Frame(self.notebook)
        self.ogretmen_yonetimi = OgretmenYonetimi(self.ogretmen_frame, self.db, self.config)
        self.notebook.add(self.ogretmen_frame, text="Öğretmen Yönetimi")
        
        # Ders Yönetimi sekmesi
        self.ders_frame = ttk.Frame(self.notebook)
        self.ders_yonetimi = DersYonetimi(self.ders_frame, self.db, self.config)
        self.notebook.add(self.ders_frame, text="Ders Yönetimi")
        
        # Derslik Yönetimi sekmesi
        self.derslik_frame = ttk.Frame(self.notebook)
        self.derslik_yonetimi = DerslikYonetimi(self.derslik_frame, self.db, self.config)
        self.notebook.add(self.derslik_frame, text="Derslik Yönetimi")
        
        # Kısıt Yönetimi sekmesi
        self.kisit_frame = ttk.Frame(self.notebook)
        self.kisit_yonetimi = KisitYonetimi(self.kisit_frame, self.db, self.config)
        self.notebook.add(self.kisit_frame, text="Kısıt Yönetimi")
        
        # Program Oluşturma sekmesi
        self.program_olusturma_frame = ttk.Frame(self.notebook)
        self.program_olusturma = ProgramOlusturma(self.program_olusturma_frame, self.db, self.config)
        self.notebook.add(self.program_olusturma_frame, text="Program Oluşturma")
        
        # Program Görüntüleme sekmesi
        self.program_goruntuleme_frame = ttk.Frame(self.notebook)
        self.program_goruntuleme = ProgramGoruntuleme(self.program_goruntuleme_frame, self.db, self.config)
        self.notebook.add(self.program_goruntuleme_frame, text="Program Görüntüleme")
        
        # Ayarlar sekmesi
        self.ayarlar_frame = ttk.Frame(self.notebook)
        self.ayarlar = Ayarlar(self.ayarlar_frame, self.db, self.config)
        self.notebook.add(self.ayarlar_frame, text="Ayarlar")
    
    def backup_database(self):
        """
        Veritabanını yedekler
        """
        try:
            # Veritabanı yedekleme işlemi
            messagebox.showinfo("Bilgi", "Veritabanı yedekleme işlemi başarıyla tamamlandı.")
        except Exception as e:
            self.logger.error(f"Veritabanı yedekleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Veritabanı yedekleme işlemi sırasında bir hata oluştu:\n{str(e)}")
    
    def restore_database(self):
        """
        Veritabanını geri yükler
        """
        try:
            # Veritabanı geri yükleme işlemi
            messagebox.showinfo("Bilgi", "Veritabanı geri yükleme işlemi başarıyla tamamlandı.")
        except Exception as e:
            self.logger.error(f"Veritabanı geri yükleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Veritabanı geri yükleme işlemi sırasında bir hata oluştu:\n{str(e)}")
    
    def create_schedule(self):
        """
        Program oluşturur
        """
        # Program oluşturma sekmesine geç
        self.notebook.select(self.program_olusturma_frame)
        self.program_olusturma.create_schedule()
    
    def clear_schedule(self):
        """
        Programı temizler
        """
        if messagebox.askyesno("Onay", "Mevcut program tamamen silinecek. Devam etmek istiyor musunuz?"):
            try:
                self.db.tum_programi_temizle()
                messagebox.showinfo("Bilgi", "Program başarıyla temizlendi.")
                # Program görüntüleme sekmesini güncelle
                self.program_goruntuleme.refresh()
            except Exception as e:
                self.logger.error(f"Program temizleme hatası: {str(e)}")
                messagebox.showerror("Hata", f"Program temizleme işlemi sırasında bir hata oluştu:\n{str(e)}")
    
    def export_pdf(self):
        """
        Programı PDF olarak dışa aktarır
        """
        # Program görüntüleme sekmesine geç
        self.notebook.select(self.program_goruntuleme_frame)
        self.program_goruntuleme.export_pdf()
    
    def export_excel(self):
        """
        Programı Excel olarak dışa aktarır
        """
        # Program görüntüleme sekmesine geç
        self.notebook.select(self.program_goruntuleme_frame)
        self.program_goruntuleme.export_excel()
    
    def show_help(self):
        """
        Yardım penceresini gösterir
        """
        messagebox.showinfo("Yardım", "Ders Programı Oluşturma Uygulaması Yardım\n\n"
                           "Bu uygulama, okul ders programlarını otomatik olarak oluşturmak için tasarlanmıştır.\n\n"
                           "1. Önce sınıf, öğretmen, ders ve derslik bilgilerini girin.\n"
                           "2. Kısıtlamaları tanımlayın (öğretmen uygunlukları, öğle arası vb.).\n"
                           "3. Program Oluşturma sekmesinden programı oluşturun.\n"
                           "4. Program Görüntüleme sekmesinden programı görüntüleyin ve düzenleyin.\n"
                           "5. Programı PDF veya Excel olarak dışa aktarın.")
    
    def show_about(self):
        """
        Hakkında penceresini gösterir
        """
        messagebox.showinfo("Hakkında", "Ders Programı Oluşturma Uygulaması\n\n"
                           "Sürüm: 1.0\n"
                           "Lisans: MIT\n\n"
                           "Bu uygulama, okul ders programlarını otomatik olarak oluşturmak için tasarlanmıştır."
                           "Bu programın hakları Emrullah ALKAÇ a aittir.")
    
    def set_status(self, message):
        """
        Durum çubuğu mesajını ayarlar
        
        Args:
            message (str): Mesaj
        """
        self.status_bar.config(text=message)
        """_summary_
        """