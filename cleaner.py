import requests
import re

URL = "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/26.txt"

# Словарь для сбора статистики
stats = {
    "total_received": 0,
    "bad_syntax": 0,
    "bad_ip_or_port": 0,
    "ad_spam": 0,
    "expired_or_warning": 0,
    "non_ru_sni": 0,
    "valid": 0
}

def is_valid(link):
    if not link.strip().startswith("vless://"):
        return False

    # 1. Синтаксис (&amp;)
    if "&amp;" in link:
        stats["bad_syntax"] += 1
        return False

    # 2. IP и Порт
    try:
        server_info = link.split('@')[1].split('?')[0]
        address = server_info.split(':')[0] if ':' in server_info else server_info
        port = server_info.split(':')[1] if ':' in server_info else "443"

        bad_addresses = ['0.0.0.0', '127.0.0.1', 'localhost', '1.1.1.1']
        if address in bad_addresses or port == "1":
            stats["bad_ip_or_port"] += 1
            return False
    except:
        stats["bad_ip_or_port"] += 1
        return False

    # 3. Рекламный спам (@ в host/spx)
    if re.search(r'(host|spx)=[^&]*@', link):
        stats["ad_spam"] += 1
        return False

    # 4. Заглушки
    lowered = link.lower()
    if any(word in lowered for word in ["expired", "subscription_empty", "warning"]):
        stats["expired_or_warning"] += 1
        return False

    # 5. SNI не .ru
    sni_match = re.search(r'sni=([^&?#]+)', link)
    if sni_match:
        sni = sni_match.group(1)
        if not sni.endswith('.ru'):
            stats["non_ru_sni"] += 1
            return False
    else:
        stats["non_ru_sni"] += 1
        return False

    stats["valid"] += 1
    return True

def main():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        lines = response.text.splitlines()
        stats["total_received"] = len(lines)
        
        cleaned_links = [line for line in lines if is_valid(line)]
        
        with open("cleaned_links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_links))
        
        # Печать красивой статистики в логи GitHub
        print("="*30)
        print("ОТЧЕТ О РАБОТЕ СКРИПТА")
        print("="*30)
        print(f"Всего получено строк:  {stats['total_received']}")
        print(f"Очищено (валидно):     {stats['valid']}")
        print("-"*30)
        print(f"Удалено по причинам:")
        print(f" - Ошибки синтаксиса (&amp;):    {stats['bad_syntax']}")
        print(f" - Мусорные IP/Порт (0.0.0.0): {stats['bad_ip_or_port']}")
        print(f" - Рекламный спам в параметрах: {stats['ad_spam']}")
        print(f" - Заглушки (Expired/Warning):  {stats['expired_or_warning']}")
        print(f" - SNI не в зоне .ru:           {stats['non_ru_sni']}")
        print("="*30)
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
