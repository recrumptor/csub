import urllib.parse

ALLOWED_FLAGS = ['🇷🇺', '🇩🇪', '🇫🇮', '🇳🇱']

def filter_links(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            links = file.readlines()

        filtered_links = []

        for link in links:
            link = link.strip()
            if '#' not in link:
                continue
                
            # Разделяем: всё, что до # — это адрес/ключи, всё, что после — название
            # split('#', 1) делит строку только по первой найденной решетке
            parts = link.split('#', 1)
            name_part = urllib.parse.unquote(parts[1]) # Декодируем только название

            # Проверяем флаг ТОЛЬКО в названии
            if any(flag in name_part for flag in ALLOWED_FLAGS):
                filtered_links.append(link + '\n')

        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(filtered_links)
        
        print(f"Готово! Найдено по названию: {len(filtered_links)}")
    
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    filter_links('cleaned_links.txt', 'filtered_links.txt')

