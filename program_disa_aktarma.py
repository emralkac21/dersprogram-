#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dışa aktarma arayüzü
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime

from export.pdf_exporter import PDFExporter
from export.excel_exporter import ExcelExporter

class ProgramDisaAktarma:
    """
    Program dışa aktarma arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Program dışa aktarma arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # PDF ve Excel dışa aktarıcılar
        self.pdf_exporter = PDFExporter(self.db, self.config)
        self.excel_exporter = ExcelExporter(self.db, self.config)
        
        # Görünüm modu (sinif, ogretmen, derslik)
        self.view_mode = tk.StringVar(value="sinif")
        
        # Dışa aktarma formatı (pdf, excel)
        self.export_format = tk.StringVar(value="pdf")
        
        # Seçili filtre değerleri
        self.selected_sinif_id = None
        self.selected_ogretmen_id = None
        self.selected_derslik_id = None
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Filtreleri yükle
        self.load_filters()
        
        self.logger.info("Program dışa aktarma arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Başlık
        ttk.Label(self.main_frame, text="Program Dışa Aktarma", font=("TkDefaultFont", 16, "bold")).pack(pady=10)
        
        # Görünüm modu seçimi
        self.view_frame = ttk.LabelFrame(self.main_frame, text="Görünüm Modu")
        self.view_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.sinif_radio = ttk.Radiobutton(self.view_frame, text="Sınıf", variable=self.view_mode, value="sinif", command=self.change_view_mode)
        self.sinif_radio.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.ogretmen_radio = ttk.Radiobutton(self.view_frame, text="Öğretmen", variable=self.view_mode, value="ogretmen", command=self.change_view_mode)
        self.ogretmen_radio.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.derslik_radio = ttk.Radiobutton(self.view_frame, text="Derslik", variable=self.view_mode, value="derslik", command=self.change_view_mode)
        self.derslik_radio.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Filtre seçimi
        self.filter_frame = ttk.LabelFrame(self.main_frame, text="Filtre")
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.filter_frame, text="Seçim:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        
        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.filter_frame, textvariable=self.filter_var, state="readonly", width=40)
        self.filter_combobox.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.on_filter_change)
        
        # Tümünü seç
        self.select_all_var = tk.BooleanVar(value=False)
        self.select_all_check = ttk.Checkbutton(self.filter_frame, text="Tümünü Seç", variable=self.select_all_var, command=self.on_select_all)
        self.select_all_check.grid(row=0, column=2, padx=20, pady=10)
        
        # Format seçimi
        self.format_frame = ttk.LabelFrame(self.main_frame, text="Dışa Aktarma Formatı")
        self.format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.pdf_radio = ttk.Radiobutton(self.format_frame, text="PDF", variable=self.export_format, value="pdf")
        self.pdf_radio.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.excel_radio = ttk.Radiobutton(self.format_frame, text="Excel", variable=self.export_format, value="excel")
        self.excel_radio.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Dışa aktarma seçenekleri
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Dışa Aktarma Seçenekleri")
        self.options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Çıktı dizini
        ttk.Label(self.options_frame, text="Çıktı Dizini:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.output_dir_var = tk.StringVar(value=os.path.expanduser("~"))
        self.output_dir_entry = ttk.Entry(self.options_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.browse_button = ttk.Button(self.options_frame, text="Gözat", command=self.browse_output_dir)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Butonlar
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=20)
        
        self.export_button = ttk.Button(self.button_frame, text="Dışa Aktar", command=self.export_program)
        self.export_button.pack(side=tk.RIGHT, padx=5)
    
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
    
    def change_view_mode(self):
        """
        Görünüm modunu değiştirir
        """
        # Filtreleri yükle
        self.load_filters()
        
        # Tümünü seç seçeneğini sıfırla
        self.select_all_var.set(False)
        
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
        
        # Tümünü seç seçeneğini sıfırla
        self.select_all_var.set(False)
        
        self.logger.info(f"Filtre değiştirildi: {selected_value}")
    
    def on_select_all(self):
        """
        Tümünü seç seçeneği değiştiğinde çağrılır
        """
        if self.select_all_var.get():
            # Tümünü seç seçiliyse, filtre combobox'ı devre dışı bırak
            self.filter_combobox.config(state="disabled")
        else:
            # Tümünü seç seçili değilse, filtre combobox'ı etkinleştir
            self.filter_combobox.config(state="readonly")
        
        self.logger.info(f"Tümünü seç değiştirildi: {self.select_all_var.get()}")
    
    def browse_output_dir(self):
        """
        Çıktı dizini seçme iletişim kutusunu açar
        """
        output_dir = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if output_dir:
            self.output_dir_var.set(output_dir)
            self.logger.info(f"Çıktı dizini seçildi: {output_dir}")
    
    def export_program(self):
        """
        Programı dışa aktarır
        """
        # Çıktı dizinini kontrol et
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Hata", "Lütfen çıktı dizini seçin.")
            return
        
        if not os.path.isdir(output_dir):
            messagebox.showerror("Hata", "Seçilen çıktı dizini geçerli değil.")
            return
        
        try:
            # Dışa aktarma formatı
            export_format = self.export_format.get()
            
            # Görünüm modu
            view_mode = self.view_mode.get()
            
            # Tümünü seç
            select_all = self.select_all_var.get()
            
            # Dışa aktarma işlemi
            if select_all:
                # Tümünü dışa aktar
                if view_mode == "sinif":
                    if export_format == "pdf":
                        self.pdf_exporter.export_tum_sinif_programlari(output_dir)
                    else:
                        self.excel_exporter.export_tum_sinif_programlari(output_dir)
                    
                    messagebox.showinfo("Bilgi", "Tüm sınıf programları başarıyla dışa aktarıldı.")
                
                elif view_mode == "ogretmen":
                    if export_format == "pdf":
                        self.pdf_exporter.export_tum_ogretmen_programlari(output_dir)
                    else:
                        self.excel_exporter.export_tum_ogretmen_programlari(output_dir)
                    
                    messagebox.showinfo("Bilgi", "Tüm öğretmen programları başarıyla dışa aktarıldı.")
                
                elif view_mode == "derslik":
                    if export_format == "pdf":
                        self.pdf_exporter.export_tum_derslik_programlari(output_dir)
                    else:
                        self.excel_exporter.export_tum_derslik_programlari(output_dir)
                    
                    messagebox.showinfo("Bilgi", "Tüm derslik programları başarıyla dışa aktarıldı.")
            
            else:
                # Seçili olanı dışa aktar
                if view_mode == "sinif" and self.selected_sinif_id:
                    # Sınıf adını al
                    self.db.execute("SELECT ad, sube FROM siniflar WHERE id = ?", (self.selected_sinif_id,))
                    sinif = self.db.fetchone()
                    
                    if sinif:
                        sinif_adi = f"{sinif['ad']}_{sinif['sube']}"
                        
                        if export_format == "pdf":
                            output_path = os.path.join(output_dir, f"sinif_programi_{sinif_adi}.pdf")
                            self.pdf_exporter.export_sinif_programi(self.selected_sinif_id, output_path)
                        else:
                            output_path = os.path.join(output_dir, f"sinif_programi_{sinif_adi}.xlsx")
                            self.excel_exporter.export_sinif_programi(self.selected_sinif_id, output_path)
                        
                        messagebox.showinfo("Bilgi", f"{sinif['ad']} {sinif['sube']} sınıfının programı başarıyla dışa aktarıldı.")
                    else:
                        messagebox.showerror("Hata", "Seçili sınıf bulunamadı.")
                
                elif view_mode == "ogretmen" and self.selected_ogretmen_id:
                    # Öğretmen adını al
                    self.db.execute("SELECT ad_soyad FROM ogretmenler WHERE id = ?", (self.selected_ogretmen_id,))
                    ogretmen = self.db.fetchone()
                    
                    if ogretmen:
                        ogretmen_adi = ogretmen['ad_soyad'].replace(' ', '_')
                        
                        if export_format == "pdf":
                            output_path = os.path.join(output_dir, f"ogretmen_programi_{ogretmen_adi}.pdf")
                            self.pdf_exporter.export_ogretmen_programi(self.selected_ogretmen_id, output_path)
                        else:
                            output_path = os.path.join(output_dir, f"ogretmen_programi_{ogretmen_adi}.xlsx")
                            self.excel_exporter.export_ogretmen_programi(self.selected_ogretmen_id, output_path)
                        
                        messagebox.showinfo("Bilgi", f"{ogretmen['ad_soyad']} öğretmeninin programı başarıyla dışa aktarıldı.")
                    else:
                        messagebox.showerror("Hata", "Seçili öğretmen bulunamadı.")
                
                elif view_mode == "derslik" and self.selected_derslik_id:
                    # Derslik adını al
                    self.db.execute("SELECT ad FROM derslikler WHERE id = ?", (self.selected_derslik_id,))
                    derslik = self.db.fetchone()
                    
                    if derslik:
                        derslik_adi = derslik['ad'].replace(' ', '_')
                        
                        if export_format == "pdf":
                            output_path = os.path.join(output_dir, f"derslik_programi_{derslik_adi}.pdf")
                            self.pdf_exporter.export_derslik_programi(self.selected_derslik_id, output_path)
                        else:
                            output_path = os.path.join(output_dir, f"derslik_programi_{derslik_adi}.xlsx")
                            self.excel_exporter.export_derslik_programi(self.selected_derslik_id, output_path)
                        
                        messagebox.showinfo("Bilgi", f"{derslik['ad']} dersliğinin programı başarıyla dışa aktarıldı.")
                    else:
                        messagebox.showerror("Hata", "Seçili derslik bulunamadı.")
                
                else:
                    messagebox.showerror("Hata", "Lütfen bir seçim yapın.")
            
            self.logger.info(f"Program dışa aktarıldı: {view_mode}, {export_format}, {select_all}")
        except Exception as e:
            self.logger.error(f"Program dışa aktarılırken hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Program dışa aktarılırken bir hata oluştu:\n{str(e)}")
