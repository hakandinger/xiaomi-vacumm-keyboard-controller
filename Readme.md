# Xiaomi Vacuum Keyboard Controller

**Xiaomi STYTJ02YM Model robot süpürgesini bilgisayar klavyesi üzerinden kontrol etmek için geliştirilmiş bir proje.**

Bu proje, Xiaomi robot süpürgesini yerel ağ üzerinden kontrol etmeyi ve klavye girdileriyle manuel yönlendirmeyi amaçlar. Özellikle robot süpürgesini bilgisayar üzerinden daha pratik şekilde yönetmek ve cihazla doğrudan iletişim kurmayı denemek isteyenler için geliştirilmiştir.

> ⚠️ **Not:** Proje geliştirme aşamasındadır. Cihaz uyumluluğu ve bağlantı kararlılığı kullanılan modele, ağ yapılandırmasına ve yazılım sürümlerine göre değişebilir.

## ✨ Özellikler

- ⌨️ Klavye üzerinden manuel kontrol
- 📡 Yerel ağ üzerinden cihazla iletişim
- 🤖 Xiaomi robot süpürgeleriyle kontrol denemeleri
- 🔧 Python ve `python-miio` kütüphanesiyle cihaz iletişimi
- 🛠️ Bağlantı sorunlarını inceleme ve hata ayıklama çalışmaları

## 🖥️ Kullanılan Teknolojiler

- Python
- [python-miio](https://github.com/aholstenson/miio)
- Yerel ağ iletişimi
- Klavye girdisiyle kontrol

## 🤖 Test Edilen Cihaz

- **Model:** Xiaomi Viomi Vacuum STYTJ02YM

Diğer Xiaomi veya Viomi tabanlı robot süpürgelerde çalışması garanti edilmez.

## ⚙️ Gereksinimler

- Python 3
- Aynı yerel ağa bağlı bilgisayar ve robot süpürge
- Cihazın IP adresi
- Cihazla iletişim kurmak için gerekli yetkilendirme bilgileri
- Projenin kullandığı Python bağımlılıkları

## 🚀 Kurulum

### 1. Repoyu klonlayın

```bash
git clone https://github.com/hakandinger/xiaomi-vacumm-keyboard-controller.git
cd xiaomi-vacumm-keyboard-controller
```

### 2. Sanal ortam oluşturun

macOS ve Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Bağımlılıkları yükleyin

Projede `requirements.txt` dosyası bulunuyorsa:

```bash
pip install -r requirements.txt
```

Bu dosya yoksa projenin kullandığı bağımlılıkları ayrıca yüklemeniz gerekir.

### 4. Cihaz bağlantısını yapılandırın

Robot süpürgenin IP adresini ve gerekli bağlantı bilgilerini projenin yapılandırmasına girin. Gerçek yapılandırma yöntemi kullanılan kod dosyalarına bağlıdır.

export MIIO_IP=Robotip
export MIIO_TOKEN=Robottoken

### 5. Projeyi çalıştırın

Çalıştırma komutu, projenin ana Python dosyasına göre belirlenmelidir.

Örneğin:

```bash
python keyboard_controller.py
```

## 🔐 Güvenlik

- Cihaz token'ınızı, parolanızı veya diğer gizli bilgilerinizi GitHub'da paylaşmayın.
- Hassas bilgileri kaynak koduna doğrudan yazmak yerine güvenli yapılandırma yöntemleri kullanın.
- Cihaz kontrolünü yalnızca erişim izniniz olan ağlarda gerçekleştirin.
- Bağlantı bilgilerini paylaşmadan önce Git geçmiş

## 🙏 Teşekkür

Bu projeyi geliştirirken ilham aldığım ve çalışmalarından faydalandığım orijinal projenin geliştiricisine teşekkür ederim.

Açık kaynak topluluğunun bilgi paylaşımı ve katkıları, bu projenin ortaya çıkmasına yardımcı olmuştur.

- **İlham alınan proje:** robot-vacuum-joystick-controller (https://github.com/Niyazicancinkir/robot-vacuum-joystick-controller)
- **Geliştirici:** @Niyazicancinkir (https://github.com/Niyazicancinkir)

Bu çalışma, kendi cihazım ve kullanım ihtiyaçlarım doğrultusunda yaptığım uyarlamaları ve geliştirmeleri içermektedir.
