# Ders Programı Oluşturma Uygulaması - Test Planı

## 1. Veritabanı Testleri

- [x] Veritabanı bağlantısı kurulabiliyor mu?
- [x] Tablolar doğru şekilde oluşturuluyor mu?
- [x] CRUD işlemleri (ekleme, okuma, güncelleme, silme) doğru çalışıyor mu?
- [x] İlişkisel veri bütünlüğü korunuyor mu?
- [x] Ayarlar doğru şekilde saklanıyor ve alınabiliyor mu?

## 2. Veri Yönetimi Modülleri Testleri

### 2.1 Sınıf Yönetimi
- [x] Sınıf ekleme işlemi çalışıyor mu?
- [x] Sınıf düzenleme işlemi çalışıyor mu?
- [x] Sınıf silme işlemi çalışıyor mu?
- [x] Sınıf listeleme ve filtreleme işlemleri çalışıyor mu?

### 2.2 Öğretmen Yönetimi
- [x] Öğretmen ekleme işlemi çalışıyor mu?
- [x] Öğretmen düzenleme işlemi çalışıyor mu?
- [x] Öğretmen silme işlemi çalışıyor mu?
- [x] Öğretmen listeleme ve filtreleme işlemleri çalışıyor mu?
- [x] Öğretmen uygun olmayan zaman tanımlama işlemi çalışıyor mu?

### 2.3 Ders Yönetimi
- [x] Ders ekleme işlemi çalışıyor mu?
- [x] Ders düzenleme işlemi çalışıyor mu?
- [x] Ders silme işlemi çalışıyor mu?
- [x] Ders listeleme ve filtreleme işlemleri çalışıyor mu?
- [x] Ders-sınıf-öğretmen ilişkilendirme işlemi çalışıyor mu?

### 2.4 Derslik Yönetimi
- [x] Derslik ekleme işlemi çalışıyor mu?
- [x] Derslik düzenleme işlemi çalışıyor mu?
- [x] Derslik silme işlemi çalışıyor mu?
- [x] Derslik listeleme ve filtreleme işlemleri çalışıyor mu?

### 2.5 Kısıt Yönetimi
- [x] Zaman ayarları doğru şekilde kaydediliyor mu?
- [x] Öğretmen kısıtları doğru şekilde kaydediliyor mu?
- [x] Sınıf kısıtları doğru şekilde kaydediliyor mu?
- [x] Derslik kısıtları doğru şekilde kaydediliyor mu?
- [x] Genel kısıtlar doğru şekilde kaydediliyor mu?

## 3. Program Oluşturma Algoritması Testleri

- [x] Algoritma çalışıyor mu?
- [x] Tüm kısıtlar dikkate alınıyor mu?
- [x] Öğretmen uygunluk kısıtları doğru uygulanıyor mu?
- [x] Sınıf çakışma kısıtları doğru uygulanıyor mu?
- [x] Derslik çakışma kısıtları doğru uygulanıyor mu?
- [x] Blok ders kısıtları doğru uygulanıyor mu?
- [x] Öğle arası kısıtları doğru uygulanıyor mu?
- [x] Günlük ve haftalık ders saati kısıtları doğru uygulanıyor mu?
- [x] Algoritma çalışma süresi sınırı doğru uygulanıyor mu?
- [x] Çözüm bulunamadığında uygun hata mesajı veriliyor mu?

## 4. Program Görüntüleme ve Düzenleme Testleri

- [x] Sınıf bazlı program görüntüleme çalışıyor mu?
- [x] Öğretmen bazlı program görüntüleme çalışıyor mu?
- [x] Derslik bazlı program görüntüleme çalışıyor mu?
- [x] Program tablosu doğru şekilde oluşturuluyor mu?
- [x] Ders seçme işlemi çalışıyor mu?
- [x] Ders taşıma işlemi çalışıyor mu?
- [x] Ders silme işlemi çalışıyor mu?
- [x] Çakışma kontrolü ve uyarıları doğru çalışıyor mu?

## 5. Dışa Aktarma ve Yazdırma Testleri

### 5.1 PDF Dışa Aktarma
- [x] Sınıf programı PDF olarak dışa aktarılabiliyor mu?
- [x] Öğretmen programı PDF olarak dışa aktarılabiliyor mu?
- [x] Derslik programı PDF olarak dışa aktarılabiliyor mu?
- [x] Tüm programlar toplu olarak PDF olarak dışa aktarılabiliyor mu?
- [x] PDF dosyaları doğru formatta ve okunabilir mi?

### 5.2 Excel Dışa Aktarma
- [x] Sınıf programı Excel olarak dışa aktarılabiliyor mu?
- [x] Öğretmen programı Excel olarak dışa aktarılabiliyor mu?
- [x] Derslik programı Excel olarak dışa aktarılabiliyor mu?
- [x] Tüm programlar toplu olarak Excel olarak dışa aktarılabiliyor mu?
- [x] Excel dosyaları doğru formatta ve okunabilir mi?

## 6. Entegrasyon Testleri

- [x] Tüm modüller birbirleriyle uyumlu çalışıyor mu?
- [x] Veri yönetimi modüllerindeki değişiklikler program oluşturma algoritmasına yansıyor mu?
- [x] Program oluşturma sonuçları program görüntüleme modülüne doğru aktarılıyor mu?
- [x] Program görüntüleme modülündeki değişiklikler dışa aktarma modülüne yansıyor mu?
- [x] Ayarlar tüm modüllere doğru şekilde uygulanıyor mu?

## 7. Performans Testleri

- [x] Büyük veri setleriyle (50 öğretmen, 20 sınıf) uygulama performansı yeterli mi?
- [x] Program oluşturma algoritması makul sürede çalışıyor mu?
- [x] Arayüz tepki süresi kabul edilebilir mi?
- [x] Dışa aktarma işlemleri makul sürede tamamlanıyor mu?

## 8. Kullanıcı Arayüzü Testleri

- [x] Tüm arayüz bileşenleri doğru görüntüleniyor mu?
- [x] Menüler ve gezinme doğru çalışıyor mu?
- [x] Form doğrulamaları doğru çalışıyor mu?
- [x] Hata mesajları anlaşılır ve yardımcı mı?
- [x] Bilgi mesajları anlaşılır ve yardımcı mı?
- [x] Arayüz tutarlı ve kullanıcı dostu mu?

## 9. Hata Durumu Testleri

- [x] Veritabanı bağlantı hatası durumunda uygun hata mesajı veriliyor mu?
- [x] Veri doğrulama hataları doğru şekilde ele alınıyor mu?
- [x] Program oluşturma hatası durumunda uygun hata mesajı veriliyor mu?
- [x] Dışa aktarma hatası durumunda uygun hata mesajı veriliyor mu?
- [x] Beklenmeyen hatalar doğru şekilde loglama yapılıyor mu?

## 10. Kurulum ve Başlatma Testleri

- [x] Uygulama doğru şekilde başlatılabiliyor mu?
- [x] Gerekli dizinler ve dosyalar otomatik oluşturuluyor mu?
- [x] Loglama sistemi doğru çalışıyor mu?
- [x] Uygulama kapatma işlemi doğru çalışıyor mu?
