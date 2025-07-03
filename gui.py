#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flower Bot GUI - Ayrılmış GUI bileşenleri
Bot mantığı bot_core.py dosyasında bulunur
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import time
import sys
import os
import random
from datetime import datetime
import queue

# Bot Core import et
try:
    import bot_core
except ImportError as e:
    print(f"❌ Bot core yüklenemedi: {e}")
    print("bot_core.py dosyasının mevcut olduğundan emin olun.")
    sys.exit(1)

class FlowerBotGUI:
    def __init__(self):
        # Bot mantığı instance'ı
        self.bot_logic = bot_core.FlowerBotLogic()
        self.running = False
        self.selected_hwnd = None
        self.stats = bot_core.BotStats()
        self.current_theme = "dark"
        
        # Thread-safe logging için queue
        self.log_queue = queue.Queue()
        
        # GUI setup
        self.setup_gui()
        
        # Log queue işleyicisini başlat
        self.process_log_queue()
    
    def load_logo(self, size=(120, 120)):
        """Logo dosyasını yükle"""
        try:
            if os.path.exists("logo.png"):
                logo_img = Image.open("logo.png")
                logo_img = logo_img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(logo_img)
            elif os.path.exists("assets/logo.png"):
                logo_img = Image.open("assets/logo.png")
                logo_img = logo_img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(logo_img)
        except Exception as e:
            print(f"Logo yüklenemedi: {e}")
        return None
    
    def setup_gui(self):
        self.window = tk.Tk()
        self.target_type = tk.StringVar(value="flower_lv1")
        
        # Pencere başlığı ayarla
        self.window.title("🌸 Flower Bot")
        
        # İlk olarak boyutu ayarla
        self.window.geometry("950x600")
            
        self.window.minsize(900, 500)
        
        # Discordumsu renkler
        discord_bg = "#23272A"
        discord_fg = "#FFFFFF"
        accent = "#5865F2"
        accent2 = "#43B581"
        danger = "#ED4245"
        
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Sidebar.TFrame", background=discord_bg)
        style.configure("Main.TFrame", background="#2C2F33")
        style.configure("Custom.TButton", background=accent, foreground=discord_fg, font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.configure("Custom.TLabel", background=discord_bg, foreground=discord_fg, font=('Segoe UI', 10))
        style.configure("Custom.TLabelframe", background=discord_bg, foreground=accent, font=('Segoe UI', 10, 'bold'))
        style.configure("Custom.TLabelframe.Label", background=discord_bg, foreground=accent)
        style.configure("Accent.TButton", background=accent2, foreground=discord_fg, font=('Segoe UI', 10, 'bold'))
        style.configure("Danger.TButton", background=danger, foreground=discord_fg, font=('Segoe UI', 10, 'bold'))
        
        # Ana container
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (sol)
        sidebar = ttk.Frame(main_container, style="Sidebar.TFrame", width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main area (sağ)
        main_area = ttk.Frame(main_container, style="Main.TFrame")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Logo ve başlık frame
        header_frame = tk.Frame(sidebar, bg=discord_bg)
        header_frame.pack(pady=15)
        
        # Logo
        logo = self.load_logo((80, 80))
        if logo:
            logo_label = tk.Label(header_frame, image=logo, bg=discord_bg)
            logo_label.image = logo  # Reference tutmak için
            logo_label.pack()
        
        # Başlık
        title_label = tk.Label(header_frame, text="🌸 Flower Bot", 
                              font=('Segoe UI', 16, 'bold'), 
                              bg=discord_bg, fg=accent)
        title_label.pack(pady=(5, 0))
        
        # Version
        version_label = tk.Label(header_frame, text="v2.0", 
                                font=('Segoe UI', 10), 
                                bg=discord_bg, fg="#99AAB5")
        version_label.pack()
        
        # Kontrol butonları - Modern flat design
        button_container = tk.Frame(sidebar, bg=discord_bg)
        button_container.pack(pady=10, fill=tk.X, padx=10)
        
        # Başlat butonu
        self.start_btn = tk.Button(button_container, text="▶ Başlat", command=self.start_bot,
                                  bg="#43B581", fg="#FFFFFF", font=('Segoe UI', 12, 'bold'),
                                  relief=tk.FLAT, bd=0, padx=30, pady=12,
                                  activebackground="#3CA374", cursor="hand2")
        self.start_btn.pack(pady=5, fill=tk.X)
        
        # Durdur butonu
        self.stop_btn = tk.Button(button_container, text="⛔ Durdur", command=self.stop_bot,
                                 bg="#ED4245", fg="#FFFFFF", font=('Segoe UI', 12, 'bold'),
                                 relief=tk.FLAT, bd=0, padx=30, pady=12,
                                 activebackground="#C73E42", cursor="hand2")
        self.stop_btn.pack(pady=5, fill=tk.X)
        
        # Yenile butonu
        self.refresh_btn = tk.Button(button_container, text="🔄 Pencereleri Yenile", command=self.update_window_list,
                                    bg="#5865F2", fg="#FFFFFF", font=('Segoe UI', 10, 'bold'),
                                    relief=tk.FLAT, bd=0, padx=25, pady=10,
                                    activebackground="#4752C4", cursor="hand2")
        self.refresh_btn.pack(pady=5, fill=tk.X)
        
        # Hover efektleri
        def on_start_enter(e):
            self.start_btn.config(bg="#3CA374")
        def on_start_leave(e):
            self.start_btn.config(bg="#43B581")
        self.start_btn.bind("<Enter>", on_start_enter)
        self.start_btn.bind("<Leave>", on_start_leave)
        
        def on_stop_enter(e):
            self.stop_btn.config(bg="#C73E42")
        def on_stop_leave(e):
            self.stop_btn.config(bg="#ED4245")
        self.stop_btn.bind("<Enter>", on_stop_enter)
        self.stop_btn.bind("<Leave>", on_stop_leave)
        
        def on_refresh_enter(e):
            self.refresh_btn.config(bg="#4752C4")
        def on_refresh_leave(e):
            self.refresh_btn.config(bg="#5865F2")
        self.refresh_btn.bind("<Enter>", on_refresh_enter)
        self.refresh_btn.bind("<Leave>", on_refresh_leave)
        
        # Pencere seçici
        window_label = ttk.Label(sidebar, text="Hedef Pencere:", style="Custom.TLabel")
        window_label.pack(pady=(18, 2))
        self.window_combo = ttk.Combobox(sidebar, state="readonly", width=28, font=('Segoe UI', 10))
        self.window_combo.bind("<<ComboboxSelected>>", self.select_window)
        self.window_combo.pack(pady=(0, 10))
        
        # Ayarlar
        settings_frame = ttk.LabelFrame(sidebar, text="Ayarlar", padding="8", style="Custom.TLabelframe")
        settings_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Max retry
        retry_frame = ttk.Frame(settings_frame, style="Sidebar.TFrame")
        retry_frame.pack(fill=tk.X, pady=2)
        ttk.Label(retry_frame, text="🔁 Max Başarısızlık:", style="Custom.TLabel").pack(side=tk.LEFT, padx=2)
        self.max_retry_var = tk.StringVar(value=str(bot_core.DEFAULT_MAX_RETRY if bot_core and hasattr(bot_core, 'DEFAULT_MAX_RETRY') else "5"))
        retry_entry = ttk.Entry(retry_frame, textvariable=self.max_retry_var, width=5, font=('Segoe UI', 10))
        retry_entry.pack(side=tk.LEFT)

        # Ot süresi (herb_timeout_var)
        herb_frame = ttk.Frame(settings_frame, style="Sidebar.TFrame")
        herb_frame.pack(fill=tk.X, pady=2)
        ttk.Label(herb_frame, text="🌿 Ot Süresi:", style="Custom.TLabel").pack(side=tk.LEFT, padx=2)
        self.herb_timeout_var = tk.StringVar(value="5.0")
        herb_entry = ttk.Entry(herb_frame, textvariable=self.herb_timeout_var, width=5, font=('Segoe UI', 10))
        herb_entry.pack(side=tk.LEFT)

        # Can süresi (health_timeout_var)
        health_frame = ttk.Frame(settings_frame, style="Sidebar.TFrame")
        health_frame.pack(fill=tk.X, pady=2)
        ttk.Label(health_frame, text="❤️ Can Süresi:", style="Custom.TLabel").pack(side=tk.LEFT, padx=2)
        self.health_timeout_var = tk.StringVar(value="8.0")
        health_entry = ttk.Entry(health_frame, textvariable=self.health_timeout_var, width=5, font=('Segoe UI', 10))
        health_entry.pack(side=tk.LEFT)

        # Kara liste süresi (blacklist_duration_var)
        blacklist_frame = ttk.Frame(settings_frame, style="Sidebar.TFrame")
        blacklist_frame.pack(fill=tk.X, pady=2)
        ttk.Label(blacklist_frame, text="⛔ Kara Liste (sn):", style="Custom.TLabel").pack(side=tk.LEFT, padx=2)
        self.blacklist_duration_var = tk.StringVar(value="30")
        blacklist_entry = ttk.Entry(blacklist_frame, textvariable=self.blacklist_duration_var, width=5, font=('Segoe UI', 10))
        blacklist_entry.pack(side=tk.LEFT)

        # Hedef tipi seçici
        target_frame = ttk.Frame(settings_frame, style="Sidebar.TFrame")
        target_frame.pack(fill=tk.X, pady=2)
        ttk.Label(target_frame, text="🎯 Hedef Tipi:", style="Custom.TLabel").pack(side=tk.LEFT, padx=2)
        target_combo = ttk.Combobox(target_frame, textvariable=self.target_type, 
                                  values=["flower_lv1", "chest_lv1", "tree_lv1"], 
                                  state="readonly", width=10, font=('Segoe UI', 10))
        target_combo.pack(side=tk.LEFT)
        
        # Discord Webhook Ayarları
        webhook_frame = ttk.LabelFrame(sidebar, text="Discord Webhook", padding="8", style="Custom.TLabelframe")
        webhook_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Webhook URL
        webhook_url_label = ttk.Label(webhook_frame, text="🔗 Webhook URL:", style="Custom.TLabel")
        webhook_url_label.pack(anchor="w", pady=(0, 2))
        self.webhook_url_var = tk.StringVar(value="")
        webhook_url_entry = ttk.Entry(webhook_frame, textvariable=self.webhook_url_var, width=30, font=('Segoe UI', 9))
        webhook_url_entry.pack(fill=tk.X, pady=(0, 5))
        
        # User ID
        user_id_label = ttk.Label(webhook_frame, text="👤 Kullanıcı ID:", style="Custom.TLabel")
        user_id_label.pack(anchor="w", pady=(0, 2))
        self.user_id_var = tk.StringVar(value="")
        user_id_entry = ttk.Entry(webhook_frame, textvariable=self.user_id_var, width=30, font=('Segoe UI', 9))
        user_id_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Webhook test butonu - Modern design
        webhook_test_btn = tk.Button(webhook_frame, text="🧪 Test Webhook", command=self.test_webhook,
                                    bg="#5865F2", fg="#FFFFFF", font=('Segoe UI', 10, 'bold'),
                                    relief=tk.FLAT, bd=0, padx=20, pady=8,
                                    activebackground="#4752C4", cursor="hand2")
        webhook_test_btn.pack(pady=(8, 0))
        
        # Webhook test hover efekti
        def on_webhook_enter(e):
            webhook_test_btn.config(bg="#4752C4")
        def on_webhook_leave(e):
            webhook_test_btn.config(bg="#5865F2")
        webhook_test_btn.bind("<Enter>", on_webhook_enter)
        webhook_test_btn.bind("<Leave>", on_webhook_leave)
        
        # İstatistikler
        stats_frame = ttk.LabelFrame(main_area, text="İstatistikler", padding="10", style="Custom.TLabelframe")
        stats_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        self.stats_text = tk.StringVar()
        stats_label = ttk.Label(stats_frame, textvariable=self.stats_text, style="Custom.TLabel", font=('Segoe UI', 10))
        stats_label.pack(pady=5, anchor="w")
        self.herb_success_count = tk.IntVar(value=0)
        
        # Center Zone bilgisi
        center_frame = ttk.LabelFrame(main_area, text="🚫 Center Zone Koruması", padding="10", style="Custom.TLabelframe") 
        center_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        center_info = f"Center zone aktif: 80x80 pixel radius (Toplanan nesnelerin hayaletlerine tıklanmasını engeller)"
        center_label = ttk.Label(center_frame, text=center_info, style="Custom.TLabel", font=('Segoe UI', 9))
        center_label.pack(pady=2, anchor="w")
        
        # E-Q Tuş sistemi bilgisi
        eq_frame = ttk.LabelFrame(main_area, text="🎮 E-Q Kamera Sistemi", padding="10", style="Custom.TLabelframe")
        eq_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        eq_info = ("E-Q tuşları otomatik basılır: 10 döngü çiçek yok | 6 defa center zone | 8sn can azalmadı + Blacklist sadece başarılı toplamada temizlenir")
        eq_label = ttk.Label(eq_frame, text=eq_info, style="Custom.TLabel", font=('Segoe UI', 9))
        eq_label.pack(pady=2, anchor="w")
        
        # Discord Webhook bilgisi
        webhook_info_frame = ttk.LabelFrame(main_area, text="📩 Discord Webhook Sistemi", padding="10", style="Custom.TLabelframe")
        webhook_info_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
        webhook_info = ("Mesaj kutusu tespit edildiğinde Discord'a otomatik bildirim gönderir. Templates/message/ klasörüne mesaj kutusu görüntüleri ekleyin.")
        webhook_info_label = ttk.Label(webhook_info_frame, text=webhook_info, style="Custom.TLabel", font=('Segoe UI', 9))
        webhook_info_label.pack(pady=2, anchor="w")
        
        # Log alanı
        log_frame = ttk.LabelFrame(main_area, text="Log", padding="10", style="Custom.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        log_container = ttk.Frame(log_frame, style="Main.TFrame")
        log_container.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_container, height=15, width=80, font=('Consolas', 10), wrap=tk.WORD, bg="#23272A", fg="#C7CCD1", insertbackground=accent, borderwidth=0, highlightthickness=0)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.hwnd_map = {}
        
        # Bot yüklendiyse window list'i güncelle
        if bot_core and hasattr(bot_core, 'get_visible_windows'):
            self.update_window_list()
            self.log("🧪 Bot hazır. Pencereyi seçip başlatabilirsin.")
        else:
            self.log("⚠️ Bot henüz yüklenmedi. Lütfen bekleyin...")
            
        self.update_stats()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_stats(self):
        stats = (
            f"⏱️ Çalışma Süresi: {self.stats.get_session_duration()}\n"
            f"✅ Başarılı Tıklamalar: {self.stats.successful_clicks}\n"
            f"❌ Başarısız Tıklamalar: {self.stats.failed_clicks}\n"
            f"🌸 Toplam Bulunan Çiçek: {self.stats.total_flowers_found}\n"
            f"🌿 Herb Onaylı Başarılı Toplama: {self.herb_success_count.get()}"
        )
        self.stats_text.set(stats)
        self.window.after(1000, self.update_stats)
        
    def log(self, message):
        """Thread-safe logging - Queue'ya mesaj ekler"""
        try:
            self.log_queue.put(message, block=False)
        except queue.Full:
            pass  # Queue doluysa mesajı göz ardı et
    
    def process_log_queue(self):
        """Log queue'sunu işle - Ana GUI thread'inde çalışır"""
        try:
            # Queue'daki tüm mesajları işle
            while True:
                try:
                    message = self.log_queue.get_nowait()
                    self._write_log_to_gui(message)
                except queue.Empty:
                    break
        except Exception as e:
            # Hata olursa ignore et
            pass
        
        # Her 100ms'de bir queue'yu kontrol et
        self.window.after(100, self.process_log_queue)
    
    def _write_log_to_gui(self, message):
        """Gerçek log yazma - Sadece ana thread'de çalışır"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            
            # Log dosyasına kaydet
            try:
                log_file = bot_core.LOG_FILE if bot_core and hasattr(bot_core, 'LOG_FILE') else "bot.log"
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {message}\n")
            except:
                pass
                
            # Maximum log satırını kontrol et
            lines = int(self.log_text.index('end-1c').split('.')[0])
            max_lines = bot_core.MAX_LOG_LINES if bot_core and hasattr(bot_core, 'MAX_LOG_LINES') else 1000
            if lines > max_lines:
                self.log_text.delete("1.0", f"{lines-max_lines}.0")
        except Exception as e:
            # GUI thread hatası olursa ignore et
            pass
            
    def start_bot(self):
        if not self.selected_hwnd:
            messagebox.showwarning("Uyarı", "Lütfen önce bir pencere seçin!")
            return
            
        if not self.running:
            self.running = True
            self.stats.start_session()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Bot ayarlarını güncelle
            self.bot_logic.set_target_window(self.selected_hwnd)
            self.bot_logic.set_target_type(self.target_type.get())
            self.bot_logic.set_settings({
                'max_retry': int(self.max_retry_var.get()) if self.max_retry_var.get().isdigit() else 5,
                'herb_timeout': float(self.herb_timeout_var.get()) if self.herb_timeout_var.get() else 5.0,
                'health_timeout': float(self.health_timeout_var.get()) if self.health_timeout_var.get() else 8.0,
                'blacklist_duration': int(self.blacklist_duration_var.get()) if self.blacklist_duration_var.get().isdigit() else 30
            })
            
            # Bot callback'lerini ayarla
            self.bot_logic.set_gui_callbacks({
                'log': self.log,
                'update_stats': self.update_bot_stats
            })
            
            # Webhook ayarlarını güncelle
            self.bot_logic.set_webhook_settings(
                self.webhook_url_var.get(),
                self.user_id_var.get()
            )
            
            # Bot thread'ini başlat
            threading.Thread(target=self.run_bot_loop, daemon=True).start()
            self.log("▶️ Bot başlatıldı.")
            
    def stop_bot(self):
        if self.running:
            self.running = False
            self.bot_logic.stop()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            # Tüm sayaçları sıfırla
            self.stats.reset_stats()
            self.log("⛔ Bot durduruldu ve tüm sayaçlar sıfırlandı.")
            
    def run_bot_loop(self):
        """Bot döngüsünü çalıştırır"""
        try:
            self.bot_logic.run_loop(lambda: self.running)
        except Exception as e:
            self.log(f"❌ Bot döngüsünde hata: {str(e)}")
            self.stop_bot()
            
    def update_bot_stats(self, successful_clicks, failed_clicks, total_flowers_found, herb_success_count):
        """Bot mantığından gelen istatistikleri günceller"""
        self.stats.successful_clicks = successful_clicks
        self.stats.failed_clicks = failed_clicks
        self.stats.total_flowers_found = total_flowers_found
        self.herb_success_count.set(herb_success_count)
            
    def update_window_list(self):
        if bot_core and hasattr(bot_core, 'get_visible_windows'):
            window_list = bot_core.get_visible_windows()
            self.window_combo['values'] = [title for title, hwnd in window_list]
            self.hwnd_map.clear()
            for title, hwnd in window_list:
                self.hwnd_map[title] = hwnd
        else:
            self.window_combo['values'] = ["Bot henüz yüklenmedi"]
            self.hwnd_map.clear()
            
    def select_window(self, event):
        self.selected_hwnd = self.hwnd_map[self.window_combo.get()]
        self.log(f"🎯 Seçilen pencere: {self.window_combo.get()}")
    
    def test_webhook(self):
        """Discord webhook'unu test eder"""
        webhook_url = self.webhook_url_var.get().strip()
        user_id = self.user_id_var.get().strip()
        
        if not webhook_url:
            messagebox.showwarning("Uyarı", "Lütfen webhook URL'sini girin!")
            return
            
        try:
            # Test mesajı gönder
            if bot_core and hasattr(bot_core, 'send_discord_webhook'):
                success = bot_core.send_discord_webhook(webhook_url, user_id, "🧪 Test mesajı - Bot webhook sistemi çalışıyor!")
            else:
                self.log("❌ Bot henüz yüklenmedi, webhook test edilemiyor")
                messagebox.showerror("Hata", "Bot henüz yüklenmedi!\nÖnce botu başlatın.")
                return
            
            if success:
                self.log("✅ Webhook testi başarılı! Discord'da mesaj kontrol edin.")
                messagebox.showinfo("Başarılı", "Webhook testi başarılı!\nDiscord kanalınızda mesajı kontrol edin.")
            else:
                self.log("❌ Webhook testi başarısız! URL'yi kontrol edin.")
                messagebox.showerror("Hata", "Webhook testi başarısız!\nURL'yi kontrol edin.")
                
        except Exception as e:
            self.log(f"❌ Webhook test hatası: {str(e)}")
            messagebox.showerror("Hata", f"Webhook test hatası:\n{str(e)}")
        
    def on_closing(self):
        if self.running:
            if messagebox.askokcancel("Çıkış", "Bot çalışıyor. Çıkmak istediğinize emin misiniz?"):
                self.stop_bot()
                self.window.destroy()
        else:
            self.window.destroy()
            
    def run(self):
        """GUI'yi başlatır"""
        self.window.mainloop()

# === MAIN EXECUTION ===
if __name__ == "__main__":
    try:
        # GUI'yi başlat (license key kontrolü içerisinde yapılacak)
        gui = FlowerBotGUI()
        
        # Yönetici hakları kontrolü (bot yüklendikten sonra)
        if bot_core and hasattr(bot_core, 'is_admin') and not bot_core.is_admin():
            import ctypes
            # Yönetici hakları yoksa, yönetici olarak yeniden başlat
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        
        # Anti-Detection başlatma
        if (bot_core and hasattr(bot_core, 'ANTI_DETECTION') and 
            bot_core.ANTI_DETECTION.get("enabled", False)):
            fake_process = bot_core.AntiDetection.obfuscate_process()
            print(f"🛡️ Anti-Detection aktif - Process gizleme: {fake_process}")
        
        # GUI'yi çalıştır
        gui.run()
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        
        input("Bir hata oluştu, devam etmek için Enter'a basın...") 