#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF dışa aktarma modülü
"""

import os
import logging
from datetime import datetime
import tempfile
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class PDFExporter:
    """
    PDF dışa aktarma sınıfı
    """
    
    def __init__(self, db, config):
        """
        PDF dışa aktarma sınıfını başlatır
        
        Args:
            db (Database): Veritabanı bağlantısı
            config (Config): Yapılandırma
        """
        self.db = db
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Zaman ayarları
        self.load_time_settings()
        
        # Gün adları
        self.gun_adlari = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        
        self.logger.info("PDF dışa aktarma sınıfı başlatıldı")
    
    def load_time_settings(self):
        """
        Zaman ayarlarını yükler
        """
        try:
            # Ders süresi
            self.ders_suresi = int(self.db.ayar_getir("ders_suresi", "40"))
            
            # Teneffüs süresi
            self.teneffus_suresi = int(self.db.ayar_getir("teneffus_suresi", "10"))
            
            # Günlük ders başlangıç saati
            self.baslangic_saati = self.db.ayar_getir("gunluk_ders_baslangic", "08:30")
            
            # Günlük ders bitiş saati
            self.bitis_saati = self.db.ayar_getir("gunluk_ders_bitis", "16:00")
            
            # Öğle arası başlangıç saati
            self.ogle_baslangic = self.db.ayar_getir("ogle_arasi_baslangic", "12:00")
            
            # Öğle arası bitiş saati
            self.ogle_bitis = self.db.ayar_getir("ogle_arasi_bitis", "13:00")
            
            # Maksimum günlük ders saati
            self.max_gunluk_ders = int(self.db.ayar_getir("max_gunluk_ders", "8"))
            
            self.logger.info("Zaman ayarları başarıyla yüklendi")
        except Exception as e:
            self.logger.error(f"Zaman ayarları yüklenirken hata oluştu: {str(e)}")
            raise
    
    def calculate_time(self, period_index, teneffus=False):
        """
        Ders saatini hesaplar
        
        Args:
            period_index (int): Ders indeksi
            teneffus (bool): Teneffüs dahil mi?
            
        Returns:
            str: Saat formatında zaman
        """
        try:
            # Başlangıç saatini parse et
            hour, minute = map(int, self.baslangic_saati.split(":"))
            
            # Toplam dakika
            total_minutes = hour * 60 + minute
            
            # Ders indeksine göre dakika ekle
            if period_index > 0:
                for i in range(period_index):
                    # Ders süresi ekle
                    total_minutes += self.ders_suresi
                    
                    # Teneffüs süresi ekle (son ders için teneffüs eklenmez)
                    if i < period_index - 1 or teneffus:
                        total_minutes += self.teneffus_suresi
            
            # Öğle arası kontrolü
            ogle_baslangic_hour, ogle_baslangic_minute = map(int, self.ogle_baslangic.split(":"))
            ogle_bitis_hour, ogle_bitis_minute = map(int, self.ogle_bitis.split(":"))
            
            ogle_baslangic_minutes = ogle_baslangic_hour * 60 + ogle_baslangic_minute
            ogle_bitis_minutes = ogle_bitis_hour * 60 + ogle_bitis_minute
            
            # Eğer hesaplanan zaman öğle arası içindeyse, öğle arası sonrasına kaydır
            if ogle_baslangic_minutes <= total_minutes < ogle_bitis_minutes:
                total_minutes = ogle_bitis_minutes
            
            # Dakikayı saat ve dakika olarak dönüştür
            hour = total_minutes // 60
            minute = total_minutes % 60
            
            # Saat formatında döndür
            return f"{hour:02d}:{minute:02d}"
        except Exception as e:
            self.logger.error(f"Saat hesaplanırken hata oluştu: {str(e)}")
            return "00:00"
    
    def get_ders_color(self, ders_id):
        """
        Ders ID'sine göre renk döndürür
        
        Args:
            ders_id (int): Ders ID'si
            
        Returns:
            str: Renk kodu
        """
        # Ders ID'sine göre sabit bir renk üret
        colors = [
            "#FFD6D6", "#D6FFD6", "#D6D6FF", "#FFFFD6", "#FFD6FF", "#D6FFFF",
            "#FFE0D6", "#D6FFE0", "#E0D6FF", "#FFFFE0", "#FFE0FF", "#E0FFFF"
        ]
        
        return colors[ders_id % len(colors)]
    
    def export_sinif_programi(self, sinif_id, output_path):
        """
        Sınıf programını PDF olarak dışa aktarır
        
        Args:
            sinif_id (int): Sınıf ID'si
            output_path (str): Çıktı dosya yolu
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Sınıf bilgilerini al
            self.db.execute("SELECT * FROM siniflar WHERE id = ?", (sinif_id,))
            sinif = self.db.fetchone()
            
            if not sinif:
                self.logger.error(f"Sınıf bulunamadı: {sinif_id}")
                return False
            
            # Program verilerini al
            self.db.execute("""
                SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                       o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                       dr.ad as derslik_adi, d.id as ders_id
                FROM program p
                JOIN siniflar s ON p.sinif_id = s.id
                JOIN ogretmenler o ON p.ogretmen_id = o.id
                JOIN dersler d ON p.ders_id = d.id
                JOIN derslikler dr ON p.derslik_id = dr.id
                WHERE p.sinif_id = ?
                ORDER BY p.gun, p.saat
            """, (sinif_id,))
            
            program_verileri = self.db.fetchall()
            
            # Program verilerini gün ve saate göre düzenle
            program_tablosu = {}
            for gun in range(len(self.gun_adlari)):
                program_tablosu[gun] = {}
                for saat in range(self.max_gunluk_ders):
                    program_tablosu[gun][saat] = None
            
            for ders in program_verileri:
                program_tablosu[ders["gun"]][ders["saat"]] = ders
            
            # HTML şablonu oluştur
            html_content = self.create_sinif_programi_html(sinif, program_tablosu)
            
            # PDF oluştur
            font_config = FontConfiguration()
            css = CSS(string=self.get_css(), font_config=font_config)
            
            # Geçici HTML dosyası oluştur
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html.write(html_content.encode('utf-8'))
                temp_html_path = temp_html.name
            
            # HTML'den PDF oluştur
            HTML(filename=temp_html_path).write_pdf(output_path, stylesheets=[css], font_config=font_config)
            
            # Geçici dosyayı sil
            os.unlink(temp_html_path)
            
            self.logger.info(f"Sınıf programı PDF olarak dışa aktarıldı: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Sınıf programı dışa aktarılırken hata oluştu: {str(e)}")
            raise
    
    def export_ogretmen_programi(self, ogretmen_id, output_path):
        """
        Öğretmen programını PDF olarak dışa aktarır
        
        Args:
            ogretmen_id (int): Öğretmen ID'si
            output_path (str): Çıktı dosya yolu
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Öğretmen bilgilerini al
            self.db.execute("SELECT * FROM ogretmenler WHERE id = ?", (ogretmen_id,))
            ogretmen = self.db.fetchone()
            
            if not ogretmen:
                self.logger.error(f"Öğretmen bulunamadı: {ogretmen_id}")
                return False
            
            # Program verilerini al
            self.db.execute("""
                SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                       o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                       dr.ad as derslik_adi, d.id as ders_id
                FROM program p
                JOIN siniflar s ON p.sinif_id = s.id
                JOIN ogretmenler o ON p.ogretmen_id = o.id
                JOIN dersler d ON p.ders_id = d.id
                JOIN derslikler dr ON p.derslik_id = dr.id
                WHERE p.ogretmen_id = ?
                ORDER BY p.gun, p.saat
            """, (ogretmen_id,))
            
            program_verileri = self.db.fetchall()
            
            # Program verilerini gün ve saate göre düzenle
            program_tablosu = {}
            for gun in range(len(self.gun_adlari)):
                program_tablosu[gun] = {}
                for saat in range(self.max_gunluk_ders):
                    program_tablosu[gun][saat] = None
            
            for ders in program_verileri:
                program_tablosu[ders["gun"]][ders["saat"]] = ders
            
            # HTML şablonu oluştur
            html_content = self.create_ogretmen_programi_html(ogretmen, program_tablosu)
            
            # PDF oluştur
            font_config = FontConfiguration()
            css = CSS(string=self.get_css(), font_config=font_config)
            
            # Geçici HTML dosyası oluştur
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html.write(html_content.encode('utf-8'))
                temp_html_path = temp_html.name
            
            # HTML'den PDF oluştur
            HTML(filename=temp_html_path).write_pdf(output_path, stylesheets=[css], font_config=font_config)
            
            # Geçici dosyayı sil
            os.unlink(temp_html_path)
            
            self.logger.info(f"Öğretmen programı PDF olarak dışa aktarıldı: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Öğretmen programı dışa aktarılırken hata oluştu: {str(e)}")
            raise
    
    def export_derslik_programi(self, derslik_id, output_path):
        """
        Derslik programını PDF olarak dışa aktarır
        
        Args:
            derslik_id (int): Derslik ID'si
            output_path (str): Çıktı dosya yolu
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Derslik bilgilerini al
            self.db.execute("SELECT * FROM derslikler WHERE id = ?", (derslik_id,))
            derslik = self.db.fetchone()
            
            if not derslik:
                self.logger.error(f"Derslik bulunamadı: {derslik_id}")
                return False
            
            # Program verilerini al
            self.db.execute("""
                SELECT p.*, s.ad as sinif_adi, s.sube as sinif_sube, 
                       o.ad_soyad as ogretmen_adi, d.ad as ders_adi, 
                       dr.ad as derslik_adi, d.id as ders_id
                FROM program p
                JOIN siniflar s ON p.sinif_id = s.id
                JOIN ogretmenler o ON p.ogretmen_id = o.id
                JOIN dersler d ON p.ders_id = d.id
                JOIN derslikler dr ON p.derslik_id = dr.id
                WHERE p.derslik_id = ?
                ORDER BY p.gun, p.saat
            """, (derslik_id,))
            
            program_verileri = self.db.fetchall()
            
            # Program verilerini gün ve saate göre düzenle
            program_tablosu = {}
            for gun in range(len(self.gun_adlari)):
                program_tablosu[gun] = {}
                for saat in range(self.max_gunluk_ders):
                    program_tablosu[gun][saat] = None
            
            for ders in program_verileri:
                program_tablosu[ders["gun"]][ders["saat"]] = ders
            
            # HTML şablonu oluştur
            html_content = self.create_derslik_programi_html(derslik, program_tablosu)
            
            # PDF oluştur
            font_config = FontConfiguration()
            css = CSS(string=self.get_css(), font_config=font_config)
            
            # Geçici HTML dosyası oluştur
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_html:
                temp_html.write(html_content.encode('utf-8'))
                temp_html_path = temp_html.name
            
            # HTML'den PDF oluştur
            HTML(filename=temp_html_path).write_pdf(output_path, stylesheets=[css], font_config=font_config)
            
            # Geçici dosyayı sil
            os.unlink(temp_html_path)
            
            self.logger.info(f"Derslik programı PDF olarak dışa aktarıldı: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Derslik programı dışa aktarılırken hata oluştu: {str(e)}")
            raise
    
    def export_tum_sinif_programlari(self, output_dir):
        """
        Tüm sınıf programlarını PDF olarak dışa aktarır
        
        Args:
            output_dir (str): Çıktı dizini
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Sınıfları al
            self.db.execute("SELECT * FROM siniflar ORDER BY ad, sube")
            siniflar = self.db.fetchall()
            
            if not siniflar:
                self.logger.error("Hiç sınıf bulunamadı")
                return False
            
            # Her sınıf için PDF oluştur
            for sinif in siniflar:
                output_path = os.path.join(output_dir, f"sinif_programi_{sinif['ad']}_{sinif['sube']}.pdf")
                self.export_sinif_programi(sinif["id"], output_path)
            
            self.logger.info(f"Tüm sınıf programları PDF olarak dışa aktarıldı: {output_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Tüm sınıf programları dışa aktarılırken hata oluştu: {str(e)}")
            raise
    
    def export_tum_ogretmen_programlari(self, output_dir):
        """
        Tüm öğretmen programlarını PDF olarak dışa aktarır
        
        Args:
            output_dir (str): Çıktı dizini
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Öğretmenleri al
            self.db.execute("SELECT * FROM ogretmenler ORDER BY ad_soyad")
            ogretmenler = self.db.fetchall()
            
            if not ogretmenler:
                self.logger.error("Hiç öğretmen bulunamadı")
                return False
            
            # Her öğretmen için PDF oluştur
            for ogretmen in ogretmenler:
                output_path = os.path.join(output_dir, f"ogretmen_programi_{ogretmen['ad_soyad'].replace(' ', '_')}.pdf")
                self.export_ogretmen_programi(ogretmen["id"], output_path)
            
            self.logger.info(f"Tüm öğretmen programları PDF olarak dışa aktarıldı: {output_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Tüm öğretmen programları dışa aktarılırken hata oluştu: {str(e)}")
            raise
    
    def export_tum_derslik_programlari(self, output_dir):
        """
        Tüm derslik programlarını PDF olarak dışa aktarır
        
        Args:
            output_dir (str): Çıktı dizini
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # Derslikleri al
            self.db.execute("SELECT * FROM derslikler ORDER BY ad")
            derslikler = self.db.fetchall()
            
            if not derslikler:
                self.logger.error("Hiç derslik bulunamadı")
                return False
            
            # Her derslik için PDF oluştur
            for derslik in derslikler:
                output_path = os.path.join(output_dir, f"derslik_programi_{derslik['ad'].replace(' ', '_')}.pdf")
                self.export_derslik_programi(derslik["id"], output_path)
            
            self.logger.info(f"Tüm derslik programları PDF olarak dışa aktarıldı: {output_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Tüm derslik programları dışa aktarılırken hata oluştu: {str(e)}")
            raise
    
    def create_sinif_programi_html(self, sinif, program_tablosu):
        """
        Sınıf programı için HTML şablonu oluşturur
        
        Args:
            sinif (dict): Sınıf bilgileri
            program_tablosu (dict): Program tablosu
            
        Returns:
            str: HTML içeriği
        """
        # Başlık ve üst bilgi
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Sınıf Programı - {sinif['ad']} {sinif['sube']}</title>
        </head>
        <body>
            <div class="header">
                <h1>Sınıf Programı</h1>
                <h2>{sinif['ad']} {sinif['sube']}</h2>
                <p>Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Saat / Gün</th>
        """
        
        # Gün başlıkları
        for gun_adi in self.gun_adlari:
            html += f"<th>{gun_adi}</th>"
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        # Ders saatleri ve program
        for saat in range(self.max_gunluk_ders):
            saat_baslangic = self.calculate_time(saat)
            saat_bitis = self.calculate_time(saat + 1, teneffus=True)
            
            html += f"""
                    <tr>
                        <td class="time-cell">{saat+1}. Ders<br>{saat_baslangic}-{saat_bitis}</td>
            """
            
            # Her gün için
            for gun in range(len(self.gun_adlari)):
                ders = program_tablosu[gun][saat]
                
                if ders:
                    # Ders rengi
                    bg_color = self.get_ders_color(ders["ders_id"])
                    
                    html += f"""
                        <td class="lesson-cell" style="background-color: {bg_color}">
                            <div class="lesson-name">{ders['ders_adi']}</div>
                            <div class="teacher-name">{ders['ogretmen_adi']}</div>
                            <div class="classroom-name">{ders['derslik_adi']}</div>
                        </td>
                    """
                else:
                    html += """
                        <td class="empty-cell"></td>
                    """
            
            html += """
                    </tr>
            """
        
        # HTML'i tamamla
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def create_ogretmen_programi_html(self, ogretmen, program_tablosu):
        """
        Öğretmen programı için HTML şablonu oluşturur
        
        Args:
            ogretmen (dict): Öğretmen bilgileri
            program_tablosu (dict): Program tablosu
            
        Returns:
            str: HTML içeriği
        """
        # Başlık ve üst bilgi
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Öğretmen Programı - {ogretmen['ad_soyad']}</title>
        </head>
        <body>
            <div class="header">
                <h1>Öğretmen Programı</h1>
                <h2>{ogretmen['ad_soyad']}</h2>
                <p>Branş: {ogretmen['brans']}</p>
                <p>Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Saat / Gün</th>
        """
        
        # Gün başlıkları
        for gun_adi in self.gun_adlari:
            html += f"<th>{gun_adi}</th>"
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        # Ders saatleri ve program
        for saat in range(self.max_gunluk_ders):
            saat_baslangic = self.calculate_time(saat)
            saat_bitis = self.calculate_time(saat + 1, teneffus=True)
            
            html += f"""
                    <tr>
                        <td class="time-cell">{saat+1}. Ders<br>{saat_baslangic}-{saat_bitis}</td>
            """
            
            # Her gün için
            for gun in range(len(self.gun_adlari)):
                ders = program_tablosu[gun][saat]
                
                if ders:
                    # Ders rengi
                    bg_color = self.get_ders_color(ders["ders_id"])
                    
                    html += f"""
                        <td class="lesson-cell" style="background-color: {bg_color}">
                            <div class="lesson-name">{ders['ders_adi']}</div>
                            <div class="class-name">{ders['sinif_adi']} {ders['sinif_sube']}</div>
                            <div class="classroom-name">{ders['derslik_adi']}</div>
                        </td>
                    """
                else:
                    html += """
                        <td class="empty-cell"></td>
                    """
            
            html += """
                    </tr>
            """
        
        # HTML'i tamamla
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def create_derslik_programi_html(self, derslik, program_tablosu):
        """
        Derslik programı için HTML şablonu oluşturur
        
        Args:
            derslik (dict): Derslik bilgileri
            program_tablosu (dict): Program tablosu
            
        Returns:
            str: HTML içeriği
        """
        # Başlık ve üst bilgi
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Derslik Programı - {derslik['ad']}</title>
        </head>
        <body>
            <div class="header">
                <h1>Derslik Programı</h1>
                <h2>{derslik['ad']}</h2>
                <p>Tür: {derslik['tur']}</p>
                <p>Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Saat / Gün</th>
        """
        
        # Gün başlıkları
        for gun_adi in self.gun_adlari:
            html += f"<th>{gun_adi}</th>"
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        # Ders saatleri ve program
        for saat in range(self.max_gunluk_ders):
            saat_baslangic = self.calculate_time(saat)
            saat_bitis = self.calculate_time(saat + 1, teneffus=True)
            
            html += f"""
                    <tr>
                        <td class="time-cell">{saat+1}. Ders<br>{saat_baslangic}-{saat_bitis}</td>
            """
            
            # Her gün için
            for gun in range(len(self.gun_adlari)):
                ders = program_tablosu[gun][saat]
                
                if ders:
                    # Ders rengi
                    bg_color = self.get_ders_color(ders["ders_id"])
                    
                    html += f"""
                        <td class="lesson-cell" style="background-color: {bg_color}">
                            <div class="lesson-name">{ders['ders_adi']}</div>
                            <div class="class-name">{ders['sinif_adi']} {ders['sinif_sube']}</div>
                            <div class="teacher-name">{ders['ogretmen_adi']}</div>
                        </td>
                    """
                else:
                    html += """
                        <td class="empty-cell"></td>
                    """
            
            html += """
                    </tr>
            """
        
        # HTML'i tamamla
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def get_css(self):
        """
        PDF için CSS stillerini döndürür
        
        Returns:
            str: CSS içeriği
        """
        return """
        @page {
            size: A4 landscape;
            margin: 1cm;
        }
        
        body {
            font-family: "Noto Sans CJK SC", "WenQuanYi Zen Hei", sans-serif;
            font-size: 10pt;
            line-height: 1.3;
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 18pt;
            margin: 0;
        }
        
        .header h2 {
            font-size: 16pt;
            margin: 5px 0;
        }
        
        .header p {
            font-size: 10pt;
            margin: 5px 0;
        }
        
        .schedule-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #000;
        }
        
        .schedule-table th, .schedule-table td {
            border: 1px solid #000;
            padding: 5px;
            text-align: center;
            vertical-align: middle;
        }
        
        .schedule-table th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        
        .time-cell {
            width: 80px;
            font-weight: bold;
            background-color: #f0f0f0;
        }
        
        .lesson-cell {
            height: 60px;
        }
        
        .empty-cell {
            background-color: #ffffff;
        }
        
        .lesson-name {
            font-weight: bold;
            margin-bottom: 3px;
        }
        
        .teacher-name, .class-name, .classroom-name {
            font-size: 9pt;
        }
        """
