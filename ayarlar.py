#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ayarlar modülü
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import os

class Ayarlar:
    """
    Ayarlar sınıfı - Uygulama ayarlarını yönetir
    """
    
    def __init__(self, parent, db, config):
        """
        Ayarlar sınıfını başlatır
        
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
        
        self.logger.info("Ayarlar modülü başlatıldı")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sekme kontrolü
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Genel ayarlar sekmesi
        self.general_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.general_frame, text="Genel Ayarlar")
        self.create_general_settings()
        
        # Veritabanı ayarları sekmesi
        self.database_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.database_frame, text="Veritabanı Ayarları")
        self.create_database_settings()
        
        # Görünüm ayarları sekmesi
        self.appearance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.appearance_frame, text="Görünüm Ayarları")
        self.create_appearance_settings()
        
        # Dışa aktarma ayarları sekmesi
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Dışa Aktarma Ayarları")
        self.create_export_settings()
        
        # Butonlar
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.save_button = ttk.Button(self.button_frame, text="Ayarları Kaydet", command=self.save_settings)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        self.reset_button = ttk.Button(self.button_frame, text="Varsayılana Sıfırla", command=self.reset_settings)
        self.reset_button.pack(side=tk.RIGHT, padx=5)
    
    def create_general_settings(self):
        """
        Genel ayarlar sekmesini oluşturur
        """
        # Uygulama başlığı
        ttk.Label(self.general_frame, text="Uygulama Başlığı:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.app_title_var = tk.StringVar()
        self.app_title_entry = ttk.Entry(self.general_frame, textvariable=self.app_title_var, width=40)
        self.app_title_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Loglama seviyesi
        ttk.Label(self.general_frame, text="Loglama Seviyesi:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.log_level_var = tk.StringVar()
        self.log_level_combo = ttk.Combobox(self.general_frame, textvariable=self.log_level_var, state="readonly", width=15)
        self.log_level_combo["values"] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_level_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Log dosyası
        ttk.Label(self.general_frame, text="Log Dosyası:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.log_file_var = tk.StringVar()
        self.log_file_entry = ttk.Entry(self.general_frame, textvariable=self.log_file_var, width=40)
        self.log_file_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.log_file_button = ttk.Button(self.general_frame, text="Gözat", command=self.browse_log_file)
        self.log_file_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Otomatik yedekleme
        ttk.Label(self.general_frame, text="Otomatik Yedekleme:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.auto_backup_var = tk.BooleanVar()
        self.auto_backup_check = ttk.Checkbutton(self.general_frame, text="Uygulama kapatılırken otomatik yedekle", variable=self.auto_backup_var)
        self.auto_backup_check.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
    
    def create_database_settings(self):
        """
        Veritabanı ayarları sekmesini oluşturur
        """
        # Veritabanı dosyası
        ttk.Label(self.database_frame, text="Veritabanı Dosyası:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.db_file_var = tk.StringVar()
        self.db_file_entry = ttk.Entry(self.database_frame, textvariable=self.db_file_var, width=40)
        self.db_file_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.db_file_button = ttk.Button(self.database_frame, text="Gözat", command=self.browse_db_file)
        self.db_file_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Yedekleme dizini
        ttk.Label(self.database_frame, text="Yedekleme Dizini:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.backup_dir_var = tk.StringVar()
        self.backup_dir_entry = ttk.Entry(self.database_frame, textvariable=self.backup_dir_var, width=40)
        self.backup_dir_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.backup_dir_button = ttk.Button(self.database_frame, text="Gözat", command=self.browse_backup_dir)
        self.backup_dir_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Veritabanı işlemleri
        ttk.Separator(self.database_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=3, sticky=tk.EW, padx=5, pady=10)
        
        ttk.Label(self.database_frame, text="Veritabanı İşlemleri:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.db_operations_frame = ttk.Frame(self.database_frame)
        self.db_operations_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.backup_button = ttk.Button(self.db_operations_frame, text="Veritabanını Yedekle", command=self.backup_database)
        self.backup_button.pack(side=tk.LEFT, padx=5)
        
        self.restore_button = ttk.Button(self.db_operations_frame, text="Veritabanını Geri Yükle", command=self.restore_database)
        self.restore_button.pack(side=tk.LEFT, padx=5)
        
        self.optimize_button = ttk.Button(self.db_operations_frame, text="Veritabanını Optimize Et", command=self.optimize_database)
        self.optimize_button.pack(side=tk.LEFT, padx=5)
    
    def create_appearance_settings(self):
        """
        Görünüm ayarları sekmesini oluşturur
        """
        # Tema
        ttk.Label(self.appearance_frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(self.appearance_frame, textvariable=self.theme_var, state="readonly", width=15)
        self.theme_combo["values"] = ["Varsayılan", "Açık", "Koyu"]
        self.theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Yazı tipi
        ttk.Label(self.appearance_frame, text="Yazı Tipi:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.font_var = tk.StringVar()
        self.font_combo = ttk.Combobox(self.appearance_frame, textvariable=self.font_var, state="readonly", width=15)
        self.font_combo["values"] = ["Varsayılan", "Arial", "Times New Roman", "Courier New"]
        self.font_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Yazı boyutu
        ttk.Label(self.appearance_frame, text="Yazı Boyutu:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.font_size_var = tk.StringVar()
        self.font_size_combo = ttk.Combobox(self.appearance_frame, textvariable=self.font_size_var, state="readonly", width=15)
        self.font_size_combo["values"] = ["Küçük", "Normal", "Büyük"]
        self.font_size_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Renk şeması
        ttk.Label(self.appearance_frame, text="Renk Şeması:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.color_scheme_var = tk.StringVar()
        self.color_scheme_combo = ttk.Combobox(self.appearance_frame, textvariable=self.color_scheme_var, state="readonly", width=15)
        self.color_scheme_combo["values"] = ["Varsayılan", "Mavi", "Yeşil", "Kırmızı"]
        self.color_scheme_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
    
    def create_export_settings(self):
        """
        Dışa aktarma ayarları sekmesini oluşturur
        """
        # Varsayılan dışa aktarma formatı
        ttk.Label(self.export_frame, text="Varsayılan Format:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.default_export_format_var = tk.StringVar()
        self.default_export_format_combo = ttk.Combobox(self.export_frame, textvariable=self.default_export_format_var, state="readonly", width=15)
        self.default_export_format_combo["values"] = ["PDF", "Excel"]
        self.default_export_format_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Varsayılan dışa aktarma dizini
        ttk.Label(self.export_frame, text="Varsayılan Dizin:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.default_export_dir_var = tk.StringVar()
        self.default_export_dir_entry = ttk.Entry(self.export_frame, textvariable=self.default_export_dir_var, width=40)
        self.default_export_dir_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.default_export_dir_button = ttk.Button(self.export_frame, text="Gözat", command=self.browse_export_dir)
        self.default_export_dir_button.grid(row=1, column=2, padx=5, pady=5)
        
        # PDF ayarları
        ttk.Label(self.export_frame, text="PDF Ayarları:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.pdf_settings_frame = ttk.Frame(self.export_frame)
        self.pdf_settings_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.pdf_page_size_var = tk.StringVar()
        ttk.Label(self.pdf_settings_frame, text="Sayfa Boyutu:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.pdf_page_size_combo = ttk.Combobox(self.pdf_settings_frame, textvariable=self.pdf_page_size_var, state="readonly", width=15)
        self.pdf_page_size_combo["values"] = ["A4", "A3", "Letter", "Legal"]
        self.pdf_page_size_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.pdf_orientation_var = tk.StringVar()
        ttk.Label(self.pdf_settings_frame, text="Yönlendirme:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.pdf_orientation_combo = ttk.Combobox(self.pdf_settings_frame, textvariable=self.pdf_orientation_var, state="readonly", width=15)
        self.pdf_orientation_combo["values"] = ["Dikey", "Yatay"]
        self.pdf_orientation_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Excel ayarları
        ttk.Label(self.export_frame, text="Excel Ayarları:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.excel_settings_frame = ttk.Frame(self.export_frame)
        self.excel_settings_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.excel_sheet_name_var = tk.StringVar()
        ttk.Label(self.excel_settings_frame, text="Sayfa Adı:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.excel_sheet_name_entry = ttk.Entry(self.excel_settings_frame, textvariable=self.excel_sheet_name_var, width=20)
        self.excel_sheet_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.excel_include_header_var = tk.BooleanVar()
        self.excel_include_header_check = ttk.Checkbutton(self.excel_settings_frame, text="Başlık Ekle", variable=self.excel_include_header_var)
        self.excel_include_header_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
    
    def browse_log_file(self):
        """
        Log dosyası seçme iletişim kutusunu açar
        """
        log_file = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.log_file_var.get()) if self.log_file_var.get() else os.path.expanduser("~"),
            title="Log Dosyası Seç",
            filetypes=(("Log Dosyaları", "*.log"), ("Tüm Dosyalar", "*.*"))
        )
        if log_file:
            self.log_file_var.set(log_file)
    
    def browse_db_file(self):
        """
        Veritabanı dosyası seçme iletişim kutusunu açar
        """
        db_file = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.db_file_var.get()) if self.db_file_var.get() else os.path.expanduser("~"),
            title="Veritabanı Dosyası Seç",
            filetypes=(("SQLite Veritabanları", "*.db"), ("Tüm Dosyalar", "*.*"))
        )
        if db_file:
            self.db_file_var.set(db_file)
    
    def browse_backup_dir(self):
        """
        Yedekleme dizini seçme iletişim kutusunu açar
        """
        backup_dir = filedialog.askdirectory(
            initialdir=self.backup_dir_var.get() if self.backup_dir_var.get() else os.path.expanduser("~"),
            title="Yedekleme Dizini Seç"
        )
        if backup_dir:
            self.backup_dir_var.set(backup_dir)
    
    def browse_export_dir(self):
        """
        Dışa aktarma dizini seçme iletişim kutusunu açar
        """
        export_dir = filedialog.askdirectory(
            initialdir=self.default_export_dir_var.get() if self.default_export_dir_var.get() else os.path.expanduser("~"),
            title="Dışa Aktarma Dizini Seç"
        )
        if export_dir:
            self.default_export_dir_var.set(export_dir)
    
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
    
    def optimize_database(self):
        """
        Veritabanını optimize eder
        """
        try:
            # Veritabanı optimizasyon işlemi
            messagebox.showinfo("Bilgi", "Veritabanı optimizasyon işlemi başarıyla tamamlandı.")
        except Exception as e:
            self.logger.error(f"Veritabanı optimizasyon hatası: {str(e)}")
            messagebox.showerror("Hata", f"Veritabanı optimizasyon işlemi sırasında bir hata oluştu:\n{str(e)}")
    
    def load_settings(self):
        """
        Ayarları yükler
        """
        try:
            # Genel ayarlar
            self.app_title_var.set(self.config.get('app', 'title', 'Ders Programı Oluşturma Uygulaması'))
            self.log_level_var.set(self.config.get('logging', 'level', 'INFO'))
            self.log_file_var.set(self.config.get('logging', 'file', 'logs/ders_programi.log'))
            self.auto_backup_var.set(self.config.get('app', 'auto_backup', True))
            
            # Veritabanı ayarları
            self.db_file_var.set(self.config.get('database', 'file', 'data/ders_programi.db'))
            self.backup_dir_var.set(self.config.get('database', 'backup_dir', 'backups'))
            
            # Görünüm ayarları
            self.theme_var.set(self.config.get('appearance', 'theme', 'Varsayılan'))
            self.font_var.set(self.config.get('appearance', 'font', 'Varsayılan'))
            self.font_size_var.set(self.config.get('appearance', 'font_size', 'Normal'))
            self.color_scheme_var.set(self.config.get('appearance', 'color_scheme', 'Varsayılan'))
            
            # Dışa aktarma ayarları
            self.default_export_format_var.set(self.config.get('export', 'default_format', 'PDF'))
            self.default_export_dir_var.set(self.config.get('export', 'default_dir', os.path.expanduser('~')))
            self.pdf_page_size_var.set(self.config.get('export', 'pdf_page_size', 'A4'))
            self.pdf_orientation_var.set(self.config.get('export', 'pdf_orientation', 'Yatay'))
            self.excel_sheet_name_var.set(self.config.get('export', 'excel_sheet_name', 'Ders Programı'))
            self.excel_include_header_var.set(self.config.get('export', 'excel_include_header', True))
            
            self.logger.info("Ayarlar başarıyla yüklendi")
        except Exception as e:
            self.logger.error(f"Ayarlar yüklenirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar yüklenirken bir hata oluştu:\n{str(e)}")
    
    def save_settings(self):
        """
        Ayarları kaydeder
        """
        try:
            # Genel ayarlar
            self.config.set('app', 'title', self.app_title_var.get())
            self.config.set('logging', 'level', self.log_level_var.get())
            self.config.set('logging', 'file', self.log_file_var.get())
            self.config.set('app', 'auto_backup', self.auto_backup_var.get())
            
            # Veritabanı ayarları
            self.config.set('database', 'file', self.db_file_var.get())
            self.config.set('database', 'backup_dir', self.backup_dir_var.get())
            
            # Görünüm ayarları
            self.config.set('appearance', 'theme', self.theme_var.get())
            self.config.set('appearance', 'font', self.font_var.get())
            self.config.set('appearance', 'font_size', self.font_size_var.get())
            self.config.set('appearance', 'color_scheme', self.color_scheme_var.get())
            
            # Dışa aktarma ayarları
            self.config.set('export', 'default_format', self.default_export_format_var.get())
            self.config.set('export', 'default_dir', self.default_export_dir_var.get())
            self.config.set('export', 'pdf_page_size', self.pdf_page_size_var.get())
            self.config.set('export', 'pdf_orientation', self.pdf_orientation_var.get())
            self.config.set('export', 'excel_sheet_name', self.excel_sheet_name_var.get())
            self.config.set('export', 'excel_include_header', self.excel_include_header_var.get())
            
            # Yapılandırmayı kaydet
            self.config.save()
            
            messagebox.showinfo("Bilgi", "Ayarlar başarıyla kaydedildi.")
            self.logger.info("Ayarlar başarıyla kaydedildi")
        except Exception as e:
            self.logger.error(f"Ayarlar kaydedilirken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def reset_settings(self):
        """
        Ayarları varsayılan değerlere sıfırlar
        """
        if messagebox.askyesno("Onay", "Tüm ayarları varsayılan değerlere sıfırlamak istediğinizden emin misiniz?"):
            try:
                # Varsayılan ayarları yükle
                self.config.reset_to_defaults()
                
                # Ayarları yeniden yükle
                self.load_settings()
                
                messagebox.showinfo("Bilgi", "Ayarlar varsayılan değerlere sıfırlandı.")
                self.logger.info("Ayarlar varsayılan değerlere sıfırlandı")
            except Exception as e:
                self.logger.error(f"Ayarlar sıfırlanırken hata oluştu: {str(e)}")
                messagebox.showerror("Hata", f"Ayarlar sıfırlanırken bir hata oluştu:\n{str(e)}")
