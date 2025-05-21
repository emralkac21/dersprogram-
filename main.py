#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ana uygulama modülü
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from config import Config
from main_window import MainWindow

def setup_logging():
    """
    Loglama ayarlarını yapılandırır
    """
    # Proje kök dizini
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Log dizini
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Log dosyası
    log_file = os.path.join(log_dir, "ders_programi.log")
    
    # Loglama yapılandırması
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """
    Ana uygulama fonksiyonu
    """
    # Loglama ayarları
    logger = setup_logging()
    logger.info("Uygulama başlatılıyor...")
    
    # Proje kök dizini
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Veritabanı bağlantısı
        db_path = os.path.join(project_root, "data", "ders_programi.db")
        db = Database(db_path)
        logger.info(f"Veritabanı bağlantısı kuruldu: {db_path}")
        
        # Yapılandırma
        config = Config()
        logger.info("Yapılandırma yüklendi")
        
        # Tkinter uygulaması
        root = tk.Tk()
        root.title("Ders Programı Oluşturma Uygulaması")
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        # Ana pencere
        main_window = MainWindow(root, db, config)
        
        # Uygulama simgesi
        try:
            icon_path = os.path.join(project_root, "assets", "icon.ico")
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Uygulama simgesi yüklenemedi: {str(e)}")
        
        # Uygulama kapatıldığında
        def on_closing():
            if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinizden emin misiniz?"):
                logger.info("Uygulama kapatılıyor...")
                db.close()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Uygulamayı başlat
        logger.info("Uygulama arayüzü başlatıldı")
        root.mainloop()
    
    except Exception as e:
        logger.error(f"Uygulama başlatılırken hata oluştu: {str(e)}")
        messagebox.showerror("Hata", f"Uygulama başlatılırken bir hata oluştu:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
