#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yapılandırma yönetimi sınıfı
"""

import os
import json
import logging
from pathlib import Path

class Config:
    """
    Uygulama yapılandırma yönetimi sınıfı
    """
    
    def __init__(self, config_file=None):
        """
        Yapılandırma dosyasını yükler
        
        Args:
            config_file (str, optional): Yapılandırma dosyası yolu. Defaults to None.
        """
        self.logger = logging.getLogger(__name__)
        
        # Varsayılan yapılandırma dosyası yolu
        if config_file is None:
            self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
        else:
            self.config_file = config_file
        
        # Varsayılan yapılandırma
        self.config = {
            'database': {
                'path': os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'ders_programi.db')
            },
            'app': {
                'title': 'Ders Programı Oluşturma Uygulaması',
                'theme': 'clam',
                'language': 'tr'
            },
            'schedule': {
                'lesson_duration': 40,  # dakika
                'break_duration': 10,   # dakika
                'start_time': '08:30',
                'end_time': '16:00',
                'lunch_break_start': '12:00',
                'lunch_break_end': '13:00',
                'max_daily_lessons': 8,
                'max_weekly_lessons': 40,
                'days': ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
            },
            'export': {
                'default_format': 'pdf',
                'pdf_page_size': 'A4',
                'pdf_orientation': 'landscape'
            }
        }
        
        # Yapılandırma dosyasını yükle
        self.load()
    
    def load(self):
        """
        Yapılandırma dosyasını yükler
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Yüklenen yapılandırmayı mevcut yapılandırma ile birleştir
                    self._merge_config(self.config, loaded_config)
                    self.logger.info(f"Yapılandırma dosyası yüklendi: {self.config_file}")
            else:
                # Yapılandırma dosyası yoksa oluştur
                self.save()
                self.logger.info(f"Yapılandırma dosyası oluşturuldu: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Yapılandırma dosyası yüklenirken hata oluştu: {str(e)}")
    
    def save(self):
        """
        Yapılandırma dosyasını kaydeder
        """
        try:
            # Dizin yoksa oluştur
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                self.logger.info(f"Yapılandırma dosyası kaydedildi: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Yapılandırma dosyası kaydedilirken hata oluştu: {str(e)}")
    
    def get(self, section, key=None, default=None):
        """
        Yapılandırma değerini döndürür
        
        Args:
            section (str): Bölüm adı
            key (str, optional): Anahtar adı. Defaults to None.
            default (any, optional): Varsayılan değer. Defaults to None.
            
        Returns:
            any: Yapılandırma değeri
        """
        try:
            if key is None:
                return self.config.get(section, default)
            else:
                return self.config.get(section, {}).get(key, default)
        except Exception as e:
            self.logger.error(f"Yapılandırma değeri alınırken hata oluştu: {str(e)}")
            return default
    
    def set(self, section, key, value):
        """
        Yapılandırma değerini ayarlar
        
        Args:
            section (str): Bölüm adı
            key (str): Anahtar adı
            value (any): Değer
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            self.save()
            return True
        except Exception as e:
            self.logger.error(f"Yapılandırma değeri ayarlanırken hata oluştu: {str(e)}")
            return False
    
    def _merge_config(self, target, source):
        """
        İki yapılandırma sözlüğünü birleştirir
        
        Args:
            target (dict): Hedef sözlük
            source (dict): Kaynak sözlük
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
