🇹🇷 Türkiye Ekonomisi Kıyamet Saati (Doom Watch) ⏳
Bu proje, Türkiye ekonomisindeki olası riskleri çeşitli göstergeler ve halkın genel duyarlılığı üzerinden değerlendiren, basit ama etkili bir risk göstergesi uygulamasıdır. Anlık piyasa verilerini ve haber akışlarını kullanarak güncel ekonomik risk seviyesini görselleştirir.

⚠️ ÖNEMLİ NOT: Bu proje eğitim ve simülasyon amaçlıdır. Finansal kararlar alırken LÜTFEN bu uygulamadaki verilere doğrudan güvenmeyin. Piyasa koşulları sürekli değişir ve finansal kararlar uzman tavsiyesi gerektirir.

🚀 Proje Hakkında
"Türkiye Ekonomisi Kıyamet Saati", belirli ekonomik göstergeleri (faiz, enflasyon, işsizlik, döviz volatilitesi vb.) ve özellikle gerçek zamanlı haber akışlarından elde edilen kamu duyarlılığını analiz ederek bir risk skoru hesaplar. Hesaplanan skor, 0 (düşük risk) ile 1 (yüksek risk) arasında bir değer alır ve zaman içindeki seyrini gösteren basit bir grafik ile sunulur.

Temel Özellikler:

