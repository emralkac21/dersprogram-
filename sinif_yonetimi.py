#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sınıf yönetimi arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class SinifYonetimi:
    """
    Sınıf yönetimi arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Sınıf yönetimi arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Seçili sınıf ID'si
        self.selected_id = None
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Sınıfları listele
        self.refresh_list()
        
        self.logger.info("Sınıf yönetimi arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeveyi iki bölüme ayır
        self.paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sol panel - Sınıf listesi
        self.list_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.list_frame, weight=1)
        
        # Sınıf listesi
        self.create_list_widgets()
        
        # Sağ panel - Sınıf detayları
        self.detail_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.detail_frame, weight=2)
        
        # Sınıf detayları
        self.create_detail_widgets()
    
    def create_list_widgets(self):
        """
        Sınıf listesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.list_frame, text="Sınıf Listesi", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Arama çubuğu
        self.search_frame = ttk.Frame(self.list_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Ara:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_var.trace("w", lambda name, index, mode: self.filter_list())
        
        # Sınıf listesi
        self.list_frame_inner = ttk.Frame(self.list_frame)
        self.list_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame_inner)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(self.list_frame_inner, columns=("ad", "sube", "haftalik_saat"), 
                                show="headings", selectmode="browse", yscrollcommand=self.scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.tree.yview)
        
        # Sütun başlıkları
        self.tree.heading("ad", text="Sınıf Adı")
        self.tree.heading("sube", text="Şube")
        self.tree.heading("haftalik_saat", text="Haftalık Saat")
        
        # Sütun genişlikleri
        self.tree.column("ad", width=100)
        self.tree.column("sube", width=50)
        self.tree.column("haftalik_saat", width=100)
        
        # Seçim olayı
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Butonlar
        self.button_frame = ttk.Frame(self.list_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(self.button_frame, text="Yeni Sınıf", command=self.clear_form)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(self.button_frame, text="Sil", command=self.delete_sinif)
        self.delete_button.pack(side=tk.RIGHT, padx=5)
    
    def create_detail_widgets(self):
        """
        Sınıf detayları bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.detail_frame, text="Sınıf Detayları", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Form
        self.form_frame = ttk.Frame(self.detail_frame)
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sınıf Adı
        ttk.Label(self.form_frame, text="Sınıf Adı:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ad_var = tk.StringVar()
        self.ad_entry = ttk.Entry(self.form_frame, textvariable=self.ad_var)
        self.ad_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Şube
        ttk.Label(self.form_frame, text="Şube:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sube_var = tk.StringVar()
        self.sube_entry = ttk.Entry(self.form_frame, textvariable=self.sube_var)
        self.sube_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Haftalık Toplam Saat
        ttk.Label(self.form_frame, text="Haftalık Toplam Saat:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.haftalik_saat_var = tk.IntVar()
        self.haftalik_saat_spinbox = ttk.Spinbox(self.form_frame, from_=0, to=50, textvariable=self.haftalik_saat_var)
        self.haftalik_saat_spinbox.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Butonlar
        self.form_button_frame = ttk.Frame(self.form_frame)
        self.form_button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.save_button = ttk.Button(self.form_button_frame, text="Kaydet", command=self.save_sinif)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(self.form_button_frame, text="İptal", command=self.clear_form)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Sınıf Dersleri
        ttk.Label(self.form_frame, text="Sınıf Dersleri:", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Ders listesi çerçevesi
        self.ders_frame = ttk.Frame(self.form_frame)
        self.ders_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Ders listesi
        self.ders_tree_frame = ttk.Frame(self.ders_frame)
        self.ders_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.ders_scrollbar = ttk.Scrollbar(self.ders_tree_frame)
        self.ders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.ders_tree = ttk.Treeview(self.ders_tree_frame, columns=("ders", "ogretmen", "saat"), 
                                    show="headings", selectmode="browse", yscrollcommand=self.ders_scrollbar.set)
        self.ders_tree.pack(fill=tk.BOTH, expand=True)
        
        self.ders_scrollbar.config(command=self.ders_tree.yview)
        
        # Sütun başlıkları
        self.ders_tree.heading("ders", text="Ders")
        self.ders_tree.heading("ogretmen", text="Öğretmen")
        self.ders_tree.heading("saat", text="Haftalık Saat")
        
        # Sütun genişlikleri
        self.ders_tree.column("ders", width=150)
        self.ders_tree.column("ogretmen", width=150)
        self.ders_tree.column("saat", width=100)
        
        # Ders butonları
        self.ders_button_frame = ttk.Frame(self.ders_frame)
        self.ders_button_frame.pack(fill=tk.X, pady=5)
        
        self.add_ders_button = ttk.Button(self.ders_button_frame, text="Ders Ekle", command=self.add_ders)
        self.add_ders_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_ders_button = ttk.Button(self.ders_button_frame, text="Düzenle", command=self.edit_ders)
        self.edit_ders_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_ders_button = ttk.Button(self.ders_button_frame, text="Sil", command=self.delete_ders)
        self.delete_ders_button.pack(side=tk.LEFT, padx=5)
        
        # Form alanlarını genişlet
        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.rowconfigure(5, weight=1)
    
    def refresh_list(self):
        """
        Sınıf listesini yeniler
        """
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Sınıfları getir
            siniflar = self.db.tum_siniflari_getir()
            
            # Listeye ekle
            for sinif in siniflar:
                self.tree.insert("", tk.END, values=(sinif["ad"], sinif["sube"], sinif["haftalik_toplam_saat"]), 
                                tags=(sinif["id"],))
            
            self.logger.info(f"{len(siniflar)} sınıf listelendi")
        except Exception as e:
            self.logger.error(f"Sınıf listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def filter_list(self):
        """
        Sınıf listesini filtreler
        """
        search_term = self.search_var.get().lower()
        
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Sınıfları getir
            siniflar = self.db.tum_siniflari_getir()
            
            # Filtrele ve listeye ekle
            for sinif in siniflar:
                if (search_term in sinif["ad"].lower() or 
                    search_term in sinif["sube"].lower()):
                    self.tree.insert("", tk.END, values=(sinif["ad"], sinif["sube"], sinif["haftalik_toplam_saat"]), 
                                    tags=(sinif["id"],))
        except Exception as e:
            self.logger.error(f"Sınıf listesi filtreleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf listesi filtrelenirken bir hata oluştu:\n{str(e)}")
    
    def on_select(self, event):
        """
        Sınıf seçildiğinde çağrılır
        
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
            # Sınıf bilgilerini getir
            sinif = self.db.sinif_getir(self.selected_id)
            if not sinif:
                return
            
            # Form alanlarını doldur
            self.ad_var.set(sinif["ad"])
            self.sube_var.set(sinif["sube"])
            self.haftalik_saat_var.set(sinif["haftalik_toplam_saat"])
            
            # Sınıfın derslerini getir
            self.refresh_ders_list()
            
            self.logger.info(f"Sınıf seçildi: {sinif['ad']} {sinif['sube']}")
        except Exception as e:
            self.logger.error(f"Sınıf seçme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf bilgileri alınırken bir hata oluştu:\n{str(e)}")
    
    def refresh_ders_list(self):
        """
        Sınıfın ders listesini yeniler
        """
        # Listeyi temizle
        for item in self.ders_tree.get_children():
            self.ders_tree.delete(item)
        
        if not self.selected_id:
            return
        
        try:
            # Sınıfın derslerini getir
            dersler = self.db.sinifin_derslerini_getir(self.selected_id)
            
            # Listeye ekle
            for ders in dersler:
                self.ders_tree.insert("", tk.END, values=(ders["ders_adi"], ders["ogretmen_adi"], ders["haftalik_saat"]), 
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
        self.ad_var.set("")
        self.sube_var.set("")
        self.haftalik_saat_var.set(30)  # Varsayılan değer
        
        # Ders listesini temizle
        for item in self.ders_tree.get_children():
            self.ders_tree.delete(item)
        
        # Odağı sınıf adı alanına taşı
        self.ad_entry.focus()
    
    def save_sinif(self):
        """
        Sınıf bilgilerini kaydeder
        """
        # Form verilerini al
        ad = self.ad_var.get().strip()
        sube = self.sube_var.get().strip()
        
        try:
            haftalik_saat = int(self.haftalik_saat_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Haftalık saat sayısal bir değer olmalıdır.")
            return
        
        # Veri doğrulama
        if not ad:
            messagebox.showerror("Hata", "Sınıf adı boş olamaz.")
            return
        
        if not sube:
            messagebox.showerror("Hata", "Şube boş olamaz.")
            return
        
        if haftalik_saat <= 0:
            messagebox.showerror("Hata", "Haftalık saat 0'dan büyük olmalıdır.")
            return
        
        try:
            if self.selected_id:
                # Mevcut sınıfı güncelle
                self.db.sinif_guncelle(self.selected_id, ad, sube, haftalik_saat)
                messagebox.showinfo("Bilgi", f"{ad} {sube} sınıfı başarıyla güncellendi.")
                self.logger.info(f"Sınıf güncellendi: {ad} {sube}")
            else:
                # Yeni sınıf ekle
                self.selected_id = self.db.sinif_ekle(ad, sube, haftalik_saat)
                messagebox.showinfo("Bilgi", f"{ad} {sube} sınıfı başarıyla eklendi.")
                self.logger.info(f"Sınıf eklendi: {ad} {sube}")
            
            # Listeyi yenile
            self.refresh_list()
            
            # Yeni eklenen/güncellenen sınıfı seç
            for item in self.tree.get_children():
                if int(self.tree.item(item, "tags")[0]) == self.selected_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            self.logger.error(f"Sınıf kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def delete_sinif(self):
        """
        Seçili sınıfı siler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen silinecek sınıfı seçin.")
            return
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili sınıfı silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # Sınıf bilgilerini al
            sinif = self.db.sinif_getir(self.selected_id)
            
            # Sınıfı sil
            self.db.sinif_sil(self.selected_id)
            
            messagebox.showinfo("Bilgi", f"{sinif['ad']} {sinif['sube']} sınıfı başarıyla silindi.")
            self.logger.info(f"Sınıf silindi: {sinif['ad']} {sinif['sube']}")
            
            # Formu temizle
            self.clear_form()
            
            # Listeyi yenile
            self.refresh_list()
        except Exception as e:
            self.logger.error(f"Sınıf silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf silinirken bir hata oluştu:\n{str(e)}")
    
    def add_ders(self):
        """
        Sınıfa ders ekler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen önce bir sınıf seçin veya kaydedin.")
            return
        
        # Ders ekleme penceresi
        self.open_ders_dialog()
    
    def edit_ders(self):
        """
        Seçili dersi düzenler
        """
        # Seçili dersi al
        selected_items = self.ders_tree.selection()
        if not selected_items:
            messagebox.showerror("Hata", "Lütfen düzenlenecek dersi seçin.")
            return
        
        # Ders düzenleme penceresi
        self.open_ders_dialog(edit_mode=True)
    
    def delete_ders(self):
        """
        Seçili dersi siler
        """
        # Seçili dersi al
        selected_items = self.ders_tree.selection()
        if not selected_items:
            messagebox.showerror("Hata", "Lütfen silinecek dersi seçin.")
            return
        
        # Seçili dersin ID'sini al
        item = selected_items[0]
        ders_id = int(self.ders_tree.item(item, "tags")[0])
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili dersi silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # Ders-sınıf ilişkisini sil
            self.db.ders_sinif_iliskisi_sil(ders_id)
            
            messagebox.showinfo("Bilgi", "Ders başarıyla silindi.")
            self.logger.info(f"Ders silindi: ID {ders_id}")
            
            # Ders listesini yenile
            self.refresh_ders_list()
        except Exception as e:
            self.logger.error(f"Ders silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders silinirken bir hata oluştu:\n{str(e)}")
    
    def open_ders_dialog(self, edit_mode=False):
        """
        Ders ekleme/düzenleme penceresini açar
        
        Args:
            edit_mode (bool, optional): Düzenleme modu. Defaults to False.
        """
        # Yeni pencere oluştur
        dialog = tk.Toplevel(self.parent)
        dialog.title("Ders Ekle" if not edit_mode else "Ders Düzenle")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Ders seçimi
        ttk.Label(dialog, text="Ders:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ders_var = tk.StringVar()
        ders_combobox = ttk.Combobox(dialog, textvariable=ders_var, state="readonly")
        ders_combobox.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Öğretmen seçimi
        ttk.Label(dialog, text="Öğretmen:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ogretmen_var = tk.StringVar()
        ogretmen_combobox = ttk.Combobox(dialog, textvariable=ogretmen_var, state="readonly")
        ogretmen_combobox.grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Haftalık saat
        ttk.Label(dialog, text="Haftalık Saat:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        haftalik_saat_var = tk.IntVar(value=2)  # Varsayılan değer
        haftalik_saat_spinbox = ttk.Spinbox(dialog, from_=1, to=20, textvariable=haftalik_saat_var)
        haftalik_saat_spinbox.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Kaydet butonu
        save_button = ttk.Button(button_frame, text="Kaydet", command=lambda: self.save_ders_dialog(
            dialog, ders_combobox, ogretmen_combobox, haftalik_saat_var, edit_mode))
        save_button.pack(side=tk.LEFT, padx=5)
        
        # İptal butonu
        cancel_button = ttk.Button(button_frame, text="İptal", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Dersleri yükle
        try:
            dersler = self.db.tum_dersleri_getir()
            ders_combobox["values"] = [ders["ad"] for ders in dersler]
            
            # Ders ID'lerini sakla
            ders_combobox.ders_ids = {ders["ad"]: ders["id"] for ders in dersler}
        except Exception as e:
            self.logger.error(f"Ders listesi yükleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders listesi yüklenirken bir hata oluştu:\n{str(e)}")
        
        # Öğretmenleri yükle
        try:
            ogretmenler = self.db.tum_ogretmenleri_getir()
            ogretmen_combobox["values"] = [ogretmen["ad_soyad"] for ogretmen in ogretmenler]
            
            # Öğretmen ID'lerini sakla
            ogretmen_combobox.ogretmen_ids = {ogretmen["ad_soyad"]: ogretmen["id"] for ogretmen in ogretmenler}
        except Exception as e:
            self.logger.error(f"Öğretmen listesi yükleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Öğretmen listesi yüklenirken bir hata oluştu:\n{str(e)}")
        
        # Düzenleme modunda mevcut değerleri yükle
        if edit_mode:
            selected_items = self.ders_tree.selection()
            if selected_items:
                item = selected_items[0]
                ders_id = int(self.ders_tree.item(item, "tags")[0])
                
                try:
                    # Ders-sınıf ilişkisini getir
                    ders_sinif = self.db.ders_sinif_iliskisi_getir(ders_id)
                    
                    # Ders ve öğretmen bilgilerini getir
                    ders = self.db.ders_getir(ders_sinif["ders_id"])
                    ogretmen = self.db.ogretmen_getir(ders_sinif["ogretmen_id"])
                    
                    # Değerleri ayarla
                    ders_var.set(ders["ad"])
                    ogretmen_var.set(ogretmen["ad_soyad"])
                    haftalik_saat_var.set(ders_sinif["haftalik_saat"])
                    
                    # Ders ID'sini sakla
                    dialog.ders_sinif_id = ders_id
                except Exception as e:
                    self.logger.error(f"Ders bilgileri yükleme hatası: {str(e)}")
                    messagebox.showerror("Hata", f"Ders bilgileri yüklenirken bir hata oluştu:\n{str(e)}")
        
        # Pencereyi ortala
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def save_ders_dialog(self, dialog, ders_combobox, ogretmen_combobox, haftalik_saat_var, edit_mode):
        """
        Ders ekleme/düzenleme penceresindeki bilgileri kaydeder
        
        Args:
            dialog (tk.Toplevel): Pencere
            ders_combobox (ttk.Combobox): Ders seçim kutusu
            ogretmen_combobox (ttk.Combobox): Öğretmen seçim kutusu
            haftalik_saat_var (tk.IntVar): Haftalık saat değişkeni
            edit_mode (bool): Düzenleme modu
        """
        # Değerleri al
        ders_adi = ders_combobox.get()
        ogretmen_adi = ogretmen_combobox.get()
        
        try:
            haftalik_saat = int(haftalik_saat_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Haftalık saat sayısal bir değer olmalıdır.")
            return
        
        # Veri doğrulama
        if not ders_adi:
            messagebox.showerror("Hata", "Lütfen bir ders seçin.")
            return
        
        if not ogretmen_adi:
            messagebox.showerror("Hata", "Lütfen bir öğretmen seçin.")
            return
        
        if haftalik_saat <= 0:
            messagebox.showerror("Hata", "Haftalık saat 0'dan büyük olmalıdır.")
            return
        
        # ID'leri al
        ders_id = ders_combobox.ders_ids.get(ders_adi)
        ogretmen_id = ogretmen_combobox.ogretmen_ids.get(ogretmen_adi)
        
        try:
            if edit_mode:
                # Mevcut ders-sınıf ilişkisini güncelle
                ders_sinif_id = dialog.ders_sinif_id
                self.db.ders_sinif_iliskisi_guncelle(ders_sinif_id, ders_id, self.selected_id, ogretmen_id, haftalik_saat)
                messagebox.showinfo("Bilgi", "Ders başarıyla güncellendi.")
                self.logger.info(f"Ders güncellendi: {ders_adi}, Öğretmen: {ogretmen_adi}")
            else:
                # Yeni ders-sınıf ilişkisi ekle
                self.db.ders_sinif_iliskisi_ekle(ders_id, self.selected_id, ogretmen_id, haftalik_saat)
                messagebox.showinfo("Bilgi", "Ders başarıyla eklendi.")
                self.logger.info(f"Ders eklendi: {ders_adi}, Öğretmen: {ogretmen_adi}")
            
            # Ders listesini yenile
            self.refresh_ders_list()
            
            # Pencereyi kapat
            dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            self.logger.error(f"Ders kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders kaydedilirken bir hata oluştu:\n{str(e)}")
