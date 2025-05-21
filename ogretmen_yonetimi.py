#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Öğretmen yönetimi arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class OgretmenYonetimi:
    """
    Öğretmen yönetimi arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Öğretmen yönetimi arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Seçili öğretmen ID'si
        self.selected_id = None
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Öğretmenleri listele
        self.refresh_list()
        
        self.logger.info("Öğretmen yönetimi arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeveyi iki bölüme ayır
        self.paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sol panel - Öğretmen listesi
        self.list_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.list_frame, weight=1)
        
        # Öğretmen listesi
        self.create_list_widgets()
        
        # Sağ panel - Öğretmen detayları
        self.detail_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.detail_frame, weight=2)
        
        # Öğretmen detayları
        self.create_detail_widgets()
    
    def create_list_widgets(self):
        """
        Öğretmen listesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.list_frame, text="Öğretmen Listesi", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Arama çubuğu
        self.search_frame = ttk.Frame(self.list_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Ara:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_var.trace("w", lambda name, index, mode: self.filter_list())
        
        # Öğretmen listesi
        self.list_frame_inner = ttk.Frame(self.list_frame)
        self.list_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame_inner)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(self.list_frame_inner, columns=("ad_soyad", "brans", "haftalik_ders_saati"), 
                                show="headings", selectmode="browse", yscrollcommand=self.scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.tree.yview)
        
        # Sütun başlıkları
        self.tree.heading("ad_soyad", text="Ad Soyad")
        self.tree.heading("brans", text="Branş")
        self.tree.heading("haftalik_ders_saati", text="Haftalık Ders Saati")
        
        # Sütun genişlikleri
        self.tree.column("ad_soyad", width=150)
        self.tree.column("brans", width=100)
        self.tree.column("haftalik_ders_saati", width=100)
        
        # Seçim olayı
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Butonlar
        self.button_frame = ttk.Frame(self.list_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(self.button_frame, text="Yeni Öğretmen", command=self.clear_form)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(self.button_frame, text="Sil", command=self.delete_ogretmen)
        self.delete_button.pack(side=tk.RIGHT, padx=5)
    
    def create_detail_widgets(self):
        """
        Öğretmen detayları bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.detail_frame, text="Öğretmen Detayları", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Form
        self.form_frame = ttk.Frame(self.detail_frame)
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ad Soyad
        ttk.Label(self.form_frame, text="Ad Soyad:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ad_soyad_var = tk.StringVar()
        self.ad_soyad_entry = ttk.Entry(self.form_frame, textvariable=self.ad_soyad_var)
        self.ad_soyad_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Branş
        ttk.Label(self.form_frame, text="Branş:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.brans_var = tk.StringVar()
        self.brans_entry = ttk.Entry(self.form_frame, textvariable=self.brans_var)
        self.brans_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Haftalık Ders Saati
        ttk.Label(self.form_frame, text="Haftalık Ders Saati:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.haftalik_ders_saati_var = tk.IntVar()
        self.haftalik_ders_saati_spinbox = ttk.Spinbox(self.form_frame, from_=0, to=40, textvariable=self.haftalik_ders_saati_var)
        self.haftalik_ders_saati_spinbox.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Butonlar
        self.form_button_frame = ttk.Frame(self.form_frame)
        self.form_button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.save_button = ttk.Button(self.form_button_frame, text="Kaydet", command=self.save_ogretmen)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(self.form_button_frame, text="İptal", command=self.clear_form)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Uygun Olmayan Zamanlar
        ttk.Label(self.form_frame, text="Uygun Olmayan Zamanlar:", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Uygun olmayan zamanlar listesi çerçevesi
        self.zaman_frame = ttk.Frame(self.form_frame)
        self.zaman_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Uygun olmayan zamanlar listesi
        self.zaman_tree_frame = ttk.Frame(self.zaman_frame)
        self.zaman_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.zaman_scrollbar = ttk.Scrollbar(self.zaman_tree_frame)
        self.zaman_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.zaman_tree = ttk.Treeview(self.zaman_tree_frame, columns=("gun", "saat_baslangic", "saat_bitis"), 
                                    show="headings", selectmode="browse", yscrollcommand=self.zaman_scrollbar.set)
        self.zaman_tree.pack(fill=tk.BOTH, expand=True)
        
        self.zaman_scrollbar.config(command=self.zaman_tree.yview)
        
        # Sütun başlıkları
        self.zaman_tree.heading("gun", text="Gün")
        self.zaman_tree.heading("saat_baslangic", text="Başlangıç Saati")
        self.zaman_tree.heading("saat_bitis", text="Bitiş Saati")
        
        # Sütun genişlikleri
        self.zaman_tree.column("gun", width=100)
        self.zaman_tree.column("saat_baslangic", width=100)
        self.zaman_tree.column("saat_bitis", width=100)
        
        # Uygun olmayan zaman butonları
        self.zaman_button_frame = ttk.Frame(self.zaman_frame)
        self.zaman_button_frame.pack(fill=tk.X, pady=5)
        
        self.add_zaman_button = ttk.Button(self.zaman_button_frame, text="Zaman Ekle", command=self.add_zaman)
        self.add_zaman_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_zaman_button = ttk.Button(self.zaman_button_frame, text="Düzenle", command=self.edit_zaman)
        self.edit_zaman_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_zaman_button = ttk.Button(self.zaman_button_frame, text="Sil", command=self.delete_zaman)
        self.delete_zaman_button.pack(side=tk.LEFT, padx=5)
        
        # Öğretmenin Dersleri
        ttk.Label(self.form_frame, text="Öğretmenin Dersleri:", font=("TkDefaultFont", 10, "bold")).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Ders listesi çerçevesi
        self.ders_frame = ttk.Frame(self.form_frame)
        self.ders_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Ders listesi
        self.ders_tree_frame = ttk.Frame(self.ders_frame)
        self.ders_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.ders_scrollbar = ttk.Scrollbar(self.ders_tree_frame)
        self.ders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.ders_tree = ttk.Treeview(self.ders_tree_frame, columns=("ders", "sinif", "saat"), 
                                    show="headings", selectmode="browse", yscrollcommand=self.ders_scrollbar.set)
        self.ders_tree.pack(fill=tk.BOTH, expand=True)
        
        self.ders_scrollbar.config(command=self.ders_tree.yview)
        
        # Sütun başlıkları
        self.ders_tree.heading("ders", text="Ders")
        self.ders_tree.heading("sinif", text="Sınıf")
        self.ders_tree.heading("saat", text="Haftalık Saat")
        
        # Sütun genişlikleri
        self.ders_tree.column("ders", width=150)
        self.ders_tree.column("sinif", width=100)
        self.ders_tree.column("saat", width=100)
        
        # Form alanlarını genişlet
        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.rowconfigure(5, weight=1)
        self.form_frame.rowconfigure(7, weight=1)
    
    def refresh_list(self):
        """
        Öğretmen listesini yeniler
        """
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Öğretmenleri getir
            ogretmenler = self.db.tum_ogretmenleri_getir()
            
            # Listeye ekle
            for ogretmen in ogretmenler:
                self.tree.insert("", tk.END, values=(ogretmen["ad_soyad"], ogretmen["brans"], ogretmen["haftalik_ders_saati"]), 
                                tags=(ogretmen["id"],))
            
            self.logger.info(f"{len(ogretmenler)} öğretmen listelendi")
        except Exception as e:
            self.logger.error(f"Öğretmen listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def filter_list(self):
        """
        Öğretmen listesini filtreler
        """
        search_term = self.search_var.get().lower()
        
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Öğretmenleri getir
            ogretmenler = self.db.tum_ogretmenleri_getir()
            
            # Filtrele ve listeye ekle
            for ogretmen in ogretmenler:
                if (search_term in ogretmen["ad_soyad"].lower() or 
                    search_term in ogretmen["brans"].lower()):
                    self.tree.insert("", tk.END, values=(ogretmen["ad_soyad"], ogretmen["brans"], ogretmen["haftalik_ders_saati"]), 
                                    tags=(ogretmen["id"],))
        except Exception as e:
            self.logger.error(f"Öğretmen listesi filtreleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen listesi filtrelenirken bir hata oluştu:\n{str(e)}")
    
    def on_select(self, event):
        """
        Öğretmen seçildiğinde çağrılır
        
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
            # Öğretmen bilgilerini getir
            ogretmen = self.db.ogretmen_getir(self.selected_id)
            if not ogretmen:
                return
            
            # Form alanlarını doldur
            self.ad_soyad_var.set(ogretmen["ad_soyad"])
            self.brans_var.set(ogretmen["brans"])
            self.haftalik_ders_saati_var.set(ogretmen["haftalik_ders_saati"])
            
            # Öğretmenin uygun olmayan zamanlarını getir
            self.refresh_zaman_list()
            
            # Öğretmenin derslerini getir
            self.refresh_ders_list()
            
            self.logger.info(f"Öğretmen seçildi: {ogretmen['ad_soyad']}")
        except Exception as e:
            self.logger.error(f"Öğretmen seçme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen bilgileri alınırken bir hata oluştu:\n{str(e)}")
    
    def refresh_zaman_list(self):
        """
        Öğretmenin uygun olmayan zamanlar listesini yeniler
        """
        # Listeyi temizle
        for item in self.zaman_tree.get_children():
            self.zaman_tree.delete(item)
        
        if not self.selected_id:
            return
        
        try:
            # Öğretmenin uygun olmayan zamanlarını getir
            zamanlar = self.db.ogretmenin_uygun_olmayan_zamanlarini_getir(self.selected_id)
            
            # Gün adları
            gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
            
            # Listeye ekle
            for zaman in zamanlar:
                gun_adi = gun_adlari[zaman["gun"]] if 0 <= zaman["gun"] < len(gun_adlari) else f"Gün {zaman['gun']}"
                self.zaman_tree.insert("", tk.END, values=(gun_adi, zaman["saat_baslangic"], zaman["saat_bitis"]), 
                                    tags=(zaman["id"],))
            
            self.logger.info(f"{len(zamanlar)} uygun olmayan zaman listelendi")
        except Exception as e:
            self.logger.error(f"Uygun olmayan zaman listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Uygun olmayan zaman listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def refresh_ders_list(self):
        """
        Öğretmenin ders listesini yeniler
        """
        # Listeyi temizle
        for item in self.ders_tree.get_children():
            self.ders_tree.delete(item)
        
        if not self.selected_id:
            return
        
        try:
            # Öğretmenin derslerini getir
            dersler = self.db.ogretmenin_derslerini_getir(self.selected_id)
            
            # Listeye ekle
            for ders in dersler:
                sinif_adi = f"{ders['sinif_adi']} {ders['sinif_sube']}"
                self.ders_tree.insert("", tk.END, values=(ders["ders_adi"], sinif_adi, ders["haftalik_saat"]), 
                                    tags=(ders["id"],))
            
            self.logger.info(f"{len(dersler)} ders listelendi")
        except Exception as e:
            self.logger.error(f"Ders listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def clear_form(self):
        """
        Form alanlarını temizler
        """
        self.selected_id = None
        self.ad_soyad_var.set("")
        self.brans_var.set("")
        self.haftalik_ders_saati_var.set(20)  # Varsayılan değer
        
        # Uygun olmayan zamanlar listesini temizle
        for item in self.zaman_tree.get_children():
            self.zaman_tree.delete(item)
        
        # Ders listesini temizle
        for item in self.ders_tree.get_children():
            self.ders_tree.delete(item)
        
        # Odağı ad soyad alanına taşı
        self.ad_soyad_entry.focus()
    
    def save_ogretmen(self):
        """
        Öğretmen bilgilerini kaydeder
        """
        # Form verilerini al
        ad_soyad = self.ad_soyad_var.get().strip()
        brans = self.brans_var.get().strip()
        
        try:
            haftalik_ders_saati = int(self.haftalik_ders_saati_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Haftalık ders saati sayısal bir değer olmalıdır.")
            return
        
        # Veri doğrulama
        if not ad_soyad:
            messagebox.showerror("Hata", "Ad Soyad boş olamaz.")
            return
        
        if not brans:
            messagebox.showerror("Hata", "Branş boş olamaz.")
            return
        
        if haftalik_ders_saati < 0:
            messagebox.showerror("Hata", "Haftalık ders saati negatif olamaz.")
            return
        
        try:
            if self.selected_id:
                # Mevcut öğretmeni güncelle
                self.db.ogretmen_guncelle(self.selected_id, ad_soyad, brans, haftalik_ders_saati)
                messagebox.showinfo("Bilgi", f"{ad_soyad} öğretmeni başarıyla güncellendi.")
                self.logger.info(f"Öğretmen güncellendi: {ad_soyad}")
            else:
                # Yeni öğretmen ekle
                self.selected_id = self.db.ogretmen_ekle(ad_soyad, brans, haftalik_ders_saati)
                messagebox.showinfo("Bilgi", f"{ad_soyad} öğretmeni başarıyla eklendi.")
                self.logger.info(f"Öğretmen eklendi: {ad_soyad}")
            
            # Listeyi yenile
            self.refresh_list()
            
            # Yeni eklenen/güncellenen öğretmeni seç
            for item in self.tree.get_children():
                if int(self.tree.item(item, "tags")[0]) == self.selected_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            self.logger.error(f"Öğretmen kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def delete_ogretmen(self):
        """
        Seçili öğretmeni siler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen silinecek öğretmeni seçin.")
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili öğretmeni silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # Öğretmen bilgilerini al
            ogretmen = self.db.ogretmen_getir(self.selected_id)
            
            # Öğretmeni sil
            self.db.ogretmen_sil(self.selected_id)
            
            messagebox.showinfo("Bilgi", f"{ogretmen['ad_soyad']} öğretmeni başarıyla silindi.")
            self.logger.info(f"Öğretmen silindi: {ogretmen['ad_soyad']}")
            
            # Formu temizle
            self.clear_form()
            
            # Listeyi yenile
            self.refresh_list()
        except Exception as e:
            self.logger.error(f"Öğretmen silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen silinirken bir hata oluştu:\n{str(e)}")
    
    def add_zaman(self):
        """
        Öğretmene uygun olmayan zaman ekler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen önce bir öğretmen seçin veya kaydedin.")
            return
        
        # Zaman ekleme penceresi
        self.open_zaman_dialog()
    
    def edit_zaman(self):
        """
        Seçili uygun olmayan zamanı düzenler
        """
        # Seçili zamanı al
        selected_items = self.zaman_tree.selection()
        if not selected_items:
            messagebox.showerror("Hata", "Lütfen düzenlenecek zamanı seçin.")
            return
        
        # Zaman düzenleme penceresi
        self.open_zaman_dialog(edit_mode=True)
    
    def delete_zaman(self):
        """
        Seçili uygun olmayan zamanı siler
        """
        # Seçili zamanı al
        selected_items = self.zaman_tree.selection()
        if not selected_items:
            messagebox.showerror("Hata", "Lütfen silinecek zamanı seçin.")
            return
        
        # Seçili zamanın ID'sini al
        item = selected_items[0]
        zaman_id = int(self.zaman_tree.item(item, "tags")[0])
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili zamanı silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # Zamanı sil
            self.db.uygun_olmayan_zaman_sil(zaman_id)
            
            messagebox.showinfo("Bilgi", "Zaman başarıyla silindi.")
            self.logger.info(f"Zaman silindi: ID {zaman_id}")
            
            # Zaman listesini yenile
            self.refresh_zaman_list()
        except Exception as e:
            self.logger.error(f"Zaman silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Zaman silinirken bir hata oluştu:\n{str(e)}")
    
    def open_zaman_dialog(self, edit_mode=False):
        """
        Uygun olmayan zaman ekleme/düzenleme penceresini açar
        
        Args:
            edit_mode (bool, optional): Düzenleme modu. Defaults to False.
        """
        # Yeni pencere oluştur
        dialog = tk.Toplevel(self.parent)
        dialog.title("Uygun Olmayan Zaman Ekle" if not edit_mode else "Uygun Olmayan Zaman Düzenle")
        dialog.geometry("400x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Gün seçimi
        ttk.Label(dialog, text="Gün:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        gun_var = tk.StringVar()
        gun_combobox = ttk.Combobox(dialog, textvariable=gun_var, state="readonly")
        gun_combobox.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Gün listesi
        gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        gun_combobox["values"] = gun_adlari
        
        # Başlangıç saati
        ttk.Label(dialog, text="Başlangıç Saati:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        baslangic_var = tk.IntVar(value=1)
        baslangic_spinbox = ttk.Spinbox(dialog, from_=1, to=8, textvariable=baslangic_var)
        baslangic_spinbox.grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Bitiş saati
        ttk.Label(dialog, text="Bitiş Saati:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        bitis_var = tk.IntVar(value=2)
        bitis_spinbox = ttk.Spinbox(dialog, from_=1, to=8, textvariable=bitis_var)
        bitis_spinbox.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Kaydet butonu
        save_button = ttk.Button(button_frame, text="Kaydet", command=lambda: self.save_zaman_dialog(
            dialog, gun_combobox, baslangic_var, bitis_var, edit_mode))
        save_button.pack(side=tk.LEFT, padx=5)
        
        # İptal butonu
        cancel_button = ttk.Button(button_frame, text="İptal", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Düzenleme modunda mevcut değerleri yükle
        if edit_mode:
            selected_items = self.zaman_tree.selection()
            if selected_items:
                item = selected_items[0]
                zaman_id = int(self.zaman_tree.item(item, "tags")[0])
                
                try:
                    # Veritabanından zamanı getir
                    self.db.execute("SELECT * FROM uygun_olmayan_zamanlar WHERE id=?", (zaman_id,))
                    zaman = self.db.fetchone()
                    
                    # Değerleri ayarla
                    gun_var.set(gun_adlari[zaman["gun"]] if 0 <= zaman["gun"] < len(gun_adlari) else "")
                    baslangic_var.set(zaman["saat_baslangic"])
                    bitis_var.set(zaman["saat_bitis"])
                    
                    # Zaman ID'sini sakla
                    dialog.zaman_id = zaman_id
                except Exception as e:
                    self.logger.error(f"Zaman bilgileri yükleme hatası: {str(e)}")
                    messagebox.showerror("Hata", f"Zaman bilgileri yüklenirken bir hata oluştu:\n{str(e)}")
        
        # Pencereyi ortala
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def save_zaman_dialog(self, dialog, gun_combobox, baslangic_var, bitis_var, edit_mode):
        """
        Uygun olmayan zaman ekleme/düzenleme penceresindeki bilgileri kaydeder
        
        Args:
            dialog (tk.Toplevel): Pencere
            gun_combobox (ttk.Combobox): Gün seçim kutusu
            baslangic_var (tk.IntVar): Başlangıç saati değişkeni
            bitis_var (tk.IntVar): Bitiş saati değişkeni
            edit_mode (bool): Düzenleme modu
        """
        # Değerleri al
        gun_adi = gun_combobox.get()
        
        try:
            baslangic = int(baslangic_var.get())
            bitis = int(bitis_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Başlangıç ve bitiş saatleri sayısal değerler olmalıdır.")
            return
        
        # Veri doğrulama
        if not gun_adi:
            messagebox.showerror("Hata", "Lütfen bir gün seçin.")
            return
        
        if baslangic < 1 or baslangic > 8:
            messagebox.showerror("Hata", "Başlangıç saati 1-8 arasında olmalıdır.")
            return
        
        if bitis < 1 or bitis > 8:
            messagebox.showerror("Hata", "Bitiş saati 1-8 arasında olmalıdır.")
            return
        
        if baslangic >= bitis:
            messagebox.showerror("Hata", "Başlangıç saati bitiş saatinden küçük olmalıdır.")
            return
        
        # Gün indeksini bul
        gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        gun = gun_adlari.index(gun_adi) if gun_adi in gun_adlari else -1
        
        if gun == -1:
            messagebox.showerror("Hata", "Geçersiz gün seçimi.")
            return
        
        try:
            if edit_mode:
                # Mevcut zamanı güncelle
                zaman_id = dialog.zaman_id
                self.db.uygun_olmayan_zaman_guncelle(zaman_id, self.selected_id, gun, baslangic, bitis)
                messagebox.showinfo("Bilgi", "Zaman başarıyla güncellendi.")
                self.logger.info(f"Zaman güncellendi: Gün {gun_adi}, Saat {baslangic}-{bitis}")
            else:
                # Yeni zaman ekle
                self.db.uygun_olmayan_zaman_ekle(self.selected_id, gun, baslangic, bitis)
                messagebox.showinfo("Bilgi", "Zaman başarıyla eklendi.")
                self.logger.info(f"Zaman eklendi: Gün {gun_adi}, Saat {baslangic}-{bitis}")
            
            # Zaman listesini yenile
            self.refresh_zaman_list()
            
            # Pencereyi kapat
            dialog.destroy()
        except Exception as e:
            self.logger.error(f"Zaman kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Zaman kaydedilirken bir hata oluştu:\n{str(e)}")

