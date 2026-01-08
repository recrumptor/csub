import requests
import re

# Источники
CONFIG_URL = "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/26.txt"
WHITELIST_URL = "https://raw.githubusercontent.com/hxehex/russia-mobile-internet-whitelist/main/whitelist.txt"

stats = {
    "total_received": 0,
    "bad_syntax": 0,
    "bad_ip_or_port": 0,
    "ad_spam": 0,
    "expired_or_warning": 0,
    "rejected_sni_count": 0,
    "valid_ru": 0,
    "valid_whitelist": 0
}

# Множество для хранения уникальных отбракованных доменов
rejected_sni_list = set()

def get_whitelist():
    try:
        resp = requests.get(WHITELIST_URL, timeout=10)
        return [line.strip().lower() for line in resp.text.splitlines() if line.strip() and not line.startswith('#')]
    except:
        print("! Ошибка загрузки вайтлиста, используем только .ru")
        return []

WHITELIST = get_whitelist()

def is_valid(link):
    if not link.strip().startswith("vless://"):
        return False

    # 1. Синтаксис
    if "&amp;" in link:
        stats["bad_syntax"] += 1
        return False

    # 2. IP и Порт
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

    # 3. Рекламный спам
    if re.search(r'(host|spx)=[^&]*@', link):
        stats["ad_spam"] += 1
        return False

    # 4. Заглушки
    if any(word in link.lower() for word in ["expired", "subscription_empty", "warning"]):
        stats["expired_or_warning"] += 1
        return False

    # 5. Фильтр SNI
    sni_match = re.search(r'sni=([^&?#]+)', link)
    if sni_match:
        sni = sni_match.group(1).lower()
        
        # Проверка .ru
        if sni.endswith('.ru'):
            stats["valid_ru"] += 1
            return True
        
        # Проверка по вайтлисту
        for allowed_domain in WHITELIST:
            if sni == allowed_domain or sni.endswith('.' + allowed_domain):
                stats["valid_whitelist"] += 1
                return True
                
        # Если не прошел — запоминаем SNI
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
        
        # Печать отчета
        print("="*40)
        print("📊 ОТЧЕТ О ФИЛЬТРАЦИИ")
        print("="*40)
        print(f"✅ Прошли проверку (.ru):   {stats['valid_ru']}")
        print(f"✅ Прошли по вайтлисту:     {stats['valid_whitelist']}")
        print(f"❌ Отбраковано SNI:         {stats['rejected_sni_count']}")
        print(f"💾 ИТОГО СОХРАНЕНО:         {len(cleaned_links)}")
        print("-" * 40)
        
        if rejected_sni_list:
            print("🔍 СПИСОК ОТБРАКОВАННЫХ SNI (уникальные):")
            # Сортируем для удобства чтения
            for s in sorted(rejected_sni_list):
                print(f"  - {s}")
            print("-" * 40)
            
        print(f"Всего получено строк: {stats['total_received']}")
        print("="*40)
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
