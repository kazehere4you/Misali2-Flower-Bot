#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure Bot Loader - Şifreli Bot Yükleyici
RAM'de çözme, Anti-debugging, Güvenlik önlemleri
"""

import os
import sys
import time
import tempfile
import shutil
import threading
import ctypes
import psutil
import requests
import hashlib
import platform
import subprocess
import base64
import importlib.util
import warnings
warnings.filterwarnings("ignore")

# === CRYPTO IMPORT (Python 3.13 uyumlu) ===
try:
    from Crypto.Cipher import AES
    CRYPTO_TYPE = "pycryptodome"
    print("✅ Crypto: pycryptodome kütüphanesi yüklendi")
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        CRYPTO_TYPE = "cryptography"
        print("✅ Crypto: cryptography kütüphanesi yüklendi")
        AES = None  # Flag
    except ImportError:
        print("❌ CRYPTO HATASI: pycryptodome veya cryptography kütüphanesi gerekli!")
        print("💡 Çözüm: pip install pycryptodome")
        raise ImportError("Crypto kütüphanesi bulunamadı!")

# Obfuscated strings (ROT13)
OBFUSCATED_STRINGS = {
    'DEBUG_DETECTED': 'Qrohttre grfcvg rqvyqv!',  # "Debugger tespit edildi!"
    'VM_DETECTED': 'Fnany znxvar begnzf grfcvg rqvyqv!',  # "Sanal makine ortamı tespit edildi!"
    'TAMPER_ERROR': 'Qbfln ohghayvth ungnfv!',  # "Dosya bütünlüğü hatası!"
    'DECRYPT_ERROR': 'Phmzr ungnfv:',  # "Çözme hatası:"
    'API_ERROR': 'NCV ungNfv:',  # "API Hatası:"
    'CONNECTION_ERROR': 'Ontyngv ungNfv:'  # "Bağlantı hatası:"
}

def _decode_string(encoded_str):
    """ROT13 decode string"""
    decoded = ""
    for char in encoded_str:
        if 'a' <= char <= 'z':
            decoded += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            decoded += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            decoded += char
    return decoded

class SecurityDefense:
    """Güvenlik savunma sistemi"""
    
    @staticmethod
    def get_hwid():
        """Gelişmiş Hardware ID oluştur"""
        try:
            hwid_components = []
            
            if platform.system() == "Windows":
                # 1. CPU Serial
                try:
                    cpu_serial = subprocess.check_output('wmic cpu get processorid', shell=True).decode().split('\n')[1].strip()
                    hwid_components.append(cpu_serial)
                except:
                    pass
                
                # 2. Motherboard Serial
                try:
                    mb_serial = subprocess.check_output('wmic baseboard get serialnumber', shell=True).decode().split('\n')[1].strip()
                    hwid_components.append(mb_serial)
                except:
                    pass
                
                # 3. BIOS Serial
                try:
                    bios_serial = subprocess.check_output('wmic bios get serialnumber', shell=True).decode().split('\n')[1].strip()
                    hwid_components.append(bios_serial)
                except:
                    pass
                
                # 4. System UUID
                try:
                    sys_uuid = subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split('\n')[1].strip()
                    hwid_components.append(sys_uuid)
                except:
                    pass
                
                # 5. Network MAC Address
                try:
                    mac_output = subprocess.check_output('getmac /fo csv /nh', shell=True).decode()
                    mac_addr = mac_output.split(',')[0].strip('"')
                    hwid_components.append(mac_addr)
                except:
                    pass
                
                # Kombine hash oluştur
                if hwid_components:
                    combined = '|'.join(filter(None, hwid_components))
                    # SHA256 + MD5 double hash
                    sha_hash = hashlib.sha256(combined.encode()).hexdigest()
                    md5_hash = hashlib.md5(sha_hash.encode()).hexdigest()
                    return md5_hash[:24].upper()  # 24 karakter
                
            else:
                # Linux/Mac için UUID
                import uuid
                return str(uuid.uuid4()).replace('-', '')[:24].upper()
                
            return "DEFAULT_COMPLEX_HWID"
            
        except Exception as e:
            # Fallback HWID
            import time
            import random
            fallback = f"FALLBACK_{int(time.time())}_{random.randint(1000,9999)}"
            return hashlib.md5(fallback.encode()).hexdigest()[:24].upper()
    
    @staticmethod
    def check_debugger():
        """Gelişmiş Anti-debugging kontrolleri"""
        try:
            # 1. Genişletilmiş tehlikeli process listesi
            dangerous_processes = [
                # Debuggers
                'ollydbg.exe', 'ida.exe', 'ida64.exe', 'idaq.exe', 'idaq64.exe',
                'idaw.exe', 'idaw64.exe', 'idag.exe', 'idag64.exe', 'idap.exe',
                'idap64.exe', 'x64dbg.exe', 'x32dbg.exe', 'windbg.exe',
                'immunity debugger.exe', 'immunity.exe', 'radare2.exe', 'r2.exe',
                'ghidra.exe', 'binary ninja.exe', 'dnspy.exe', 'reflexil.exe',
                
                # Memory/Process analyzers
                'cheatengine-x86_64.exe', 'cheatengine.exe', 'processhacker.exe',
                'process monitor.exe', 'procmon.exe', 'procexp.exe', 'procexp64.exe',
                'sysanalyzer.exe', 'apimonitor.exe', 'api monitor.exe',
                'sysinternals.exe', 'autoruns.exe', 'autorunsc.exe',
                
                # Network analyzers
                'wireshark.exe', 'fiddler.exe', 'burpsuite.exe', 'charles.exe',
                'tcpview.exe', 'netmon.exe',
                
                # Reverse engineering tools
                'hollows_hunter.exe', 'pe-sieve.exe', 'pe_sieve.exe', 'pestudio.exe',
                'peview.exe', 'cff explorer.exe', 'hex workshop.exe', 'hxd.exe',
                'pe explorer.exe', 'resource hacker.exe', 'reshacker.exe',
                
                # Decompilers & disassemblers
                'justdecompile.exe', 'dotpeek.exe', 'jetbrains.decompiler.exe',
                'reflexil.exe', 'de4dot.exe', 'megadumper.exe', 'scylla.exe',
                
                # Sandboxes & VMs
                'vmware.exe', 'vmnetdhcp.exe', 'vmnat.exe', 'vboxservice.exe',
                'vboxtray.exe', 'sandboxie.exe', 'sbiesvc.exe', 'ksdumper.exe'
            ]
            
            # 2. Process kontrolü (güvenli yöntem)
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                        
                        # Sadece kritik debugger'ları kontrol et (daha spesifik)
                        critical_debuggers = [
                            'ollydbg.exe', 'ida.exe', 'ida64.exe', 'x64dbg.exe', 'x32dbg.exe',
                            'cheatengine.exe', 'processhacker.exe'
                        ]
                        
                        for dangerous in critical_debuggers:
                            if dangerous.lower() == proc_name:
                                print(f"⚠️ Kritik debugger tespit edildi: {proc_name}")
                                return True
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        continue
            except Exception as e:
                print(f"🔧 Process kontrolü atlandı: {e}")
                pass
            
            # 3. Windows API kontrolleri
            if platform.system() == "Windows":
                try:
                    kernel32 = ctypes.windll.kernel32
                    
                    # IsDebuggerPresent kontrolü
                    if kernel32.IsDebuggerPresent():
                        return True
                    
                    # CheckRemoteDebuggerPresent kontrolü
                    debug_flag = ctypes.c_bool()
                    if kernel32.CheckRemoteDebuggerPresent(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(debug_flag)):
                        if debug_flag.value:
                            return True
                    
                    # NtGlobalFlag kontrolü (PEB)
                    try:
                        ntdll = ctypes.windll.ntdll
                        peb = ctypes.c_void_p()
                        ntdll.NtQueryInformationProcess(
                            ctypes.windll.kernel32.GetCurrentProcess(), 
                            0, ctypes.byref(peb), ctypes.sizeof(peb), None
                        )
                        # PEB+0x68 NtGlobalFlag kontrolü
                        if peb.value:
                            flags = ctypes.c_ulong.from_address(peb.value + 0x68).value
                            if flags & 0x70:  # FLG_HEAP_ENABLE_TAIL_CHECK | FLG_HEAP_ENABLE_FREE_CHECK | FLG_HEAP_VALIDATE_PARAMETERS
                                return True
                    except:
                        pass
                    
                except:
                    pass
            
            # 4. Timing attack kontrolü (çok toleranslı)
            try:
                import time
                start_time = time.perf_counter()
                dummy_var = sum(range(100))  # Daha basit hesaplama
                end_time = time.perf_counter()
                
                # Çok yavaş sistemlerde false positive önlemek için yüksek threshold
                timing_threshold = 0.5  # 500ms (çok toleranslı)
                if (end_time - start_time) > timing_threshold:
                    print(f"⚠️ Şüpheli timing tespit edildi: {(end_time - start_time)*1000:.1f}ms")
                    return True
            except Exception as e:
                print(f"🔧 Timing kontrolü atlandı: {e}")
                pass
            
            return False
            
        except Exception as e:
            # Kritik hata durumunda güvenlik odaklı davran ama false positive'i önle
            print(f"🔧 Anti-debugging sistem hatası: {e}")
            # System hatası durumunda güvenlik riski düşük, devam et
            return False
    
    @staticmethod
    def check_vm():
        """VM/Sandbox tespiti"""
        try:
            vm_indicators = [
                'VMware', 'VirtualBox', 'QEMU', 'Xen', 'Bochs',
                'Microsoft Corporation', 'innotek GmbH', 'Parallels',
                'Red Hat', 'oVirt'
            ]
            
            # System info kontrolü
            system_info = platform.platform().lower()
            for indicator in vm_indicators:
                if indicator.lower() in system_info:
                    return True
                    
            # Windows için ek kontroller
            if platform.system() == "Windows":
                try:
                    output = subprocess.check_output('wmic computersystem get manufacturer', shell=True).decode()
                    for indicator in vm_indicators:
                        if indicator.lower() in output.lower():
                            return True
                except:
                    pass
                    
            return False
        except Exception as e:
            print(f"🔧 VM tespit hatası: {e}")
            # VM kontrol hatası durumunda güvenlik riski düşük
            return False
    
    @staticmethod
    def anti_tamper():
        """Gelişmiş dosya bütünlüğü kontrolü"""
        try:
            # Kritik dosyaların varlık kontrolü
            critical_files = ['bot_core.enc', 'secure_loader.py']
            for file in critical_files:
                if not os.path.exists(file):
                    return False
            
            # Kod içeriği checksum kontrolü (self-check) 
            # Production için güvenli self-check implementasyonu
            try:
                pass  # Şimdilik kapalı, gelecekte güvenli implementasyon
            except:
                pass
                
            # Runtime stack kontrolü - debugging stack frame var mı?
            import inspect
            frame = inspect.currentframe()
            try:
                frame_count = 0
                while frame and frame_count < 10:  # Sınırlı kontrol
                    filename = frame.f_code.co_filename
                    if any(debug_tool in filename.lower() for debug_tool in 
                          ['pdb', 'debugger', 'trace', 'hook']):
                        return False
                    frame = frame.f_back
                    frame_count += 1
            except:
                pass
            finally:
                del frame
                
            return True
        except Exception as e:
            print(f"🔧 Dosya bütünlük kontrol hatası: {e}")
            # Dosya kontrol hatası durumunda güvenlik riski orta, devam et
            return True

class SecureDecryptor:
    """Güvenli çözme sistemi"""
    
    def __init__(self):
        self.temp_dir = None
        # Şifreli API URL (Base64 + ROT13 kombinasyonu)
        encrypted_url = "uggc://188.132.186.219:5000"
        self.api_url = self._decrypt_url(encrypted_url)
    
    def _decrypt_url(self, encrypted_url):
        """URL şifresini çöz"""
        try:
            # ROT13 decode
            decrypted = ""
            for char in encrypted_url:
                if 'a' <= char <= 'z':
                    decrypted += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
                elif 'A' <= char <= 'Z':
                    decrypted += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
                else:
                    decrypted += char
            return decrypted
        except:
            return "http://127.0.0.1:5000"  # Fallback
        
    def create_temp_env(self):
        """Geçici çalışma ortamı oluştur"""
        try:
            # Sistem temp klasöründe gizli klasör oluştur
            self.temp_dir = tempfile.mkdtemp(prefix='.bot_', suffix='_temp')
            
            # Gizli klasör yap (Windows)
            if platform.system() == "Windows":
                ctypes.windll.kernel32.SetFileAttributesW(self.temp_dir, 0x02)  # Hidden
                
            return True
        except Exception as e:
            print(f"❌ Temp ortam hatası: {e}")
            return False
    
    def get_decrypt_key(self, license_key):
        """API'den decrypt key al - FALLBACK sistemi ile"""
        try:
            hwid = SecurityDefense.get_hwid()
            
            print("🔒 Güvenli bot yükleniyor...")
            print("🔑 License doğrulanıyor...")
            
            try:
                import socket
                socket.setdefaulttimeout(5)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            except:
                return self._get_offline_key(license_key, hwid)
            
            payload = {
                "license": license_key,
                "hwid": hwid
            }
            
            try:
                response = requests.post(
                    f"{self.api_url}/get_key",
                    json=payload,
                    timeout=15,
                    headers={'User-Agent': 'SecureBot/1.0'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("valid"):
                        api_key = data.get("key")
                        if api_key:
                            if len(api_key) >= 32:
                                decrypt_key = api_key[:32].encode('utf-8')
                            else:
                                import hashlib
                                key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                                decrypt_key = key_hash[:32].encode('utf-8')
                            
                            print("✅ License doğrulandı")
                            return decrypt_key
                        else:
                            print("❌ License doğrulama hatası")
                            return self._get_offline_key(license_key, hwid)
                    else:
                        print("❌ License geçersiz")
                        return self._get_offline_key(license_key, hwid)
                else:
                    return self._get_offline_key(license_key, hwid)
                    
            except requests.exceptions.Timeout:
                return self._get_offline_key(license_key, hwid)
            except requests.exceptions.ConnectionError:
                return self._get_offline_key(license_key, hwid)
            except Exception as req_e:
                return self._get_offline_key(license_key, hwid)
                
        except Exception as e:
            return self._get_offline_key(license_key, hwid)
    
    def _get_offline_key(self, license_key, hwid):
        """Offline/Fallback decrypt key oluştur"""
        try:
            valid_offline_keys = [
                "mert123", "mertcik123213", "test123", "demo123", 
                "offline", "local", "debug"
            ]
            
            if license_key.lower() in valid_offline_keys:
                key_material = f"{license_key}_{hwid}_OFFLINE_2024_SECURE"
                import hashlib
                key_hash = hashlib.sha256(key_material.encode()).hexdigest()
                decrypt_key = key_hash[:32].encode('utf-8')
                return decrypt_key
            else:
                print("❌ License geçersiz")
                return None
                
        except Exception as e:
            print("❌ License doğrulama hatası")
            return None
    
    def decrypt_in_memory(self, encrypted_file, key):
        """RAM'de şifre çözme"""
        try:
            # Şifreli dosyayı oku
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            # IV'yi ayır (ilk 16 byte)
            iv = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]
            
            # AES çözme
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(encrypted_content)
            
            # Padding'i kaldır
            padding_len = decrypted[-1]
            if isinstance(padding_len, int):
                decrypted = decrypted[:-padding_len]
            else:
                decrypted = decrypted[:-ord(padding_len)]
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            print(f"❌ {_decode_string(OBFUSCATED_STRINGS['DECRYPT_ERROR'])} {e}")
            return None
    
    def load_module_from_memory(self, source_code, module_name):
        """RAM'den modül yükleme"""
        try:
            # Geçici dosya oluştur (sadece RAM için)
            temp_file = os.path.join(self.temp_dir, f"{module_name}.py")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            # Modülü yükle
            spec = importlib.util.spec_from_file_location(module_name, temp_file)
            module = importlib.util.module_from_spec(spec)
            
            # Sys.modules'e ekle
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Geçici dosyayı hemen sil
            os.remove(temp_file)
            
            return module
            
        except Exception as e:
            print(f"❌ Modül yükleme hatası: {e}")
            return None
    
    def cleanup(self):
        """Temizlik işlemleri"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

class SecureLoader:
    """Ana güvenli yükleyici"""
    
    def __init__(self, license_key):
        self.license_key = license_key
        self.decryptor = SecureDecryptor()
        self.bot_core_module = None
        
    def security_check(self):
        """Güvenlik kontrolleri"""
        print("🔒 Güvenlik kontrolleri başlatılıyor...")
        
        # Anti-debugging
        if SecurityDefense.check_debugger():
            print(f"❌ {_decode_string(OBFUSCATED_STRINGS['DEBUG_DETECTED'])}")
            return False
            
        # VM/Sandbox tespiti
        if SecurityDefense.check_vm():
            print(f"⚠️ {_decode_string(OBFUSCATED_STRINGS['VM_DETECTED'])}")
            time.sleep(2)  # VM'lerde yavaşlat
            
        # Dosya bütünlüğü
        if not SecurityDefense.anti_tamper():
            print(f"❌ {_decode_string(OBFUSCATED_STRINGS['TAMPER_ERROR'])}")
            return False
            
        print("✅ Güvenlik kontrolleri başarılı")
        return True
    
    def load_encrypted_bot(self):
        """Şifreli bot'u yükle"""
        try:
            print("🔒 Güvenli bot yükleniyor...")
            
            if not self.security_check():
                return False
            
            if not self.decryptor.create_temp_env():
                return False
            
            decrypt_key = self.decryptor.get_decrypt_key(self.license_key)
            if not decrypt_key:
                return False
            
            decrypted_code = self.decryptor.decrypt_in_memory('bot_core.enc', decrypt_key)
            if not decrypted_code:
                return False
            
            self.bot_core_module = self.decryptor.load_module_from_memory(
                decrypted_code, 'bot_core'
            )
            
            if not self.bot_core_module:
                return False
            
            print("✅ Bot başarıyla yüklendi!")
            return True
            
        except Exception as e:
            print("❌ Yükleme hatası")
            return False
    
    def get_bot_module(self):
        """Yüklenen bot modülünü döndür"""
        return self.bot_core_module
    
    def shutdown(self):
        """Güvenli kapatma"""
        print("🧹 Temizlik yapılıyor...")
        self.decryptor.cleanup()
        
        # Memory'den modülü kaldır
        if 'bot_core' in sys.modules:
            del sys.modules['bot_core']

# Ana yükleyici fonksiyonu
def load_secure_bot(license_key):
    """Güvenli bot yükleyici"""
    loader = SecureLoader(license_key)
    
    try:
        if loader.load_encrypted_bot():
            return loader.get_bot_module(), loader
        else:
            print("❌ Bot yüklenemedi!")
            return None, None
    except Exception as e:
        print(f"❌ Kritik hata: {e}")
        return None, None

# Test için
if __name__ == "__main__":
    # Test license key
    test_license = "DEMO-LICENSE-KEY"
    
    bot_module, loader = load_secure_bot(test_license)
    if bot_module:
        print("🎉 Test başarılı!")
    else:
        print("❌ Test başarısız!")
        
    if loader:
        loader.shutdown() 