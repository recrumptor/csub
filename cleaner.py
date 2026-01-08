import requests
import re

# Источник со списком конфигов
URL = "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/26.txt"

def is_valid(link):
    # 1. Базовая проверка: ссылка должна начинаться с vless://
    if not link.strip().startswith("vless://"):
        return False

    # 2. Очистка от HTML-сущностей
    # Если ссылка содержит &amp;, она "битая" по синтаксису — удаляем целиком
    if "&amp;" in link:
        return False

    # 3. Проверка адреса и порта
    try:
        # Извлекаем часть после @ и до начала параметров (?)
        # Пример: vless://uuid@1.2.3.4:443?security... -> берем "1.2.3.4:443"
        server_info = link.split('@')[1].split('?')[0]
        
        if ':' in server_info:
            address, port = server_info.split(':')
        else:
            address = server_info
            port = "443" # стандартный, если не указан

        # Удаляем "пустые" IP и порт 1
        bad_addresses = ['0.0.0.0', '127.0.0.1', 'localhost', '1.1.1.1']
        if address in bad_addresses or port == "1":
            return False
    except:
        return False

    # 4. Проверка на рекламный спам в параметрах host и spx (символ @)
    if re.search(r'(host|spx)=[^&]*@', link):
        return False

    # 5. Проверка на заглушки в названии или UUID
    lowered = link.lower()
    if "expired" in lowered or "subscription_empty" in lowered or "warning" in lowered:
        return False

    # 6. Фильтр по SNI: оставляем только те, что заканчиваются на .ru
    sni_match = re.search(r'sni=([^&?#]+)', link)
    if sni_match:
        sni = sni_match.group(1)
        if not sni.endswith('.ru'):
            return False
    else:
        # Если SNI нет вообще, для Reality это обычно означает нерабочий конфиг
        return False

    return True

def main():
    try:
        print(f"Загрузка данных из: {URL}")
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        
        lines = response.text.splitlines()
        print(f"Всего строк получено: {len(lines)}")
        
        # Фильтруем
        cleaned_links = [line for line in lines if is_valid(line)]
        
        # Сохраняем результат
        with open("cleaned_links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(cleaned_links))
        
        print(f"Очистка завершена. Сохранено строк: {len(cleaned_links)}")
        
    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")

if __name__ == "__main__":
    main()
