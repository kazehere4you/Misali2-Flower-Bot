# 🌸 Flower Bot

Python ile geliştirilmiş, modern arayüze sahip oyun botu.

## 🚀 Özellikler

- 🎮 Otomatik çiçek/nesne toplama
- 💡 Akıllı hedef seçimi
- 🎯 Merkez bölge koruması (80x80 pixel)
- ⌨️ Otomatik E-Q kamera kontrolü
- 📩 Discord Webhook entegrasyonu
- 🖼️ Modern ve kullanıcı dostu arayüz
- 🔄 Otomatik yeniden deneme sistemi
- 🎯 Çoklu hedef desteği (çiçek, sandık, ağaç)
- ⚡ Yüksek performanslı görüntü tanıma
- 🛡️ Hayalet tıklama koruması

## 📋 Gereksinimler

- Python 3.10+
- PIL (Pillow)
- Tkinter (Python ile birlikte gelir)
- Requests

## 🛠️ Kurulum

1. Python 3.10 veya üstünü yükleyin
2. Gerekli kütüphaneleri yükleyin:
```bash
pip install pillow requests
```
3. Projeyi indirin ve klasöre çıkarın
4. `start.py` dosyasını yönetici olarak çalıştırın

## 📝 Kullanım

1. Botu başlatın
2. Hedef pencereyi seçin
3. Ayarları yapılandırın
4. Başlat butonuna tıklayın

## ⚙️ Ayarlar

- **Maksimum Deneme:** En fazla başarısız deneme sayısı
- **Ot Bekleme Süresi:** Ot toplama için bekleme süresi
- **Can Bekleme Süresi:** Can yenileme için bekleme süresi
- **Kara Liste Süresi:** Başarısız hedeflerin kara listede kalma süresi
- **Hedef Tipi:** Toplanacak nesne tipi (çiçek, sandık, ağaç)

## 🔧 Gelişmiş Özellikler

### Merkez Bölge Koruması
- 80x80 pixel korumalı alan
- Hayalet tıklamaları engeller
- Sıkışma durumunda otomatik kamera ayarı

### Hedef Seçimi
- Akıllı öncelik sistemi
- Başarısız hedefler için kara liste yönetimi
- Yapılandırılabilir otomatik yeniden deneme

### Performans Optimizasyonu
- Verimli görüntü işleme
- Bellek yönetimi
- Thread-safe loglama

## 🖥️ Arayüz

Modern arayüz şunları içerir:
- Gerçek zamanlı istatistikler
- Durum göstergeleri
- İlerleme takibi
- Ayar panelleri
- Log görüntüleyici
- Discord entegrasyon ayarları

## 📊 İstatistik Takibi

Takip edilen veriler:
- Oturum süresi
- Başarılı tıklamalar
- Başarısız denemeler
- Bulunan toplam nesne
- Doğrulanmış toplamalar

## ⚠️ Önemli Notlar

- Yönetici hakları gereklidir
- Templates/message/ klasörüne mesaj kutusu görüntüleri ekleyebilirsiniz
- Kara liste sadece başarılı toplamada temizlenir
- Birden fazla oyun penceresi desteklenir
- Otomatik pencere algılama

## 🔍 Teknik Detaylar

- Python 3.10+ ile yazılmıştır
- Arayüz için Tkinter kullanır
- Görüntü işleme için PIL
- Thread-safe operasyon
- Olay tabanlı mimari
- Modüler tasarım

## 🔧 Sorun Giderme

### Sık Karşılaşılan Sorunlar
- Pencere algılanmıyor: Yönetici olarak çalıştırın
- Hedef bulunamıyor: Templates klasörünü kontrol edin
- Performans sorunları: Bekleme sürelerini ayarlayın
- Discord bildirimleri: Webhook URL'sini doğrulayın

### Performans İpuçları
- Templates klasörünü düzenli tutun
- Düzenli önbellek temizliği yapın
- Optimum bekleme süreleri ayarlayın
- Doğru pencere seçimi yapın

---

❤️ kazehere4you discord üzerinden iletişime geçebilirsiniz keyifli incelemeler!