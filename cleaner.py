import requests
import re
import os

# Источники
# CONFIG_URL = "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/26.txt"
CONFIG_URL = "https://raw.githubusercontent.com/recrumptor/csub/refs/heads/main/vless_list.txt"
EXTERNAL_WHITELIST_URL = "https://raw.githubusercontent.com/hxehex/russia-mobile-internet-whitelist/main/whitelist.txt"
LOCAL_WHITELIST_FILE = "mycdn.txt"

stats = {
    "total_received": 0,
    "bad_syntax": 0,
    "bad_ip_or_port": 0,
    "ad_spam": 0,
    "expired_or_warning": 0,
    "rejected_sni_count": 0,
    "valid_ru": 0,
    "valid_external_whitelist": 0,
    "valid_my_cdn": 0
}

rejected_sni_list = set()

def load_whitelists():
    combined_list = set()
    
    # 1. Загружаем внешний список
    try:
        resp = requests.get(EXTERNAL_WHITELIST_URL, timeout=10)
        if resp.status_code == 200:
            external = [line.strip().lower() for line in resp.text.splitlines() if line.strip() and not line.startswith('#')]
            combined_list.update(external)
            print(f"Загружено из внешнего вайтлиста: {len(external)} доменов")
    except:
        print("! Ошибка загрузки внешнего вайтлиста")

    # 2. Загружаем ваш локальный файл mycdn.txt
    if os.path.exists(LOCAL_WHITELIST_FILE):
        try:
            with open(LOCAL_WHITELIST_FILE, "r", encoding="utf-8") as f:
                local = [line.strip().lower() for line in f.read().splitlines() if line.strip() and not line.startswith('#')]
                combined_list.update(local)
                print(f"Загружено из вашего mycdn.txt: {len(local)} доменов")
                # Сохраним для статистики отдельно
                return combined_list, set(local)
        except Exception as e:
            print(f"! Ошибка чтения mycdn.txt: {e}")
    
    return combined_list, set()

# Инициализация списков
FULL_WHITELIST, MY_CDN_SET = load_whitelists()

def is_valid(link):
    if not link.strip().startswith("vless://"):
        return False

    if "&amp;" in link:
        stats["bad_syntax"] += 1
        return False

    try:
        server_info = link.split('@')[1].split('?')[0]
        address = server_info.split(':')[0] if ':' in server_info else server_info
        port = server_info.split(':')[1] if ':' in server_info else "443"
        if address in ['0.0.0.0', '127.0.0.1', 'localhost'] or port == "1":
            stats["bad_ip_or_port"] += 1
            return False
    except:
        stats["bad_ip_or_port"] += 1
        return False

    if re.search(r'(host|spx)=[^&]*@', link):
        stats["ad_spam"] += 1
        return False

    if any(word in link.lower() for word in ["expired", "subscription_empty", "warning"]):
        stats["expired_or_warning"] += 1
        return False

    sni_match = re.search(r'sni=([^&?#]+)', link)
    if sni_match:
        sni = sni_match.group(1).lower()
        
        # 1. Сначала .ru
        if sni.endswith('.ru'):
            stats["valid_ru"] += 1
            return True
        
        # 2. Потом ваш личный список (приоритет для статистики)
        for my_domain in MY_CDN_SET:
            if sni == my_domain or sni.endswith('.' + my_domain):
                stats["valid_my_cdn"] += 1
                return True

        # 3. Потом внешний список
        for allowed_domain in FULL_WHITELIST:
            if sni == allowed_domain or sni.endswith('.' + allowed_domain):
                stats["valid_external_whitelist"] += 1
                return True
                
        rejected_sni_list.add(sni)
        stats["rejected_sni_count"] += 1
        return False
    else:
        stats["rejected_sni_count"] += 1
        return False

def main():
    try:
        response = requests.get(CONFIG_URL, timeout=30)
        lines = response.text.splitlines()
        stats["total_received"] = len(lines)
        
        cleaned_links = [line for line in lines if is_valid(line)]
        
        with open("cleaned_links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_links))
        
        print("="*40)
        print("📊 ОТЧЕТ С УЧЕТОМ MYCDN.TXT")
        print("="*40)
        print(f"✅ Прошли по .ru:           {stats['valid_ru']}")
        print(f"🌟 Прошли по вашему списку:  {stats['valid_my_cdn']}")
        print(f"✅ Прошли по внешнему списку: {stats['valid_external_whitelist']}")
        print(f"❌ Отбраковано SNI:         {stats['rejected_sni_count']}")
        print(f"💾 ИТОГО СОХРАНЕНО:         {len(cleaned_links)}")
        print("-" * 40)
        
        if rejected_sni_list:
            print(f"🔍 ОТБРАКОВАННЫЕ SNI: {len(rejected_sni_list)} шт.")
            for s in sorted(rejected_sni_list):
                print(f"  - {s}")
        print("="*40)
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
