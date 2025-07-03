@echo off
chcp 65001 >nul
title 🌸 Flower Bot - Otomatik Kurulum

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🌸 FLOWER BOT                           ║
echo ║                   Otomatik Kurulum                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Çalışma dizinini ayarla
cd /d "%~dp0"

echo 🎯 Merhaba! Bot'unuzu 3 adımda hazırlayalım...
echo.

echo ┌─────────────────────────────────────────────────────────────┐
echo │                     📋 HAZIRLIK                            │
echo └─────────────────────────────────────────────────────────────┘

:: Python sürüm kontrolü
echo 🔍 Python sürümü kontrol ediliyor...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python bulunamadı! Otomatik kurulum başlatılıyor...
    echo.
    call install_python310.bat
    if %errorLevel% neq 0 (
        echo ❌ Python kurulumu başarısız!
        pause
        exit /b 1
    )
) else (
    :: Python sürümünü kontrol et
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
    echo 📍 Python sürümü: %python_version%
    
    :: Python 3.10.x kontrolü
    echo %python_version% | findstr /r "^3\.10\." >nul
    if %errorLevel% neq 0 (
        echo ⚠️  Bot Python 3.10.x ile test edilmiştir
        echo 💡 Sorun yaşarsanız Python 3.10.6 kurun
        echo.
        echo 🤔 Mevcut sürümle devam etmek ister misiniz?
        echo    [Y] = Devam et    [N] = Python 3.10.6 kur
        set /p choice="Seçiminizi yapın (Y/N): "
        
        if /i "%choice%"=="N" (
            call install_python310.bat
            if %errorLevel% neq 0 exit /b 1
        ) else if not "%choice%"=="Y" if not "%choice%"=="y" (
            echo ❌ Geçersiz seçim! Devam ediliyor...
        )
    ) else (
        echo ✅ Python 3.10.x tespit edildi - Bot ile uyumlu!
    )
)
echo.

echo ┌─────────────────────────────────────────────────────────────┐
echo │                   ⚙️ ADIM 1: KURULUM                       │
echo └─────────────────────────────────────────────────────────────┘

echo 📦 Python paketleri yükleniyor... (Bu biraz sürebilir)
pip install -r requirements.txt --quiet

if %errorLevel% neq 0 (
    echo ❌ Paket kurulumu başarısız!
    echo 💡 Manuel olarak install_requirements.bat çalıştırın
    pause
    exit /b 1
)

echo ✅ Paketler yüklendi!
echo.

echo ┌─────────────────────────────────────────────────────────────┐
echo │                ⚡ ADIM 2: YÖNETİCİ HAKLARI                 │
echo └─────────────────────────────────────────────────────────────┘

:: Admin hakları kontrolü
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 🔄 Yönetici hakları gerekli... Yeniden başlatılıyor...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ✅ Yönetici hakları mevcut!
echo.

echo ┌─────────────────────────────────────────────────────────────┐
echo │                  🚀 ADIM 3: BOT BAŞLATMA                   │
echo └─────────────────────────────────────────────────────────────┘

echo 🔐 Secure Bot başlatılıyor...
echo.

:: Spesifik Python sürümü ile başlat
echo 🐍 Python sürümü seçiliyor...

:: Python 3.10 varsa onu kullan
py -3.10 --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python 3.10 ile başlatılıyor...
    py -3.10 start.py
) else (
    :: Python 3.10 yoksa varsayılan Python'u kullan
    echo ⚠️ Python 3.10 bulunamadı, varsayılan Python ile başlatılıyor...
    python start.py
)

:: Hata kontrolü
if %errorLevel% neq 0 (
    echo.
    echo ❌ Bot başlatılamadı!
    echo.
    echo 🔧 Sorun giderme:
    echo   1. test_system.bat çalıştırın (sorun tespiti için)
    echo   2. TROUBLESHOOTING.md dosyasını okuyun
    echo   3. Destek ile iletişime geçin
    echo.
    pause
) else (
    echo.
    echo ✅ Bot başarıyla tamamlandı!
    timeout /t 2 /nobreak >nul
)

exit /b 