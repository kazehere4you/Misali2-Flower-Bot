#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Combined Flower Bot - Tüm modüller tek dosyada birleştirildi

Orijinal dosyalar: main.py, config.py, template_matcher.py, window_selector.py

"""



# === IMPORTS ===

import threading

import time

import cv2

import numpy as np

from PIL import ImageGrab

import win32gui

import win32con

import ctypes

import sys

import os

import glob

from datetime import datetime

import win32api

import pydirectinput

import random

import shapely.geometry

import pathlib



# YOLOv5 için pathlib düzeltmesi

if sys.platform == "win32":

    pathlib.PosixPath = pathlib.WindowsPath



import torch
import requests
import json



# === CONFIG SETTINGS ===

# Klasör yolları

TEMPLATE_FOLDER = "templates"

CONFIRM_FOLDER = "confirm"

HEALTH_FOLDER = "health"  # Can barı template'leri için yeni klasör

HERB_FOLDER = "herb"      # Ot template'leri için yeni klasör
MESSAGE_FOLDER = "message"  # DM/mesaj kutusunu tespit için yeni klasör

DEBUG_FOLDER = "debug"



# Ekran kararlılık kontrol ayarları

STABILITY_REGION_RATIO = 0.3

STABILITY_THRESHOLD = 1000

STABILITY_CHECK_COUNT = 3

STABILITY_DELAY = 0.1



# Bot ayarları

DEFAULT_MAX_RETRY = 5

CLICK_DELAY = 1.2

BOT_LOOP_DELAY = 0.5

FLOWER_Y_OFFSET = 0.15  # Çiçek tıklama Y-offset oranı



# Ekran ortası blok ayarları

CENTER_BLOCK_ENABLED = True   # Çiçek toplandıktan sonra ekran ortasını blokla
CENTER_NO_CLICK_ZONE = 80     # Merkez no-click zone radius (pixel)
CENTER_BLOCK_DURATION = 0     # Blok süresi (saniye) - 0 = devre dışı, 3 = varsayılan



# Başarılı toplama sonrası ekran ortası kaçınma

AVOID_CENTER_AFTER_SUCCESS = True   # Başarılı toplama sonrası ortayı önceleme

AVOID_CENTER_DURATION = 5           # Ortayı öncelememe süresi (saniye)



# Can barı kontrol ayarları

HEALTH_CHECK_TIMEOUT = 8.0  # Can barı kontrolü için maximum süre (saniye)

HEALTH_CHECK_INTERVAL = 0.2  # Can barı kontrol aralığı (saniye)

HEALTH_MATCH_THRESHOLD = 0.8  # Can barı template eşleşme eşiği



# Ot kontrol ayarları

HERB_CHECK_TIMEOUT = 5.0  # Ot kontrolü için maximum süre (saniye)

HERB_CHECK_INTERVAL = 0.2  # Ot kontrol aralığı (saniye)

HERB_MATCH_THRESHOLD = 0.7  # Ot template eşleşme eşiği (0.8'den 0.7'ye düşürüldü)



# Mesaj kutusı kontrol ayarları
MESSAGE_CHECK_INTERVAL = 3.0  # Mesaj kutusunu kontrol aralığı (saniye)
MESSAGE_MATCH_THRESHOLD = 0.7  # Mesaj kutusunu template eşleşme eşiği (0.8'den 0.7'ye düşürüldü)

# GUI ayarları

GUI_THEME = {

    "dark": {

        "bg": "#2b2b2b",

        "fg": "#ffffff"

    },

    "light": {

        "bg": "#ffffff",  

        "fg": "#000000"

    }

}



# Log ayarları

MAX_LOG_LINES = 1000

LOG_FILE = "bot.log"



# Anti-Detection ayarları

ANTI_DETECTION = {

    "enabled": True,                    # Anti-detection özelliklerini aktif et

    "random_title": True,               # Rastgele pencere başlığı

    "hide_from_taskbar": True,          # Taskbar'dan gizle

    "random_position": True,            # Rastgele pencere pozisyonu

    "stealth_mode": True,              # Genel gizlilik modu

    "human_delays": True,              # İnsan benzeri gecikmeler

    "random_intervals": True,          # Rastgele bot döngü aralıkları

    "fake_process_name": True          # Sahte process ismi

}



# İnsan benzeri davranış ayarları

HUMAN_BEHAVIOR = {

    "min_action_delay": 0.8,           # Minimum eylem arası gecikme

    "max_action_delay": 2.5,           # Maximum eylem arası gecikme

    "random_breaks": True,             # Rastgele molalar

    "break_chance": 0.02,              # Mola verme şansı (%2)

    "break_duration": (5, 15),         # Mola süresi (saniye)

    "mouse_variance": 5,               # Mouse pozisyon varyasyonu (pixel)

}



# Oyun içi UI elementlerinin koordinatları (800x600 pencere için)

UI_COORDINATES = {

    "confirm": {

        "x": 174,

        "y": 54,

        "x2": 353,

        "y2": 69,

        "width": 179,

        "height": 15

    },

    "health": {

        "x": 422,

        "y": 55,

        "x2": 596,

        "y2": 70,

        "width": 174,

        "height": 15

    },

    "minimap": {

        "x": 693,

        "y": 59,

        "x2": 786,

        "y2": 147,

        "width": 93,

        "height": 88

    }

}



# === YOLO MODEL SETUP ===

# YOLOv5 modelini torch.hub ile yükle

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yoloweight/best3.pt')

model.conf = 0.25



TARGET_LABELS = [

    'flower_lv1', 'chest_lv1', 'tree_lv1', 'unreachable',

    'character', 'other_player', 'minimap'

]



# === WINDOW SELECTOR FUNCTIONS ===

def is_valid_window(hwnd):

    """

    Pencerenin geçerli olup olmadığını kontrol et.

    

    Args:

        hwnd: Pencere handle'ı

        

    Returns:

        bool: Pencere geçerliyse True, değilse False

    """

    try:

        # Görünür pencere kontrolü

        if not win32gui.IsWindowVisible(hwnd):

            return False

            

        # Başlık kontrolü

        title = win32gui.GetWindowText(hwnd)

        if not title or title.isspace():

            return False

            

        # Pencere boyutu kontrolü

        rect = win32gui.GetWindowRect(hwnd)

        if rect[0] == rect[2] or rect[1] == rect[3]:  # Sıfır boyutlu pencere

            return False

            

        # Pencere stili kontrolü

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        if not (style & win32con.WS_VISIBLE):

            return False

            

        return True

        

    except Exception:

        return False



def get_visible_windows():

    """Görünür pencereleri listeler"""

    windows = []

    

    def callback(hwnd, windows):

        if win32gui.IsWindowVisible(hwnd):

            try:

                title = win32gui.GetWindowText(hwnd)

                if title:  # Boş başlıkları atla

                    windows.append((title, hwnd))

            except Exception as e:

                print(f"Pencere bilgisi alınamadı: {e}")

        return True

        

    win32gui.EnumWindows(callback, windows)

    return windows



# === TEMPLATE MATCHER FUNCTIONS ===

def find_objects(frame, target_class):

    # BGR formatında olmalı

    if len(frame.shape) == 2 or frame.shape[2] == 1:

        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    else:

        frame_bgr = frame

    results = model(frame_bgr[..., ::-1])  # BGR to RGB

    detected_objects = []

    names = model.names

    for *box, conf, cls_id in results.xyxy[0].tolist():

        label = names[int(cls_id)]

        if label == target_class:

            x1, y1, x2, y2 = map(int, box)

            center_x = (x1 + x2) // 2

            center_y = (y1 + y2) // 2

            width = x2 - x1

            height = y2 - y1

            detected_objects.append(((center_x, center_y), (x1, y1), width, height))

    return detected_objects



def find_flowers(frame):

    return find_objects(frame, 'flower_lv1')



def find_chests(frame):

    return find_objects(frame, 'chest_lv1')



def find_trees(frame):

    return find_objects(frame, 'tree_lv1')



def find_unreachable(frame):

    return find_objects(frame, 'unreachable')



def find_character(frame):

    return find_objects(frame, 'character')



def find_other_player(frame):

    return find_objects(frame, 'other_player')



def find_minimap(frame):

    return find_objects(frame, 'minimap')



def confirm_success(frame, confirm_templates):

    for template in confirm_templates:

        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > 0.8:

            return True

    return False


def detect_message_box(frame, message_templates):

    """

    Mesaj kutusunu tespit eder

    

    Args:

        frame: Ekran görüntüsü

        message_templates: Mesaj kutusu template'leri

        

    Returns:

        bool: Mesaj kutusu tespit edildiyse True

    """

    best_match = 0.0

    for i, template in enumerate(message_templates):

        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, _ = cv2.minMaxLoc(result)

        

        if max_val > best_match:

            best_match = max_val

            

        print(f"📊 Template {i+1}: Match değeri = {max_val:.3f} (Threshold: {MESSAGE_MATCH_THRESHOLD})")

        

        if max_val > MESSAGE_MATCH_THRESHOLD:

            print(f"✅ Template {i+1} eşleşti! Match: {max_val:.3f}")

            return True

    

    print(f"❌ Hiçbir template eşleşmedi. En iyi match: {best_match:.3f}")

    return False



# === UTILITY FUNCTIONS ===

def is_admin():

    try:

        return ctypes.windll.shell32.IsUserAnAdmin()

    except:

        return False


def send_discord_webhook(webhook_url, user_id, message="Oyunda DM mesajı tespit edildi!"):

    """

    Discord webhook'una mesaj gönderir

    

    Args:

        webhook_url (str): Discord webhook URL'i

        user_id (str): Etiketlenecek kullanıcı ID'si  

        message (str): Gönderilecek mesaj

    """

    if not webhook_url or not webhook_url.strip():

        return False

        

    try:

        # Kullanıcıyı etiketle

        mention = f"<@{user_id}>" if user_id and user_id.strip() else ""

        

        # Mesaj içeriği

        content = f"{mention} {message}".strip()

        

        data = {

            "content": content,

            "username": "Game Bot",

            "avatar_url": "https://cdn.discordapp.com/emojis/123456789/game.png"  # İsteğe bağlı

        }

        

        response = requests.post(webhook_url, data=json.dumps(data), 

                               headers={"Content-Type": "application/json"}, 

                               timeout=10)

        

        return response.status_code == 204

        

    except Exception as e:

        print(f"Discord webhook hatası: {e}")

        return False



# === ANTI-DETECTION CLASS ===

class AntiDetection:

    @staticmethod

    def get_random_title():

        """Rastgele sistem benzeri pencere başlığı döner"""

        system_titles = [

            "Windows Security",

            "System Configuration",

            "Windows Update",

            "Device Manager", 

            "Registry Editor",

            "Task Manager",

            "Control Panel",

            "Windows Defender",

            "System Properties",

            "Windows Explorer",

            "Microsoft Edge",

            "Chrome - Google",

            "Notepad",

            "Calculator",

            "Paint"

        ]

        

        random_titles = [

            f"Document{random.randint(1,99)}.txt - Notepad",

            f"Photo{random.randint(1,99)} - Photos",

            f"Video{random.randint(1,99)} - Media Player",

            f"Music{random.randint(1,99)} - Windows Media Player",

            f"Project{random.randint(1,99)} - Visual Studio",

            f"Report{random.randint(1,99)}.docx - Word"

        ]

        

        all_titles = system_titles + random_titles

        return random.choice(all_titles)

    

    @staticmethod

    def set_window_stealth(window):

        """Pencereyi gizli modda ayarlar"""

        try:

            # Taskbar'dan gizle

            window.wm_attributes('-toolwindow', True)

            # Always on top (isteğe bağlı)

            # window.wm_attributes('-topmost', True)

        except:

            pass

    

    @staticmethod

    def randomize_position(window):

        """Pencereyi rastgele pozisyonda aç"""

        try:

            screen_width = window.winfo_screenwidth()

            screen_height = window.winfo_screenheight()

            

            max_x = screen_width - 950  # Pencere genişliği

            max_y = screen_height - 600  # Pencere yüksekliği

            

            x = random.randint(50, max(50, max_x))

            y = random.randint(50, max(50, max_y))

            

            window.geometry(f"950x600+{x}+{y}")

        except:

            pass

    

    @staticmethod

    def get_human_delay():

        """İnsan benzeri rastgele gecikme döner"""

        return random.uniform(0.1, 0.3)

    

    @staticmethod

    def get_human_click_delay():

        """İnsan benzeri tıklama gecikmesi"""

        return random.uniform(0.05, 0.15)

    

    @staticmethod

    def obfuscate_process():

        """Process ismini gizlemeye çalışır"""

        try:

            # Windows API ile process ismini değiştirme (gelişmiş)

            import ctypes

            from ctypes import wintypes

            

            # Basit bir gizleme yöntemi

            fake_names = ["notepad.exe", "chrome.exe", "explorer.exe", "winlogon.exe"]

            fake_name = random.choice(fake_names)

            

            # Bu kısım daha gelişmiş yöntemler gerektirir

            # Şimdilik log'da belirtelim

            return fake_name

        except:

            return "system_process.exe"



# === BOT STATS CLASS ===

class BotStats:

    def __init__(self):

        self.reset_stats()

    

    def reset_stats(self):

        self.successful_clicks = 0

        self.failed_clicks = 0

        self.start_time = None

        self.total_flowers_found = 0

    

    def start_session(self):

        self.start_time = datetime.now()

    

    def get_session_duration(self):

        if self.start_time:

            return str(datetime.now() - self.start_time).split('.')[0]

        return "00:00:00"



# === MAIN FLOWER BOT LOGIC CLASS ===

class FlowerBotLogic:

    def __init__(self):

        self.running = False

        self.selected_hwnd = None

        self.confirm_templates = []

        self.health_templates = []

        self.herb_templates = []
        self.message_templates = []
        self.last_message_check = 0      # Son mesaj kontrolü zamanı
        self.webhook_url = ""            # Discord webhook URL'i
        self.webhook_user_id = ""        # Etiketlenecek kullanıcı ID'si

        self.center_block_until = 0

        self.center_block_box_size = 80  # px (kare için)

        self.avoid_center_until = 0     # Başarılı toplama sonrası ortayı öncelememe

        self.target_type = "flower_lv1"

        self.settings = {

            'max_retry': DEFAULT_MAX_RETRY,

            'herb_timeout': 5.0,

            'health_timeout': 8.0,

            'blacklist_duration': 30

        }

        self.stats = {

            'successful_clicks': 0,

            'failed_clicks': 0,

            'total_flowers_found': 0,

            'herb_success_count': 0

        }

        # E-Q tuş kontrolü için sayaçlar
        self.no_flower_count = 0          # Çiçek bulunamama sayacı
        self.center_zone_block_count = 0  # Center zone'da takılma sayacı
        self.blacklisted_targets = []     # Buglı çiçeklerin blacklist'i: [(x, y, expiry_time), ...]
        self.gui_callbacks = {

            'log': lambda msg: print(msg),

            'update_stats': lambda *args: None

        }

        self.load_templates()



    def load_templates(self):

        try:

            self.confirm_templates = [tpl for tpl in (cv2.imread(file, 0) 

                                    for file in glob.glob(os.path.join(CONFIRM_FOLDER, '*.png'))) 

                                    if tpl is not None]

            self.health_templates = [tpl for tpl in (cv2.imread(file, 0)

                                   for file in glob.glob(os.path.join(HEALTH_FOLDER, '*.png')))

                                   if tpl is not None]

            self.herb_templates = [tpl for tpl in (cv2.imread(file, 0)

                                 for file in glob.glob(os.path.join(HERB_FOLDER, '*.png')))

                                 if tpl is not None]

            

            if not self.confirm_templates:

                raise Exception(f"Doğrulama template dosyaları {CONFIRM_FOLDER} klasöründe bulunamadı")

            if not self.health_templates:

                raise Exception(f"Can barı template dosyaları {HEALTH_FOLDER} klasöründe bulunamadı")

            if not self.herb_templates:

                raise Exception(f"Ot template dosyaları {HERB_FOLDER} klasöründe bulunamadı")
            
            # Mesaj template'leri yükle (isteğe bağlı - yoksa hata verme)
            self.message_templates = [tpl for tpl in (cv2.imread(file, 0)
                                    for file in glob.glob(os.path.join(MESSAGE_FOLDER, '*.png')))
                                    if tpl is not None]
            
            # Debug: Template yükleme yolunu göster
            message_path = os.path.join(MESSAGE_FOLDER, '*.png')
            self.log(f"🔍 Mesaj template'leri arıyor: {message_path}")
            message_files = glob.glob(message_path)
            self.log(f"📂 Bulunan dosyalar: {message_files}")
            
            if self.message_templates:
                self.log(f"✅ {len(self.message_templates)} mesaj template'i yüklendi")
            else:
                self.log(f"⚠️ Mesaj template dosyaları {MESSAGE_FOLDER} klasöründe bulunamadı (isteğe bağlı)")

                

        except Exception as e:

            self.log(f"❌ Template Yükleme Hatası: {str(e)}")

    

    def set_target_window(self, hwnd):

        """Hedef pencereyi ayarlar"""

        self.selected_hwnd = hwnd

        

    def set_target_type(self, target_type):

        """Hedef tipini ayarlar"""

        self.target_type = target_type

        

    def set_settings(self, settings):

        """Bot ayarlarını günceller"""

        self.settings.update(settings)
    
    def set_webhook_settings(self, webhook_url, user_id):
        """Discord webhook ayarlarını günceller"""
        self.webhook_url = webhook_url.strip() if webhook_url else ""
        self.webhook_user_id = user_id.strip() if user_id else ""
        self.log(f"🔗 Webhook ayarları güncellendi: {'Aktif' if self.webhook_url else 'Deaktif'}")

        

    def set_gui_callbacks(self, callbacks):

        """GUI callback fonksiyonlarını ayarlar"""

        self.gui_callbacks.update(callbacks)

        

    def log(self, message):

        """Log mesajı gönderir"""

        self.gui_callbacks['log'](message)

        

    def stop(self):

        """Botu durdurur"""

        self.running = False

    def is_in_center_zone(self, target_x, target_y):
        """Tıklama noktasının center no-click zone içinde olup olmadığını kontrol eder"""
        if not CENTER_BLOCK_ENABLED:
            return False
            
        # Pencere boyutlarını al
        left, top, right, bottom = win32gui.GetWindowRect(self.selected_hwnd)
        window_width = right - left
        window_height = bottom - top
        
        # Pencere ortasını hesapla
        center_x = window_width // 2
        center_y = window_height // 2
        
        # Target koordinatları pencere içi koordinatlara çevir
        relative_x = target_x - left
        relative_y = target_y - top
        
        # Center zone içinde mi kontrol et
        distance = ((relative_x - center_x) ** 2 + (relative_y - center_y) ** 2) ** 0.5
        
        if distance <= CENTER_NO_CLICK_ZONE:
            self.log(f"🚫 Center zone içindeki nesne atlandı: ({relative_x}, {relative_y}), merkeze uzaklık: {distance:.1f}")
            return True
        
        return False

    def clear_blacklist(self):
        """Blacklist'i tamamen temizler (başarılı toplamadan sonra)"""
        cleared_count = len(self.blacklisted_targets)
        self.blacklisted_targets = []
        if cleared_count > 0:
            self.log(f"✅ Blacklist temizlendi ({cleared_count} çiçek kaldırıldı)")

    def add_to_blacklist(self, rel_x, rel_y):
        """Çiçeği blacklist'e ekler (relative koordinatlar)"""
        self.blacklisted_targets.append((rel_x, rel_y))
        self.log(f"🚫 Çiçek blacklist'e eklendi: ({rel_x}, {rel_y}) - başarılı toplama'ya kadar")

    def is_blacklisted(self, global_x, global_y, radius=80):
        """Verilen global koordinatın blacklist'te olup olmadığını kontrol eder"""
        # Global koordinatları relative koordinatlara çevir
        left, top, right, bottom = win32gui.GetWindowRect(self.selected_hwnd)
        rel_x = global_x - left
        rel_y = global_y - top
        
        for bl_rel_x, bl_rel_y in self.blacklisted_targets:
            distance = ((rel_x - bl_rel_x) ** 2 + (rel_y - bl_rel_y) ** 2) ** 0.5
            if distance <= radius:
                return True
        return False

    def blacklist_nearest_flower(self):
        """E-Q attıktan sonra karaktere en yakın çiçeği blacklist'e ekler"""
        try:
            frame = self.get_screen()
            
            # Hedef tipine göre nesneleri tespit et
            if self.target_type == "flower_lv1":
                detected_objects = find_flowers(frame)
            elif self.target_type == "chest_lv1":
                detected_objects = find_chests(frame)
            elif self.target_type == "tree_lv1":
                detected_objects = find_trees(frame)
            
            if not detected_objects:
                return
            
            # Pencere koordinatlarını al
            left, top, right, bottom = win32gui.GetWindowRect(self.selected_hwnd)
            mid_x = (right - left) // 2
            mid_y = (bottom - top) // 2
            
            # En yakın çiçeği bul
            detected_objects.sort(key=lambda rect: (rect[0][0] - mid_x) ** 2 + (rect[0][1] - mid_y) ** 2)
            nearest = detected_objects[0]
            
            # Relative koordinatları al (pencere içi)
            center, pt, w, h = nearest
            rel_x = center[0]
            rel_y = int(center[1] + h * 0.15)
            
            # Blacklist'e ekle (relative koordinatlar)
            self.add_to_blacklist(rel_x, rel_y)
            
        except Exception as e:
            self.log(f"⚠️ Blacklist ekleme hatası: {str(e)}")

        

    def run_loop(self, running_check_func):

        """Ana bot döngüsü - GUI'den çağrılır"""

        self.running = True

        fail_count = 0

        max_retry = self.settings.get('max_retry', 5)

        

        while running_check_func() and self.running:

            try:

                # Anti-Detection: Rastgele molalar

                if (ANTI_DETECTION.get("enabled", False) and 

                    HUMAN_BEHAVIOR.get("random_breaks", False) and 

                    random.random() < HUMAN_BEHAVIOR.get("break_chance", 0.02)):

                    

                    break_time = random.uniform(*HUMAN_BEHAVIOR.get("break_duration", (5, 15)))

                    self.log(f"😴 Rastgele mola: {break_time:.1f} saniye")

                    time.sleep(break_time)

                

                if not self.is_screen_stable():

                    self.log("⏳ Ekran hareketli, tıklama ertelendi...")

                    time.sleep(0.1)

                    continue



                frame = self.get_screen()
                
                # Mesaj kutusunu kontrol et (belirli aralıklarla)
                current_time = time.time()
                if current_time - self.last_message_check >= MESSAGE_CHECK_INTERVAL:
                    self.log(f"🔍 Mesaj kutusu kontrol ediliyor... ({len(self.message_templates)} template yüklü)")
                    if self.message_templates:
                        message_detected = detect_message_box(frame, self.message_templates)
                        if message_detected:
                            self.log("📩 Mesaj kutusu tespit edildi! Discord webhook gönderiliyor...")
                            if self.webhook_url:
                                success = send_discord_webhook(self.webhook_url, self.webhook_user_id)
                                if success:
                                    self.log("✅ Discord webhook başarıyla gönderildi!")
                                else:
                                    self.log("❌ Discord webhook gönderilemedi!")
                            else:
                                self.log("⚠️ Webhook URL boş, mesaj gönderilemedi!")
                        else:
                            self.log("🔍 Mesaj kutusu bulunamadı")
                    else:
                        self.log("⚠️ Mesaj template'leri yüklenmemiş!")
                    self.last_message_check = current_time

                

                # Hedef tipine göre nesneleri tespit et

                if self.target_type == "flower_lv1":

                    detected_objects = find_flowers(frame)

                elif self.target_type == "chest_lv1":

                    detected_objects = find_chests(frame)

                elif self.target_type == "tree_lv1":

                    detected_objects = find_trees(frame)

                

                self.stats['total_flowers_found'] = len(detected_objects)

                

                if not detected_objects:

                    self.no_flower_count += 1
                    self.log(f"🔍 {self.target_type.capitalize()} bulunamadı. ({self.no_flower_count}/10)")
                    
                    # 10 döngüde çiçek bulunamazsa E/Q bas
                    if self.no_flower_count >= 10:
                        self.log("🎯 10 döngüde çiçek bulunamadı, kamera açısı değiştiriliyor...")
                        self.press_camera_key()
                        self.blacklist_nearest_flower()  # E-Q'dan SONRA en yakın çiçeği blacklist'e ekle
                        self.no_flower_count = 0  # Sayacı sıfırla

                    time.sleep(0.1)

                    continue



                # Çiçek bulunduysa sayacı sıfırla
                self.no_flower_count = 0

                left, top, right, bottom = win32gui.GetWindowRect(self.selected_hwnd)

                mid_x = (right - left) // 2

                mid_y = (bottom - top) // 2

                

                # Normal sıralama: yakından uzağa

                detected_objects.sort(key=lambda rect: (rect[0][0] - mid_x) ** 2 + (rect[0][1] - mid_y) ** 2)



                # Center zone ve blacklist kontrolü - uygun olmayan nesneleri atla
                valid_object = None
                for obj in detected_objects:
                    center, pt, w, h = obj
                    temp_target_x = left + center[0]
                    temp_target_y = top + int(center[1] + h * 0.15)
                    
                    # Center zone dışında VE blacklist'te değilse bu nesneyi seç
                    if (not self.is_in_center_zone(temp_target_x, temp_target_y) and 
                        not self.is_blacklisted(temp_target_x, temp_target_y)):
                        valid_object = obj
                        break
                
                # Eğer uygun nesne yoksa (center zone veya blacklist), çok yakında yeniden dene
                if valid_object is None:
                    self.center_zone_block_count += 1
                    self.log(f"⚠️ Uygun nesne yok (center zone/blacklist), bekleniyor... ({self.center_zone_block_count}/7)")
                    
                    # 6-7 defa center zone'da takılırsa E/Q bas
                    if self.center_zone_block_count >= 6:
                        self.log("🎯 Center zone'da 6 defa takıldı, kamera açısı değiştiriliyor...")
                        self.press_camera_key()
                        self.blacklist_nearest_flower()  # E-Q'dan SONRA en yakın çiçeği blacklist'e ekle
                        self.center_zone_block_count = 0  # Sayacı sıfırla
                        
                    time.sleep(0.5)
                    continue
                else:
                    # Valid object bulunduysa center zone sayacını sıfırla
                    self.center_zone_block_count = 0

                center, pt, w, h = valid_object

                target_x = left + center[0]

                target_y = top + int(center[1] + h * 0.15)

                

                # Tıklama yap

                success, msg = self.safe_click(target_x, target_y, w, h)

                self.log(msg)

                time.sleep(0.2)

                

                # Başarı kontrolü

                frame_after = self.get_screen()

                if self.check_click_success(frame_after):

                    if self.check_health_decrease(self.health_templates):

                        herb_result = self.check_herb_appeared(self.herb_templates)

                        if herb_result:

                            self.log("✅ Başarılı toplama!")

                            self.stats['herb_success_count'] += 1
                            # Başarılı toplamadan sonra blacklist'i temizle
                            self.clear_blacklist()

                        self.stats['successful_clicks'] += 1

                        fail_count = 0
                        # Başarılı tıklama sonrası tüm sayaçları sıfırla
                        self.no_flower_count = 0
                        self.center_zone_block_count = 0

                        

                        # GUI'ye istatistikleri güncelle

                        self.gui_callbacks['update_stats'](

                            self.stats['successful_clicks'],

                            self.stats['failed_clicks'],

                            self.stats['total_flowers_found'],

                            self.stats['herb_success_count']

                        )

                    

            except Exception as e:

                self.log(f"❌ Hata oluştu: {str(e)}")

                time.sleep(0.2)

            

    def safe_click(self, x, y, w=None, h=None):

        """Gelişmiş tıklama sistemi - SetCursorPos ve PostMessage kombinasyonu + Anti-Detection"""

        # Windows API sabitleri

        WM_LBUTTONDOWN = 0x0201

        WM_LBUTTONUP = 0x0202

        WM_MOUSEMOVE = 0x0200

        MK_LBUTTON = 0x0001

        

        try:

            # Pencereyi aktif et

            win32gui.SetForegroundWindow(self.selected_hwnd)

            

            # İnsan benzeri rastgele gecikme

            if ANTI_DETECTION.get("enabled", False):

                human_delay = AntiDetection.get_human_delay()

                time.sleep(human_delay)

            else:

                time.sleep(0.2)

            

            # Fareyi hareket ettir (SetCursorPos ile)

            ctypes.windll.user32.SetCursorPos(int(x), int(y))

            

            # İnsan benzeri tıklama gecikmesi

            if ANTI_DETECTION.get("enabled", False):

                click_delay = AntiDetection.get_human_click_delay()

                time.sleep(click_delay)

            else:

                time.sleep(0.2)

            

            # Koordinatları LPARAM formatına çevir

            lParam = win32api.MAKELONG(x, y)

            

            # Sol tıklama mesajlarını gönder

            win32gui.PostMessage(self.selected_hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lParam)

            

            # İnsan benzeri mouse up gecikmesi

            if ANTI_DETECTION.get("enabled", False):

                time.sleep(random.uniform(0.05, 0.12))

            else:

                time.sleep(0.1)

                

            win32gui.PostMessage(self.selected_hwnd, WM_LBUTTONUP, 0, lParam)

            

            # Son gecikme

            if ANTI_DETECTION.get("enabled", False):

                time.sleep(AntiDetection.get_human_delay())

            else:

                time.sleep(0.2)

            

            return True, f"🎯 Tıklama yapıldı: ({x}, {y})"

            

        except Exception as e:

            self.log(f"⚠️ Tıklama hatası: {str(e)}")

            return False, f"❌ Tıklama başarısız: {str(e)}"



    def check_health_decrease(self, health_templates):

        """Can barının değişip değişmediğini kontrol eder"""

        start_time = time.time()

        initial_health = None

        timeout = self.settings.get('health_timeout', 8.0)

        

        # İlk can barı konumunu bul

        frame = self.get_screen()

        for template in health_templates:

            result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > HEALTH_MATCH_THRESHOLD:

                initial_health = max_loc

                break

                

        if not initial_health:

            self.log("⚠️ Can barı bulunamadı!")

            return False

            

        # Can barını kontrol et

        while time.time() - start_time < timeout:

            frame = self.get_screen()

            health_found = False

            

            for template in health_templates:

                result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                

                # Eğer can barı bulunduysa ve değişim varsa

                if max_val > HEALTH_MATCH_THRESHOLD:

                    health_found = True

                    if max_loc != initial_health:

                        self.log(f"✅ Can barı değişimi tespit edildi ({time.time() - start_time:.1f} saniye)")

                        return True

                    break

                    

            if not health_found:

                self.log("✅ Can barı kayboldu, muhtemelen azalıyor")

                return True

                

            time.sleep(HEALTH_CHECK_INTERVAL)

            

        self.log(f"⚠️ Can barı {timeout} saniye içinde değişmedi!")

        self.log("⛔ Can barı azalmıyor, ESC basılıyor...")

        pydirectinput.press("esc")
        
        # Buglı çiçeği atlamak için kamera açısı değiştir
        self.log("🎯 Buglı çiçeği atlamak için kamera açısı değiştiriliyor...")
        self.press_camera_key()
        self.blacklist_nearest_flower()  # E-Q'dan SONRA en yakın çiçeği blacklist'e ekle

        return False



    def check_click_success(self, frame):

        """Tıklama başarılı mı kontrol et"""

        return confirm_success(frame, self.confirm_templates)



    def check_herb_appeared(self, herb_templates):

        """Ekranın sol alt köşesinde ot yazısı var mı kontrol eder"""

        start_time = time.time()

        last_log_time = 0

        timeout = self.settings.get('herb_timeout', 5.0)

        

        while time.time() - start_time < timeout:

            left, top, right, bottom = win32gui.GetWindowRect(self.selected_hwnd)

            region = (left, bottom - 100, left + 400, bottom)

            frame = ImageGrab.grab(bbox=region)

            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2GRAY)



            if not os.path.exists(DEBUG_FOLDER):

                os.makedirs(DEBUG_FOLDER)

            timestamp = int(time.time())

            # cv2.imwrite(f"{DEBUG_FOLDER}/herb_check_{timestamp}.png", frame)  # Debug kaydı devre dışı



            max_ccoeff = 0

            min_sqdiff = 1.0

            found = False

            for template in herb_templates:

                # TM_CCOEFF_NORMED

                result_ccoeff = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

                _, max_val_ccoeff, _, _ = cv2.minMaxLoc(result_ccoeff)

                max_ccoeff = max(max_ccoeff, max_val_ccoeff)

                if max_val_ccoeff > HERB_MATCH_THRESHOLD:

                    self.log(f"✅ Ot tespit edildi! (TM_CCOEFF_NORMED, {max_val_ccoeff:.3f})")

                    found = True

                    break

                # TM_SQDIFF_NORMED

                result_sqdiff = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF_NORMED)

                min_val_sqdiff, _, _, _ = cv2.minMaxLoc(result_sqdiff)

                min_sqdiff = min(min_sqdiff, min_val_sqdiff)

                if min_val_sqdiff < 0.2:

                    self.log(f"✅ Ot tespit edildi! (TM_SQDIFF_NORMED, {min_val_sqdiff:.3f})")

                    found = True

                    break



            if found:

                return True



            # Her 2 saniyede bir log at

            current_time = time.time()

            if current_time - last_log_time >= 2:

                self.log(f"🔍 Ot kontrolü - Max CCOEFF: {max_ccoeff:.3f} (Eşik: {HERB_MATCH_THRESHOLD}), Min SQDIFF: {min_sqdiff:.3f} (Eşik: 0.2)")

                last_log_time = current_time



            time.sleep(HERB_CHECK_INTERVAL)



        self.log(f"⚠️ Ot {timeout} saniye içinde görünmedi!")

        return False



    def press_camera_key(self):

        key = random.choice(["e", "q"])

        hold_time = random.uniform(2.0, 2.5)  # 2.0-2.5 saniye arası

        self.log(f"🎮 {key.upper()} tuşuna {hold_time:.2f} sn basılıyor (kamera açısı değiştir)...")

        pydirectinput.keyDown(key)

        time.sleep(hold_time)

        pydirectinput.keyUp(key)



    def get_screen(self):

        if self.selected_hwnd is None:

            img = ImageGrab.grab()

        else:

            rect = win32gui.GetWindowRect(self.selected_hwnd)

            img = ImageGrab.grab(bbox=rect)

        # BGR'ye çevir ve sonra gri tonlamaya dönüştür

        img_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)  # Gri tonlamaya çevir



    def is_screen_stable(self):

        left, top, right, bottom = win32gui.GetWindowRect(self.selected_hwnd)

        

        # Config'den minimap koordinatlarını al

        minimap = UI_COORDINATES["minimap"]

        

        # Pencere koordinatlarına göre minimap bölgesi

        region = (

            left + minimap["x"],

            top + minimap["y"],

            left + minimap["x"] + minimap["width"],

            top + minimap["y"] + minimap["height"]

        )



        prev_frame = ImageGrab.grab(bbox=region).convert('L')

        prev_np = np.array(prev_frame)



        # Sadece bir kez kontrol et, iki kez değil

        time.sleep(0.3)

        new_frame = ImageGrab.grab(bbox=region).convert('L')

        new_np = np.array(new_frame)

        diff = cv2.absdiff(prev_np, new_np)

        non_zero = cv2.countNonZero(diff)

        

        # Minimap için daha hassas eşik - 1000 piksel değişim eşiği

        if non_zero < 1000:  # Eşiği artırdık

            return True

        else:

            self.log(f"🗺️ Minimap hareketi algılandı: {non_zero} piksel değişti")

            return False







# === MAIN EXECUTION ===

if __name__ == "__main__":

    # Bu dosya artık sadece bot mantığını içeriyor

    # GUI için gui.py dosyasını kullanın

    print("🤖 Bot Core - Bu dosya bot mantığını içerir.")

    print("GUI başlatmak için gui.py dosyasını çalıştırın.")

    print("Launcher ile başlatmak için launcher.py dosyasını kullanın.")

    

    # Test amaçlı bot mantığı oluşturma

    try:

        bot_logic = FlowerBotLogic()

        print("✅ Bot mantığı başarıyla yüklendi.")

        print("📦 Template dosyaları kontrol edildi.")

        print("🔧 Tüm modüller hazır.")

    except Exception as e:

        print(f"❌ Bot mantığı yüklenirken hata: {e}")

        import traceback

        print(traceback.format_exc())

        input("Devam etmek için Enter'a basın...")