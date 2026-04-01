import requests
import re
import os

# Источники
CONFIG_URL = "vless_list.txt"
EXTERNAL_WHITELIST_URL = "https://raw.githubusercontent.com/hxehex/russia-mobile-internet-whitelist/main/whitelist.txt"
LOCAL_WHITELIST_FILE = "mycdn.txt"

stats = {
    "total_received": 0,
    "fixed_encoding": 0,
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
def fix_and_count(link):
    original = link
    # Цикл работает, пока не вычистит ВСЕ уровни вложенности %25
    while "%25" in link:
        link = link.replace("%25", "%")
    # 2. Очистка SNI от порта (ищет %3A и цифры после него в части параметров)
    # Ищем паттерн: sni=домен%3Aпорт
    link = re.sub(r'(sni=[^&#]+)%3A\d+', r'\1', link)
        
    # Если после замены строка изменилась — значит, мы реально что-то починили
    if link != original:
        stats["fixed_encoding"] += 1
    return link
    
    
def load_whitelists():
    combined_list = set()
    my_cdn_domains = set()
    
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
                my_cdn_domains.update(local)
                combined_list.update(local)
                print(f"Загружено из вашего mycdn.txt: {len(local)} доменов")
        except Exception as e:
            print(f"! Ошибка чтения mycdn.txt: {e}")
    
    return combined_list, my_cdn_domains

# Инициализация списков
FULL_WHITELIST, MY_CDN_SET = load_whitelists()

def is_valid(link):
    if not link.strip().startswith("vless://"):
        return False

    # 1. Проверка синтаксиса (&amp;)
    if "&amp;" in link:
        stats["bad_syntax"] += 1
        return False

    # 2. Проверка IP и порта
    try:
        server_info = link.split('@')[1].split('?')[0]
        address = server_info.split(':')[0] if ':' in server_info else server_info
        port = server_info.split(':')[1] if ':' in server_info else "443"
        
        # Отсекаем пустые IP и сервисный порт 1
        if address in ['0.0.0.0', '127.0.0.1', 'localhost', '1.1.1.1'] or port == "1":
            stats["bad_ip_or_port"] += 1
            return False
    except:
        stats["bad_ip_or_port"] += 1
        return False

    # 3. Проверка на рекламный спам в host или spx (наличие @ внутри параметра)
    if re.search(r'(host|spx)=[^&]*@', link):
        stats["ad_spam"] += 1
        return False

    # 4. Проверка на заглушки (Expired/Warning)
    if any(word in link.lower() for word in ["expired", "subscription_empty", "warning"]):
        stats["expired_or_warning"] += 1
        return False

    # 5. Проверка SNI (Reality)
    sni_match = re.search(r'sni=([^&?#]+)', link)
    if sni_match:
        sni = sni_match.group(1).lower()
        
        # 5.1 Сначала зона .ru
        # if sni.endswith('.ru'):
            # stats["valid_ru"] += 1
            # return True
        
        # 5.2 Затем ваш личный mycdn.txt
        for my_domain in MY_CDN_SET:
            if sni == my_domain or sni.endswith('.' + my_domain):
                stats["valid_my_cdn"] += 1
                return True

        # 5.3 Затем внешний вайтлист
        for allowed_domain in FULL_WHITELIST:
            if sni == allowed_domain or sni.endswith('.' + allowed_domain):
                stats["valid_external_whitelist"] += 1
                return True
                
        # Если домен не прошел ни один фильтр
        rejected_sni_list.add(sni)
        stats["rejected_sni_count"] += 1
        return False
    else:
        # Если SNI вообще не найден в ссылке
        stats["rejected_sni_count"] += 1
        return False

def main():
    try:
        print(f"Чтение файла: {CONFIG_URL}")
        
        # Проверяем, существует ли файл
        if not os.path.exists(CONFIG_URL):
            print(f"Ошибка: Файл {CONFIG_URL} не найден!")
            return

        # Читаем файл локально
        with open(CONFIG_URL, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            
        stats["total_received"] = len(lines)

        # ШАГ 1: Исправляем кодировки во всех строках
        processed_lines = [fix_and_count(line) for line in lines]
        
        # ШАГ 2: Фильтруем уже исправленные ссылки через is_valid
        cleaned_links = [line for line in processed_lines if is_valid(line)]
        
        with open("cleaned_links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_links))
        
        print("="*40)
        print("📊 ПОЛНЫЙ ОТЧЕТ О ФИЛЬТРАЦИИ")
        print("="*40)
        print(f"Всего получено строк:      {stats['total_received']}")
        print(f"🔧 Исправлено кодировок:    {stats['fixed_encoding']}") 
        print(f"🌟 Прошли по mycdn.txt:     {stats['valid_my_cdn']}")
        print(f"✅ Прошли по внешнему списку: {stats['valid_external_whitelist']}")
        print("-" * 40)
        print(f"❌ ОТБРАКОВАНО:")
        print(f" - Ошибки синтаксиса (&amp;):    {stats['bad_syntax']}")
        print(f" - Пустые IP / Порт 1:        {stats['bad_ip_or_port']}")
        print(f" - Рекламный спам (host/spx): {stats['ad_spam']}")
        print(f" - Заглушки (Expired/Empty):  {stats['expired_or_warning']}")
        print(f" - Неизвестные SNI:           {stats['rejected_sni_count']}")
        print("-" * 40)
        print(f"💾 ИТОГО СОХРАНЕНО:         {len(cleaned_links)}")
        print("-" * 40)
        
        if rejected_sni_list:
            print(f"🔍 СПИСОК ОТБРАКОВАННЫХ SNI (уникальные):")
            for s in sorted(rejected_sni_list):
                print(f"  - {s}")
        print("="*40)
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
