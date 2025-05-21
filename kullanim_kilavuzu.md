# Ders Programı Oluşturma Uygulaması - Kullanım Kılavuzu

## İçindekiler

1. [Giriş](#giriş)
2. [Kurulum](#kurulum)
3. [Başlangıç](#başlangıç)
4. [Veri Yönetimi](#veri-yönetimi)
   - [Sınıf Yönetimi](#sınıf-yönetimi)
   - [Öğretmen Yönetimi](#öğretmen-yönetimi)
   - [Ders Yönetimi](#ders-yönetimi)
   - [Derslik Yönetimi](#derslik-yönetimi)
   - [Kısıt Yönetimi](#kısıt-yönetimi)
5. [Program Oluşturma](#program-oluşturma)
6. [Program Görüntüleme ve Düzenleme](#program-görüntüleme-ve-düzenleme)
7. [Dışa Aktarma](#dışa-aktarma)
8. [Sorun Giderme](#sorun-giderme)
9. [Teknik Destek](#teknik-destek)

## Giriş

Ders Programı Oluşturma Uygulaması, lisede görevli 50 öğretmenin ve 20 sınıfın ders programlarını otomatik olarak oluşturan, kullanıcı dostu ve esnek bir masaüstü uygulamasıdır. Bu uygulama, öğretmenlerin branşları, haftalık ders saatleri ve uygunluklarına göre en uygun ders programını oluşturur.

### Temel Özellikler

- Sınıf, öğretmen, ders ve derslik tanımlama
- Öğretmenlerin uygun olmadığı zamanları belirleme
- Kısıtlar dikkate alınarak otomatik program oluşturma
- Oluşturulan programları görüntüleme ve manuel düzenleme
- Programları PDF ve Excel formatlarında dışa aktarma

## Kurulum

### Sistem Gereksinimleri

- Windows 10/11, macOS 10.14+ veya Linux (Ubuntu 20.04+)
- Python 3.8 veya üzeri
- 4 GB RAM (minimum)
- 500 MB boş disk alanı

### Kurulum Adımları

1. Uygulamanın ZIP dosyasını indirin ve istediğiniz bir konuma çıkarın.
2. Gerekli Python paketlerini yüklemek için terminal veya komut istemcisini açın ve uygulama dizinine gidin:

```bash
cd /path/to/ders_programi_projesi
pip install -r requirements.txt
```

3. Uygulamayı başlatmak için:

```bash
python src/main.py
```

## Başlangıç

Uygulama ilk kez başlatıldığında, boş bir veritabanı oluşturulur. Ders programı oluşturmadan önce, aşağıdaki adımları sırasıyla tamamlamanız gerekmektedir:

1. Sınıfları tanımlayın
2. Öğretmenleri tanımlayın
3. Dersleri tanımlayın
4. Derslikleri tanımlayın
5. Kısıtları ayarlayın
6. Ders-sınıf-öğretmen ilişkilerini tanımlayın
7. Program oluşturun

## Veri Yönetimi

### Sınıf Yönetimi

Sınıf Yönetimi modülü, okulunuzdaki sınıfları tanımlamanızı sağlar.

#### Sınıf Ekleme

1. Ana menüden "Veri Yönetimi" > "Sınıf Yönetimi" seçeneğini tıklayın.
2. "Yeni Sınıf" butonuna tıklayın.
3. Sınıf adını (örn: "9") ve şubesini (örn: "A") girin.
4. "Kaydet" butonuna tıklayın.

#### Sınıf Düzenleme

1. Sınıf listesinden düzenlemek istediğiniz sınıfı seçin.
2. Bilgileri güncelleyin.
3. "Kaydet" butonuna tıklayın.

#### Sınıf Silme

1. Sınıf listesinden silmek istediğiniz sınıfı seçin.
2. "Sil" butonuna tıklayın.
3. Onay iletişim kutusunda "Evet" seçeneğini tıklayın.

### Öğretmen Yönetimi

Öğretmen Yönetimi modülü, okulunuzdaki öğretmenleri ve onların uygunluk durumlarını tanımlamanızı sağlar.

#### Öğretmen Ekleme

1. Ana menüden "Veri Yönetimi" > "Öğretmen Yönetimi" seçeneğini tıklayın.
2. "Yeni Öğretmen" butonuna tıklayın.
3. Ad-Soyad, branş ve haftalık ders saati bilgilerini girin.
4. "Kaydet" butonuna tıklayın.

#### Öğretmen Uygunluk Durumu Tanımlama

1. Öğretmen listesinden bir öğretmen seçin.
2. "Uygun Olmayan Zamanlar" bölümünde "Ekle" butonuna tıklayın.
3. Gün, başlangıç saati ve bitiş saati seçin.
4. "Kaydet" butonuna tıklayın.

### Ders Yönetimi

Ders Yönetimi modülü, okulunuzda verilen dersleri tanımlamanızı ve bu dersleri sınıflara ve öğretmenlere atamanızı sağlar.

#### Ders Ekleme

1. Ana menüden "Veri Yönetimi" > "Ders Yönetimi" seçeneğini tıklayın.
2. "Yeni Ders" butonuna tıklayın.
3. Ders adını ve haftalık ders saatini girin.
4. "Kaydet" butonuna tıklayın.

#### Ders-Sınıf-Öğretmen İlişkisi Ekleme

1. Ders listesinden bir ders seçin.
2. "Ders-Sınıf-Öğretmen İlişkileri" bölümünde "İlişki Ekle" butonuna tıklayın.
3. Sınıf, öğretmen ve haftalık ders saati seçin.
4. "Kaydet" butonuna tıklayın.

### Derslik Yönetimi

Derslik Yönetimi modülü, okulunuzdaki derslikleri tanımlamanızı sağlar.

#### Derslik Ekleme

1. Ana menüden "Veri Yönetimi" > "Derslik Yönetimi" seçeneğini tıklayın.
2. "Yeni Derslik" butonuna tıklayın.
3. Derslik adını girin ve türünü (normal veya özel) seçin.
4. "Kaydet" butonuna tıklayın.

### Kısıt Yönetimi

Kısıt Yönetimi modülü, program oluşturma algoritmasının dikkate alacağı kısıtları ayarlamanızı sağlar.

#### Zaman Ayarları

1. Ana menüden "Veri Yönetimi" > "Kısıt Yönetimi" seçeneğini tıklayın.
2. "Zaman Ayarları" sekmesini seçin.
3. Ders süresi, teneffüs süresi, günlük ders başlangıç ve bitiş saatleri, öğle arası başlangıç ve bitiş saatleri, maksimum günlük ve haftalık ders saati bilgilerini girin.
4. "Ayarları Kaydet" butonuna tıklayın.

#### Öğretmen Kısıtları

1. "Öğretmen Kısıtları" sekmesini seçin.
2. Öğretmen günlük maksimum ve minimum ders saati, öğretmen boş saat tercihi gibi ayarları yapın.
3. "Ayarları Kaydet" butonuna tıklayın.

#### Sınıf Kısıtları

1. "Sınıf Kısıtları" sekmesini seçin.
2. Sınıf günlük maksimum ve minimum ders saati, aynı dersin aynı günde maksimum tekrarı gibi ayarları yapın.
3. "Ayarları Kaydet" butonuna tıklayın.

#### Derslik Kısıtları

1. "Derslik Kısıtları" sekmesini seçin.
2. Özel derslik zorunluluğu, derslik değişim minimizasyonu gibi ayarları yapın.
3. "Ayarları Kaydet" butonuna tıklayın.

#### Genel Kısıtlar

1. "Genel Kısıtlar" sekmesini seçin.
2. Blok ders tercihi, maksimum blok ders sayısı, algoritma çalışma süresi sınırı gibi ayarları yapın.
3. "Ayarları Kaydet" butonuna tıklayın.

## Program Oluşturma

Program Oluşturma modülü, tanımladığınız veriler ve kısıtlar doğrultusunda otomatik olarak ders programı oluşturur.

### Program Oluşturma Adımları

1. Ana menüden "Program" > "Program Oluştur" seçeneğini tıklayın.
2. Bilgileri kontrol edin ve gerekirse algoritma çalışma süresi sınırını ayarlayın.
3. "Program Oluştur" butonuna tıklayın.
4. İşlem tamamlandığında sonuç mesajını görüntüleyin.

**Not:** Program oluşturma işlemi, veri miktarına ve kısıtlara bağlı olarak birkaç dakika sürebilir. İşlem sırasında uygulamayı kapatmayın.

## Program Görüntüleme ve Düzenleme

Program Görüntüleme ve Düzenleme modülü, oluşturulan programları görüntülemenizi ve gerektiğinde manuel düzenlemeler yapmanızı sağlar.

### Program Görüntüleme

1. Ana menüden "Program" > "Program Görüntüle" seçeneğini tıklayın.
2. Görünüm modunu seçin (Sınıf, Öğretmen veya Derslik).
3. Filtre seçeneğinden görüntülemek istediğiniz sınıfı, öğretmeni veya dersliği seçin.
4. Program tablosu otomatik olarak yüklenecektir.

### Program Düzenleme

1. Program tablosunda düzenlemek istediğiniz derse tıklayın.
2. Seçili ders bilgileri alt panelde görüntülenecektir.
3. Dersi taşımak için yeni gün, saat ve derslik seçin, ardından "Dersi Taşı" butonuna tıklayın.
4. Dersi silmek için "Dersi Sil" butonuna tıklayın.

**Not:** Manuel düzenlemeler çakışmalara neden olabilir. Uygulama, çakışma durumunda sizi uyaracaktır.

## Dışa Aktarma

Dışa Aktarma modülü, oluşturulan programları PDF veya Excel formatında dışa aktarmanızı sağlar.

### Program Dışa Aktarma

1. Ana menüden "Program" > "Dışa Aktar" seçeneğini tıklayın.
2. Görünüm modunu seçin (Sınıf, Öğretmen veya Derslik).
3. Dışa aktarmak istediğiniz öğeyi seçin veya "Tümünü Seç" seçeneğini işaretleyin.
4. Dışa aktarma formatını seçin (PDF veya Excel).
5. Çıktı dizinini seçin.
6. "Dışa Aktar" butonuna tıklayın.

## Sorun Giderme

### Sık Karşılaşılan Sorunlar ve Çözümleri

#### Program Oluşturulamıyor

**Sorun:** Program oluşturma işlemi başarısız oluyor veya çözüm bulunamıyor.

**Çözüm:**
1. Kısıtları kontrol edin ve gerekirse bazı kısıtları gevşetin.
2. Öğretmenlerin uygun olmayan zamanlarını kontrol edin.
3. Algoritma çalışma süresi sınırını artırın.
4. Ders-sınıf-öğretmen ilişkilerini kontrol edin.

#### Uygulama Başlatılamıyor

**Sorun:** Uygulama başlatılamıyor veya hata veriyor.

**Çözüm:**
1. Python sürümünüzün 3.8 veya üzeri olduğundan emin olun.
2. Gerekli paketlerin doğru şekilde yüklendiğinden emin olun.
3. Uygulama dizinindeki logs klasöründeki hata günlüklerini kontrol edin.

#### Dışa Aktarma Hatası

**Sorun:** PDF veya Excel dışa aktarma işlemi başarısız oluyor.

**Çözüm:**
1. Çıktı dizininin yazma izinlerine sahip olduğundan emin olun.
2. Dışa aktarılacak programın oluşturulduğundan emin olun.
3. Gerekli paketlerin doğru şekilde yüklendiğinden emin olun.

## Teknik Destek

Teknik destek için lütfen aşağıdaki iletişim bilgilerini kullanın:

- E-posta: destek@dersprogrami.com
- Telefon: +90 (212) 555 1234
- Web: www.dersprogrami.com/destek

Lütfen sorununuzu detaylı bir şekilde açıklayın ve varsa hata mesajlarını ekleyin.
