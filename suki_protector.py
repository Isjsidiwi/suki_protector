import os
import sys
import subprocess
import requests
import time
import uuid

# --- CONFIG ---
AUTH_URL = "https://lixynso.x10.mx/connect"

# --- DEFINISI WARNA (SUDAH DIPERBAIKI) ---
R = "\033[31m"   # Merah
G = "\033[32m"   # Hijau
C = "\033[36m"   # Cyan
Y = "\033[33m"   # Kuning
W = "\033[0m"    # Putih (Reset)
P = "\033[35m"   # Purple
B = "\033[1m"    # Bold (INI YANG TADI HILANG)

def get_android_id():
    """Mendapatkan Device ID"""
    try:
        cmd = "settings get secure android_id"
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if out: return out.decode('utf-8').strip()
    except: pass
    return str(uuid.getnode())

def security_checks():
    """
    Cek Keamanan: HANYA Anti-Sniffer. 
    (Anti-VPN dimatikan agar tidak false alarm)
    """
    threat = False
    threat_type = ""

    # Cek Environment Proxy (Anti Canary/Reqable)
    proxies = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]
    for proxy in proxies:
        if proxy in os.environ:
            threat = True
            threat_type = "HTTP CANARY / SNIFFER DETECTED"
            
    if threat:
        os.system('clear')
        print(f"\n{R}╔════════════════════════════════════════════╗{W}")
        print(f"{R}║         SECURITY BREACH DETECTED           ║{W}")
        print(f"{R}╠════════════════════════════════════════════╣{W}")
        print(f"{R}║ TYPE: {threat_type:<28} ║{W}")
        print(f"{R}║ [!] Please turn off Packet Sniffer app.    ║{W}")
        print(f"{R}╚════════════════════════════════════════════╝{W}")
        if os.path.exists("license.key"): os.remove("license.key")
        time.sleep(2)
        sys.exit()

def validate_user():
    """Proses Login ke Server"""
    security_checks()
    
    os.system('clear')
    print(f"{P}╔══════════════════════════════════════╗{W}")
    print(f"{P}║      SUKI PROTECTOR - GUARD SYSTEM   ║{W}")
    print(f"{P}╚══════════════════════════════════════╝{W}")
    
    # Auto-Load Key
    saved_key, saved_game = "", ""
    if os.path.exists("license.key"):
        try:
            with open("license.key", "r") as f:
                d = f.read().strip().split("|")
                if len(d)>=1: saved_key=d[0]
                if len(d)>=2: saved_game=d[1]
        except: pass

    if saved_key:
        print(f"{C}[*] Verifying Session Integrity...{W}")
        time.sleep(0.5)
        user_key = saved_key
    else:
        print(f"{Y}[LOCKED] Authentication Required{W}")
        # Di sini error terjadi sebelumnya karena B belum didefinisikan
        user_key = input(f"{B}INPUT KEY >> {W}")

    if not user_key: sys.exit("Key Empty.")

    print(f"{C}[*] Connecting to Secure Gateway...{W}")
    
    # List game untuk auto-detect
    GAME_LIST = ["CODM", "BLOODSTRIKE", "BS", "PUBG", "PUBGM", "FF", "VIP", "TEST"]
    device_id = get_android_id()
    
    # Prioritaskan game yang tersimpan
    scan_list = GAME_LIST.copy()
    if saved_game and saved_game in scan_list:
        scan_list.remove(saved_game)
        scan_list.insert(0, saved_game)

    valid = False
    detected_game = ""

    # Loop Cek Server
    for game in scan_list:
        try:
            payload = {"game": game, "user_key": user_key, "serial": device_id}
            r = requests.post(AUTH_URL, data=payload, timeout=3)
            if r.status_code == 200:
                resp = r.json()
                if resp.get("status") is True:
                    valid = True
                    detected_game = game
                    break
        except:
            pass
            
    if valid:
        with open("license.key", "w") as f: 
            f.write(f"{user_key}|{detected_game}")
        print(f"{G}[SUCCESS] ACCESS GRANTED ({detected_game}){W}")
        time.sleep(1)
        return True
    else:
        print(f"{R}[!] Access Denied: Invalid Key or HWID{W}")
        if os.path.exists("license.key"): os.remove("license.key")
        time.sleep(2)
        sys.exit()
