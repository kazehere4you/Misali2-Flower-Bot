@echo off
chcp 65001 >nul
title 📦 Secure Bot Requirements Installer

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║               📦 REQUIREMENTS INSTALLER                     ║
echo ║              Python Dependencies Setup                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Python kontrolü
echo 🔍 Python kontrolü yapılıyor...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python bulunamadı!
    echo.
    echo 💡 Çözüm:
    echo   1. https://python.org adresinden Python indirin
    echo   2. Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
    echo   3. Bu dosyayı tekrar çalıştırın
    echo.
    pause
    exit /b 1
)

echo ✅ Python bulundu
python --version

echo.
echo 📋 requirements.txt kontrolü...
if not exist "requirements.txt" (
    echo ❌ requirements.txt dosyası bulunamadı!
    echo 💡 Bu dosyayı diğer bot dosyalarıyla aynı klasöre koyun
    pause
    exit /b 1
)

echo ✅ requirements.txt bulundu
echo.

echo 🔄 Python paketleri yükleniyor...
echo 💡 Bu işlem birkaç dakika sürebilir...
echo.

:: Requirements'ları kur
pip install -r requirements.txt

if %errorLevel% neq 0 (
    echo.
    echo ❌ Paket kurulumu başarısız!
    echo.
    echo 🔧 Manuel kurulum deneyin:
    echo   pip install --upgrade pip
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Tüm paketler başarıyla kuruldu!
echo.
echo 🎯 Şimdi yapabilecekleriniz:
echo   1. run_as_admin.bat dosyasını çalıştırın
echo   2. License key'inizi girin
echo   3. Secure Bot'u kullanmaya başlayın
echo.
echo 🛡️ İyi kullanımlar!
echo.
pause 