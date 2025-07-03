#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flower Bot - Başlatıcı Script
"""

import sys
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    # Yönetici hakları kontrolü
    if not is_admin():
        print("🔒 Yönetici hakları gerekli. Yeniden başlatılıyor...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    try:
        print("🌸 Flower Bot başlatılıyor...")
        from gui import FlowerBotGUI
        
        # GUI'yi başlat
        gui = FlowerBotGUI()
        gui.run()
        
    except Exception as e:
        import traceback
        print(f"❌ Hata oluştu: {e}")
        print(traceback.format_exc())
        input("Devam etmek için Enter'a basın...") 