📰 RSS Destekli Duygu Analizi: Belirli RSS feed'lerinden (Investing.com, BBC Türkçe, Dünya Bankası) ekonomi haberlerini çeker ve içeriğindeki duygu tonunu (pozitif/negatif) analiz ederek genel piyasa duyarlılığını ölçer.
📈 Risk Skoru Hesaplama: Çeşitli ekonomik parametreleri ağırlıklandırarak birleşik bir risk skoru oluşturur.
📊 Görselleştirme: Risk seviyesini kolay anlaşılır bir çizgi grafik üzerinde gösterir ve risk bölgelerini (düşük, orta, yüksek) belirtir.
🚨 Anlık Uyarılar: Yüksek risk durumlarında (veya BIST'te ani düşüşlerde) Telegram üzerinden bildirim gönderebilir (ayarları yapılması gerekir).
⚙️ Kolay Kullanım Arayüzü: Streamlit ile oluşturulmuş basit web arayüzü sayesinde herkesin kolayca kullanabileceği bir yapıya sahiptir.
🌐 Çok Dilli Destek: Arayüz Türkçe ve İngilizce olarak kullanılabilir.
🛠️ Kurulum
Uygulamayı kendi bilgisayarında çalıştırmak için aşağıdaki adımları sırasıyla takip etmelisin:

Adım 1: Proje Dosyalarını Edinin
Bu projenin tüm Python dosyalarını (örn: doom_watch.py, sentiment.py, streamlit_app.py vb.) tek bir klasöre indirin veya kopyalayın.
Bu klasöre örneğin EkonomiKiyametSaati gibi anlamlı bir isim verin.
Bu klasörün bilgisayarınızdaki yolunu aklınızda tutun (örn: C:\Kullanicilar\KullaniciAdiniz\Belgeler\EkonomiKiyametSaati).
Adım 2: Python Ortamını Hazırlayın
Uygulama Python ile yazılmıştır, bu yüzden bilgisayarınızda Python'ın kurulu olması gerekir.

Python Kurulu mu Kontrol Edin:

Windows: Başlat menüsünden "Komut İstemi"ni (Command Prompt) veya "PowerShell"i açın.
Mac/Linux: "Terminal" uygulamasını açın.
Açılan pencereye python --version yazın ve Enter'a basın.
Eğer Python 3.x.x gibi bir sürüm numarası görüyorsanız, Python kurulu demektir.
Eğer hata veriyorsa, Python'ın resmi web sitesinden (python.org) en son sürümü indirip kurmanız gerekir. Kurulum sırasında "Add Python to PATH" (veya benzeri bir ifade) kutucuğunu işaretlemeyi KESİNLİKLE unutmayın! Bu adım çok önemlidir.
pip Aracını Güncelleyin:

pip, Python kütüphanelerini yüklememizi sağlayan araçtır. Komut İstemi/Terminal'de aşağıdaki komutu çalıştırın:
```bash
python -m pip install --upgrade pip
```
Adım 3: Gerekli Kütüphaneleri Yükleyin
Şimdi uygulamanın çalışması için ihtiyaç duyduğu ek kütüphaneleri yükleyeceğiz.

Proje Klasörüne Gidin: Komut İstemi/Terminal'de, Adım 1'de oluşturduğunuz EkonomiKiyametSaati klasörüne gitmeniz gerekiyor. Bunun için cd (change directory) komutunu kullanın:
```bash
cd C:\Kullanicilar\KullaniciAdiniz\Belgeler\EkonomiKiyametSaati
# Kendi klasör yolunuzu yukarıdaki örnekle değiştirin!
```
Kütüphaneleri Yükleyin: Klasörün içindeyken, aşağıdaki komutu tek bir satırda kopyalayıp Komut İstemi/Terminal'e yapıştırın ve Enter'a basın:
```bash
pip install streamlit pandas numpy matplotlib requests feedparser transformers torch
```
Bu komut, uygulamanın tüm bağımlılıklarını otomatik olarak indirip kuracaktır. İşlem, internet hızınıza bağlı olarak birkaç dakika sürebilir.

### API Anahtarları
Telegram bildirimleri veya OpenAI tabanlı senaryoları kullanmak isterseniz `config.py` dosyasındaki alanları doldurun veya şu ortam değişkenlerini tanımlayın:

```
export TELEGRAM_BOT_TOKEN=YOUR_TOKEN
export TELEGRAM_CHAT_ID=YOUR_CHAT_ID
export OPENAI_API_KEY=YOUR_OPENAI_KEY
```
🚀 Uygulamayı Çalıştırın!
Tebrikler! Artık her şey hazır. Uygulamayı başlatmak için son bir adım kaldı:

Uygulama Başlatma Komutu: Hala EkonomiKiyametSaati klasörünüzün içinde olmanız gerekiyor. Komut İstemi/Terminal'de aşağıdaki komutu yazın ve Enter'a basın:
```bash
streamlit run streamlit_app.py
```
Tarayıcınız Açılacak: Komutu çalıştırdığınızda, varsayılan web tarayıcınız (Chrome, Firefox vb.) otomatik olarak açılacak ve "Türkiye Ekonomisi Kıyamet Saati" uygulaması karşınıza gelecektir.

💡 Uygulamayı Kullanma
Uygulama arayüzü açıldığında:

"Tarih Seç": Simülasyon amaçlı bir tarih seçebilirsiniz.
"Otomotiv Talep Değişimi": Bu alana, 3 aylık otomotiv talebindeki değişimi manuel olarak (örneğin -0.05 veya 0.03 gibi) girebilirsiniz.
"Veriyi Güncelle ve Risk Skorunu Hesapla" Butonu: Bu butona tıkladığınızda uygulama:
Belirtilen RSS feed'lerinden güncel ekonomi haberlerini çekecek ve duygu analizini yapacak.
Diğer ekonomik göstergeleri (şimdilik bazıları simüle edilmiş veya manuel olarak girilmiş) birleştirecek.
Tüm bu verilere dayanarak güncel risk skorunu hesaplayıp ekranda gösterecek.
Risk skorunun zaman içindeki değişimini gösteren bir grafiği sunacak.
Borsa İstanbul'da (BIST-100) ani bir düşüş tespit ederse size uyarı verecektir.
🤝 Katkıda Bulunma
Bu proje açık kaynaklıdır ve GPLv3 Lisansı ile lisanslanmıştır. Kodda gördüğünüz eksiklikleri gidermek, yeni özellikler eklemek veya iyileştirmeler yapmak isterseniz, katkılarınızı memnuniyetle karşılarız!

Hata raporları için Issues bölümünü kullanın.
Kod katkıları için Pull Request (PR) gönderebilirsiniz.
Umarız bu uygulama, Türkiye ekonomisindeki risk algısını anlamanıza yardımcı olur. İyi kullanımlar!
