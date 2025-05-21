#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ders yönetimi arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

class DersYonetimi:
    """
    Ders yönetimi arayüzü
    """
    
    def __init__(self, parent, db, config):
        """
        Ders yönetimi arayüzünü başlatır
        
        Args:
            parent (ttk.Frame): Üst çerçeve
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.parent = parent
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Seçili ders ID'si
        self.selected_id = None
        
        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        
        # Dersleri listele
        self.refresh_list()
        
        self.logger.info("Ders yönetimi arayüzü oluşturuldu")
    
    def create_widgets(self):
        """
        Arayüz bileşenlerini oluşturur
        """
        # Ana çerçeveyi iki bölüme ayır
        self.paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sol panel - Ders listesi
        self.list_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.list_frame, weight=1)
        
        # Ders listesi
        self.create_list_widgets()
        
        # Sağ panel - Ders detayları
        self.detail_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.detail_frame, weight=2)
        
        # Ders detayları
        self.create_detail_widgets()
    
    def create_list_widgets(self):
        """
        Ders listesi bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.list_frame, text="Ders Listesi", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Arama çubuğu
        self.search_frame = ttk.Frame(self.list_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Ara:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_var.trace("w", lambda name, index, mode: self.filter_list())
        
        # Ders listesi
        self.list_frame_inner = ttk.Frame(self.list_frame)
        self.list_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.list_frame_inner)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(self.list_frame_inner, columns=("ad", "haftalik_saat"), 
                                show="headings", selectmode="browse", yscrollcommand=self.scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.tree.yview)
        
        # Sütun başlıkları
        self.tree.heading("ad", text="Ders Adı")
        self.tree.heading("haftalik_saat", text="Haftalık Saat")
        
        # Sütun genişlikleri
        self.tree.column("ad", width=150)
        self.tree.column("haftalik_saat", width=100)
        
        # Seçim olayı
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Butonlar
        self.button_frame = ttk.Frame(self.list_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(self.button_frame, text="Yeni Ders", command=self.clear_form)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(self.button_frame, text="Sil", command=self.delete_ders)
        self.delete_button.pack(side=tk.RIGHT, padx=5)
    
    def create_detail_widgets(self):
        """
        Ders detayları bileşenlerini oluşturur
        """
        # Başlık
        ttk.Label(self.detail_frame, text="Ders Detayları", font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        
        # Form
        self.form_frame = ttk.Frame(self.detail_frame)
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ders Adı
        ttk.Label(self.form_frame, text="Ders Adı:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ad_var = tk.StringVar()
        self.ad_entry = ttk.Entry(self.form_frame, textvariable=self.ad_var)
        self.ad_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Haftalık Saat
        ttk.Label(self.form_frame, text="Haftalık Saat:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.haftalik_saat_var = tk.IntVar()
        self.haftalik_saat_spinbox = ttk.Spinbox(self.form_frame, from_=1, to=20, textvariable=self.haftalik_saat_var)
        self.haftalik_saat_spinbox.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Butonlar
        self.form_button_frame = ttk.Frame(self.form_frame)
        self.form_button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.save_button = ttk.Button(self.form_button_frame, text="Kaydet", command=self.save_ders)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(self.form_button_frame, text="İptal", command=self.clear_form)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Ders-Sınıf-Öğretmen İlişkileri
        ttk.Label(self.form_frame, text="Ders-Sınıf-Öğretmen İlişkileri:", font=("TkDefaultFont", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # İlişki listesi çerçevesi
        self.iliski_frame = ttk.Frame(self.form_frame)
        self.iliski_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # İlişki listesi
        self.iliski_tree_frame = ttk.Frame(self.iliski_frame)
        self.iliski_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.iliski_scrollbar = ttk.Scrollbar(self.iliski_tree_frame)
        self.iliski_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.iliski_tree = ttk.Treeview(self.iliski_tree_frame, columns=("sinif", "ogretmen", "saat"), 
                                    show="headings", selectmode="browse", yscrollcommand=self.iliski_scrollbar.set)
        self.iliski_tree.pack(fill=tk.BOTH, expand=True)
        
        self.iliski_scrollbar.config(command=self.iliski_tree.yview)
        
        # Sütun başlıkları
        self.iliski_tree.heading("sinif", text="Sınıf")
        self.iliski_tree.heading("ogretmen", text="Öğretmen")
        self.iliski_tree.heading("saat", text="Haftalık Saat")
        
        # Sütun genişlikleri
        self.iliski_tree.column("sinif", width=100)
        self.iliski_tree.column("ogretmen", width=150)
        self.iliski_tree.column("saat", width=100)
        
        # İlişki butonları
        self.iliski_button_frame = ttk.Frame(self.iliski_frame)
        self.iliski_button_frame.pack(fill=tk.X, pady=5)
        
        self.add_iliski_button = ttk.Button(self.iliski_button_frame, text="İlişki Ekle", command=self.add_iliski)
        self.add_iliski_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_iliski_button = ttk.Button(self.iliski_button_frame, text="Düzenle", command=self.edit_iliski)
        self.edit_iliski_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_iliski_button = ttk.Button(self.iliski_button_frame, text="Sil", command=self.delete_iliski)
        self.delete_iliski_button.pack(side=tk.LEFT, padx=5)
        
        # Form alanlarını genişlet
        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.rowconfigure(4, weight=1)
    
    def refresh_list(self):
        """
        Ders listesini yeniler
        """
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Dersleri getir
            dersler = self.db.tum_dersleri_getir()
            
            # Listeye ekle
            for ders in dersler:
                self.tree.insert("", tk.END, values=(ders["ad"], ders["haftalik_saat"]), 
                                tags=(ders["id"],))
            
            self.logger.info(f"{len(dersler)} ders listelendi")
        except Exception as e:
            self.logger.error(f"Ders listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def filter_list(self):
        """
        Ders listesini filtreler
        """
        search_term = self.search_var.get().lower()
        
        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Dersleri getir
            dersler = self.db.tum_dersleri_getir()
            
            # Filtrele ve listeye ekle
            for ders in dersler:
                if search_term in ders["ad"].lower():
                    self.tree.insert("", tk.END, values=(ders["ad"], ders["haftalik_saat"]), 
                                    tags=(ders["id"],))
        except Exception as e:
            self.logger.error(f"Ders listesi filtreleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders listesi filtrelenirken bir hata oluştu:\n{str(e)}")
    
    def on_select(self, event):
        """
        Ders seçildiğinde çağrılır
        
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
            # Ders bilgilerini getir
            ders = self.db.ders_getir(self.selected_id)
            if not ders:
                return
            
            # Form alanlarını doldur
            self.ad_var.set(ders["ad"])
            self.haftalik_saat_var.set(ders["haftalik_saat"])
            
            # Ders-sınıf-öğretmen ilişkilerini getir
            self.refresh_iliski_list()
            
            self.logger.info(f"Ders seçildi: {ders['ad']}")
        except Exception as e:
            self.logger.error(f"Ders seçme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders bilgileri alınırken bir hata oluştu:\n{str(e)}")
    
    def refresh_iliski_list(self):
        """
        Ders-sınıf-öğretmen ilişkileri listesini yeniler
        """
        # Listeyi temizle
        for item in self.iliski_tree.get_children():
            self.iliski_tree.delete(item)
        
        if not self.selected_id:
            return
        
        try:
            # SQL sorgusu ile ilişkileri getir
            self.db.execute("""
                SELECT ds.*, s.ad as sinif_adi, s.sube as sinif_sube, o.ad_soyad as ogretmen_adi
                FROM ders_sinif ds
                JOIN siniflar s ON ds.sinif_id = s.id
                JOIN ogretmenler o ON ds.ogretmen_id = o.id
                WHERE ds.ders_id = ?
                ORDER BY s.ad, s.sube
            """, (self.selected_id,))
            
            iliskiler = self.db.fetchall()
            
            # Listeye ekle
            for iliski in iliskiler:
                sinif_adi = f"{iliski['sinif_adi']} {iliski['sinif_sube']}"
                self.iliski_tree.insert("", tk.END, values=(sinif_adi, iliski["ogretmen_adi"], iliski["haftalik_saat"]), 
                                    tags=(iliski["id"],))
            
            self.logger.info(f"{len(iliskiler)} ilişki listelendi")
        except Exception as e:
            self.logger.error(f"İlişki listesi yenileme hatası: {str(e)}")
            messagebox.showerror("Hata", f"İlişki listesi yenilenirken bir hata oluştu:\n{str(e)}")
    
    def clear_form(self):
        """
        Form alanlarını temizler
        """
        self.selected_id = None
        self.ad_var.set("")
        self.haftalik_saat_var.set(4)  # Varsayılan değer
        
        # İlişki listesini temizle
        for item in self.iliski_tree.get_children():
            self.iliski_tree.delete(item)
        
        # Odağı ders adı alanına taşı
        self.ad_entry.focus()
    
    def save_ders(self):
        """
        Ders bilgilerini kaydeder
        """
        # Form verilerini al
        ad = self.ad_var.get().strip()
        
        try:
            haftalik_saat = int(self.haftalik_saat_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Haftalık saat sayısal bir değer olmalıdır.")
            return
        
        # Veri doğrulama
        if not ad:
            messagebox.showerror("Hata", "Ders adı boş olamaz.")
            return
        
        if haftalik_saat <= 0:
            messagebox.showerror("Hata", "Haftalık saat 0'dan büyük olmalıdır.")
            return
        
        try:
            if self.selected_id:
                # Mevcut dersi güncelle
                self.db.ders_guncelle(self.selected_id, ad, haftalik_saat)
                messagebox.showinfo("Bilgi", f"{ad} dersi başarıyla güncellendi.")
                self.logger.info(f"Ders güncellendi: {ad}")
            else:
                # Yeni ders ekle
                self.selected_id = self.db.ders_ekle(ad, haftalik_saat)
                messagebox.showinfo("Bilgi", f"{ad} dersi başarıyla eklendi.")
                self.logger.info(f"Ders eklendi: {ad}")
            
            # Listeyi yenile
            self.refresh_list()
            
            # Yeni eklenen/güncellenen dersi seç
            for item in self.tree.get_children():
                if int(self.tree.item(item, "tags")[0]) == self.selected_id:
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            self.logger.error(f"Ders kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders kaydedilirken bir hata oluştu:\n{str(e)}")
    
    def delete_ders(self):
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
            # Ders bilgilerini al
            ders = self.db.ders_getir(self.selected_id)
            
            # Dersi sil
            self.db.ders_sil(self.selected_id)
            
            messagebox.showinfo("Bilgi", f"{ders['ad']} dersi başarıyla silindi.")
            self.logger.info(f"Ders silindi: {ders['ad']}")
            
            # Formu temizle
            self.clear_form()
            
            # Listeyi yenile
            self.refresh_list()
        except Exception as e:
            self.logger.error(f"Ders silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Ders silinirken bir hata oluştu:\n{str(e)}")
    
    def add_iliski(self):
        """
        Ders-sınıf-öğretmen ilişkisi ekler
        """
        if not self.selected_id:
            messagebox.showerror("Hata", "Lütfen önce bir ders seçin veya kaydedin.")
            return
        
        # İlişki ekleme penceresi
        self.open_iliski_dialog()
    
    def edit_iliski(self):
        """
        Seçili ilişkiyi düzenler
        """
        # Seçili ilişkiyi al
        selected_items = self.iliski_tree.selection()
        if not selected_items:
            messagebox.showerror("Hata", "Lütfen düzenlenecek ilişkiyi seçin.")
            return
        
        # İlişki düzenleme penceresi
        self.open_iliski_dialog(edit_mode=True)
    
    def delete_iliski(self):
        """
        Seçili ilişkiyi siler
        """
        # Seçili ilişkiyi al
        selected_items = self.iliski_tree.selection()
        if not selected_items:
            messagebox.showerror("Hata", "Lütfen silinecek ilişkiyi seçin.")
            return
        
        # Seçili ilişkinin ID'sini al
        item = selected_items[0]
        iliski_id = int(self.iliski_tree.item(item, "tags")[0])
        
        # Onay iste
        if not messagebox.askyesno("Onay", "Seçili ilişkiyi silmek istediğinizden emin misiniz?"):
            return
        
        try:
            # İlişkiyi sil
            self.db.ders_sinif_iliskisi_sil(iliski_id)
            
            messagebox.showinfo("Bilgi", "İlişki başarıyla silindi.")
            self.logger.info(f"İlişki silindi: ID {iliski_id}")
            
            # İlişki listesini yenile
            self.refresh_iliski_list()
        except Exception as e:
            self.logger.error(f"İlişki silme hatası: {str(e)}")
            messagebox.showerror("Hata", f"İlişki silinirken bir hata oluştu:\n{str(e)}")
    
    def open_iliski_dialog(self, edit_mode=False):
        """
        Ders-sınıf-öğretmen ilişkisi ekleme/düzenleme penceresini açar
        
        Args:
            edit_mode (bool, optional): Düzenleme modu. Defaults to False.
        """
        # Yeni pencere oluştur
        dialog = tk.Toplevel(self.parent)
        dialog.title("İlişki Ekle" if not edit_mode else "İlişki Düzenle")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Sınıf seçimi
        ttk.Label(dialog, text="Sınıf:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        sinif_var = tk.StringVar()
        sinif_combobox = ttk.Combobox(dialog, textvariable=sinif_var, state="readonly")
        sinif_combobox.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Öğretmen seçimi
        ttk.Label(dialog, text="Öğretmen:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ogretmen_var = tk.StringVar()
        ogretmen_combobox = ttk.Combobox(dialog, textvariable=ogretmen_var, state="readonly")
        ogretmen_combobox.grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Haftalık saat
        ttk.Label(dialog, text="Haftalık Saat:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        haftalik_saat_var = tk.IntVar(value=4)  # Varsayılan değer
        haftalik_saat_spinbox = ttk.Spinbox(dialog, from_=1, to=20, textvariable=haftalik_saat_var)
        haftalik_saat_spinbox.grid(row=2, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Butonlar
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Kaydet butonu
        save_button = ttk.Button(button_frame, text="Kaydet", command=lambda: self.save_iliski_dialog(
            dialog, sinif_combobox, ogretmen_combobox, haftalik_saat_var, edit_mode))
        save_button.pack(side=tk.LEFT, padx=5)
        
        # İptal butonu
        cancel_button = ttk.Button(button_frame, text="İptal", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Sınıfları yükle
        try:
            siniflar = self.db.tum_siniflari_getir()
            sinif_combobox["values"] = [f"{sinif['ad']} {sinif['sube']}" for sinif in siniflar]
            
            # Sınıf ID'lerini sakla
            sinif_combobox.sinif_ids = {f"{sinif['ad']} {sinif['sube']}": sinif["id"] for sinif in siniflar}
        except Exception as e:
            self.logger.error(f"Sınıf listesi yükleme hatası: {str(e)}")
            messagebox.showerror("Hata", f"Sınıf listesi yüklenirken bir hata oluştu:\n{str(e)}")
        
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
            selected_items = self.iliski_tree.selection()
            if selected_items:
                item = selected_items[0]
                iliski_id = int(self.iliski_tree.item(item, "tags")[0])
                
                try:
                    # İlişkiyi getir
                    self.db.execute("""
                        SELECT ds.*, s.ad as sinif_adi, s.sube as sinif_sube, o.ad_soyad as ogretmen_adi
                        FROM ders_sinif ds
                        JOIN siniflar s ON ds.sinif_id = s.id
                        JOIN ogretmenler o ON ds.ogretmen_id = o.id
                        WHERE ds.id = ?
                    """, (iliski_id,))
                    
                    iliski = self.db.fetchone()
                    
                    # Değerleri ayarla
                    sinif_var.set(f"{iliski['sinif_adi']} {iliski['sinif_sube']}")
                    ogretmen_var.set(iliski["ogretmen_adi"])
                    haftalik_saat_var.set(iliski["haftalik_saat"])
                    
                    # İlişki ID'sini sakla
                    dialog.iliski_id = iliski_id
                except Exception as e:
                    self.logger.error(f"İlişki bilgileri yükleme hatası: {str(e)}")
                    messagebox.showerror("Hata", f"İlişki bilgileri yüklenirken bir hata oluştu:\n{str(e)}")
        
        # Pencereyi ortala
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def save_iliski_dialog(self, dialog, sinif_combobox, ogretmen_combobox, haftalik_saat_var, edit_mode):
        """
        Ders-sınıf-öğretmen ilişkisi ekleme/düzenleme penceresindeki bilgileri kaydeder
        
        Args:
            dialog (tk.Toplevel): Pencere
            sinif_combobox (ttk.Combobox): Sınıf seçim kutusu
            ogretmen_combobox (ttk.Combobox): Öğretmen seçim kutusu
            haftalik_saat_var (tk.IntVar): Haftalık saat değişkeni
            edit_mode (bool): Düzenleme modu
        """
        # Değerleri al
        sinif_adi = sinif_combobox.get()
        ogretmen_adi = ogretmen_combobox.get()
        
        try:
            haftalik_saat = int(haftalik_saat_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Haftalık saat sayısal bir değer olmalıdır.")
            return
        
        # Veri doğrulama
        if not sinif_adi:
            messagebox.showerror("Hata", "Lütfen bir sınıf seçin.")
            return
        
        if not ogretmen_adi:
            messagebox.showerror("Hata", "Lütfen bir öğretmen seçin.")
            return
        
        if haftalik_saat <= 0:
            messagebox.showerror("Hata", "Haftalık saat 0'dan büyük olmalıdır.")
            return
        
        # ID'leri al
        sinif_id = sinif_combobox.sinif_ids.get(sinif_adi)
        ogretmen_id = ogretmen_combobox.ogretmen_ids.get(ogretmen_adi)
        
        try:
            if edit_mode:
                # Mevcut ilişkiyi güncelle
                iliski_id = dialog.iliski_id
                self.db.ders_sinif_iliskisi_guncelle(iliski_id, self.selected_id, sinif_id, ogretmen_id, haftalik_saat)
                messagebox.showinfo("Bilgi", "İlişki başarıyla güncellendi.")
                self.logger.info(f"İlişki güncellendi: Ders ID: {self.selected_id}, Sınıf: {sinif_adi}, Öğretmen: {ogretmen_adi}")
            else:
                # Yeni ilişki ekle
                self.db.ders_sinif_iliskisi_ekle(self.selected_id, sinif_id, ogretmen_id, haftalik_saat)
                messagebox.showinfo("Bilgi", "İlişki başarıyla eklendi.")
                self.logger.info(f"İlişki eklendi: Ders ID: {self.selected_id}, Sınıf: {sinif_adi}, Öğretmen: {ogretmen_adi}")
            
            # İlişki listesini yenile
            self.refresh_iliski_list()
            
            # Pencereyi kapat
            dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            self.logger.error(f"İlişki kaydetme hatası: {str(e)}")
            messagebox.showerror("Hata", f"İlişki kaydedilirken bir hata oluştu:\n{str(e)}")
