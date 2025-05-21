#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Derslik yönetimi arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class DerslikYonetimi:
    """
    Derslik yönetimi arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Derslik yönetimi arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Seçili derslik ID'si
        self.selected_id = None
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Derslikleri listele
        self.refresh_list()
        
        self.logger.info("Derslik yönetimi arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeveyi iki bölüme ayır
        self.paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sol panel - Derslik listesi
        self.list_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.list_frame, weight=1)
        
        # Derslik listesi
        self.create_list_widgets()
        
        # Sağ panel - Derslik detayları
        self.detail_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.detail_frame, weight=2)
        
        # Derslik detayları
        self.create_detail_widgets()
    
    def create_list_widgets(self):
        """
        Derslik listesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.list_frame, text="Derslik Listesi", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Arama çubuğu
        self.search_frame = ttk.Frame(self.list_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Ara:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_var.trace("w", lambda name, index, mode: self.filter_list())
        
        # Derslik listesi
        self.list_frame_inner = ttk.Frame(self.list_frame)
        self.list_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame_inner)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(self.list_frame_inner, columns=("ad", "tur"), 
                                show="headings", selectmode="browse", yscrollcommand=self.scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.tree.yview)
        
        # Sütun başlıkları
        self.tree.heading("ad", text="Derslik Adı")
        self.tree.heading("tur", text="Tür")
        
        # Sütun genişlikleri
        self.tree.column("ad", width=150)
        self.tree.column("tur", width=100)
        
        # Seçim olayı
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Butonlar
        self.button_frame = ttk.Frame(self.list_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(self.button_frame, text="Yeni Derslik", command=self.clear_form)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(self.button_frame, text="Sil", command=self.delete_derslik)
        self.delete_button.pack(side=tk.RIGHT, padx=5)
    
    def create_detail_widgets(self):
        """
        Derslik detayları bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.detail_frame, text="Derslik Detayları", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Form
        self.form_frame = ttk.Frame(self.detail_frame)
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Derslik Adı
        ttk.Label(self.form_frame, text="Derslik Adı:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ad_var = tk.StringVar()
        self.ad_entry = ttk.Entry(self.form_frame, textvariable=self.ad_var)
        self.ad_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Tür
        ttk.Label(self.form_frame, text="Tür:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tur_var = tk.StringVar(value="normal")
        
        self.tur_frame = ttk.Frame(self.form_frame)
        self.tur_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.normal_radio = ttk.Radiobutton(self.tur_frame, text="Normal", variable=self.tur_var, value="normal")
        self.normal_radio.pack(side=tk.LEFT, padx=5)
        
        self.ozel_radio = ttk.Radiobutton(self.tur_frame, text="Özel", variable=self.tur_var, value="ozel")
        self.ozel_radio.pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        self.form_button_frame = ttk.Frame(self.form_frame)
        self.form_button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.save_button = ttk.Button(self.form_button_frame, text="Kaydet", command=self.save_derslik)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(self.form_button_frame, text="İptal", command=self.clear_form)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Derslik Programı
        ttk.Label(self.form_frame, text="Derslik Programı:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Program listesi çerçevesi
        self.program_frame = ttk.Frame(self.form_frame)
        self.program_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Program listesi
        self.program_tree_frame = ttk.Frame(self.program_frame)
        self.program_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.program_scrollbar = ttk.Scrollbar(self.program_tree_frame)
        self.program_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.program_tree = ttk.Treeview(self.program_tree_frame, columns=("gun", "saat", "sinif", "ders", "ogretmen"), 
                                    show="headings", selectmode="browse", yscrollcommand=self.program_scrollbar.set)
        self.program_tree.pack(fill=tk.BOTH, expand=True)
        
        self.program_scrollbar.config(command=self.program_tree.yview)
        
        # Sütun başlıkları
        self.program_tree.heading("gun", text="Gün")
        self.program_tree.heading("saat", text="Saat")
        self.program_tree.heading("sinif", text="Sınıf")
        self.program_tree.heading("ders", text="Ders")
        self.program_tree.heading("ogretmen", text="Öğretmen")
        
        # Sütun genişlikleri
        self.program_tree.column("gun", width=80)
        self.program_tree.column("saat", width=50)
        self.program_tree.column("sinif", width=80)
        self.program_tree.column("ders", width=100)
        self.program_tree.column("ogretmen", width=150)
        
        # Form alanlarını genişlet
        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.rowconfigure(4, weight=1)
    
    def refresh_list(self):
        """
        Derslik listesini yeniler
        """
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Derslikleri getir
            derslikler = self.db.tum_derslikleri_getir()
            
            # Listeye ekle
            for derslik in derslikler:
                tur_text = "Özel" if derslik["tur"] == "ozel" else "Normal"
                self.tree.insert("", tk.END, values=(derslik["ad"], tur_text), 
                                tags=(derslik["id"],))
            
            self.logger.info(f"{len(derslikler)} derslik listelendi")
        except Exception as e:
            self.logger.error(f"Derslik listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Derslik listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def filter_list(self):
        """
        Derslik listesini filtreler
        """
        search_term = self.search_var.get().lower()
        
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Derslikleri getir
            derslikler = self.db.tum_derslikleri_getir()
            
            # Filtrele ve listeye ekle
            for derslik in derslikler:
                tur_text = "Özel" if derslik["tur"] == "ozel" else "Normal"
                if search_term in derslik["ad"].lower() or search_term in tur_text.lower():
                    self.tree.insert("", tk.END, values=(derslik["ad"], tur_text), 
                                    tags=(derslik["id"],))
        except Exception as e:
            self.logger.error(f"Derslik listesi filtreleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Derslik listesi filtrelenirken bir hata oluştu:\n{str(e)}")
    
    def on_select(self, event):
        """
        Derslik seçildiğinde çağrılır
        
        Args:
            event: Seçim olayı
        """
        # Seçili öğeyi al
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Seçili öğenin ID'sini al
        item = selected_items[0]
        self.selected_id = int(self.tree.item(item, "tags")[0])
        
        try:
            # Derslik bilgilerini getir
            derslik = self.db.derslik_getir(self.selected_id)
            if not derslik:
                return
            
            # Form alanlarını doldur
            self.ad_var.set(derslik["ad"])
            self.tur_var.set(derslik["tur"])
            
            # Dersliğin programını getir
            self.refresh_program_list()
            
            self.logger.info(f"Derslik seçildi: {derslik['ad']}")
        except Exception as e:
            self.logger.error(f"Derslik seçme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Derslik bilgileri alınırken bir hata oluştu:\n{str(e)}")
    
    def refresh_program_list(self):
        """
        Derslik programı listesini yeniler
        """
        # Listeyi temizle
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        
        if not self.selected_id:
            return
        
        try:
            # Dersliğin programını getir
            program = self.db.dersligin_programini_getir(self.selected_id)
            
            # Gün adları
            gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
            
            # Listeye ekle
            for ders in program:
                gun_adi = gun_adlari[ders["gun"]] if 0 <= ders["gun"] < len(gun_adlari) else f"Gün {ders['gun']}"
                sinif_adi = f"{ders['sinif_adi']} {ders['sinif_sube']}"
                self.program_tree.insert("", tk.END, values=(gun_adi, ders["saat"], sinif_adi, ders["ders_adi"], ders["ogretmen_adi"]), 
                                    tags=(ders["id"],))
            
            self.logger.info(f"{len(program)} program kaydı listelendi")
        except Exception as e:
            self.logger.error(f"Program listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Program listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def clear_form(self):
        """
        Form alanlarını temizler
        """
        self.selected_id = None
        self.ad_var.set("")
        self.tur_var.set("normal")
        
        # Program listesini temizle
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        
        # Odağı derslik adı alanına taşı
        self.ad_entry.focus()
    
    def save_derslik(self):
        """
        Derslik bilgilerini kaydeder
        """
        # Form verilerini al
        ad = self.ad_var.get().strip()
        tur = self.tur_var.get()
        
        # Veri doğrulama
        if not ad:
            messagebox.showerror("Hata", "Derslik adı boş olamaz.")
            return
        
        try:
            if self.selected_id:
                # Mevcut dersliği güncelle
                self.db.derslik_guncelle(self.selected_id, ad, tur)
                messagebox.showinfo("Bilgi", f"{ad} dersliği başarıyla güncellendi.")
                self.logger.info(f"Derslik güncellendi: {ad}")
            else:
                # Yeni derslik ekle
                self.selected_id = self.db.derslik_ekle(ad, tur)
                messagebox.showinfo("Bilgi", f"{ad} dersliği başarıyla eklendi.")
                self.logger.info(f"Derslik eklendi: {ad}")
            
            # Listeyi yenile
            self.refresh_list()
            
            # Yeni eklenen/güncellenen dersliği seç
            for item in self.tree.get_children():
                if int(self.tree.item(item, "tags")[0]) == self.selected_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            self.logger.error(f"Derslik kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Derslik kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def delete_derslik(self):
        """
        Seçili dersliği siler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen silinecek dersliği seçin.")
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili dersliği silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # Derslik bilgilerini al
            derslik = self.db.derslik_getir(self.selected_id)
            
            # Dersliği sil
            self.db.derslik_sil(self.selected_id)
            
            messagebox.showinfo("Bilgi", f"{derslik['ad']} dersliği başarıyla silindi.")
            self.logger.info(f"Derslik silindi: {derslik['ad']}")
            
            # Formu temizle
            self.clear_form()
            
            # Listeyi yenile
            self.refresh_list()
        except Exception as e:
            self.logger.error(f"Derslik silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Derslik silinirken bir hata oluştu:\n{str(e)}")
