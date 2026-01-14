import urllib.parse
import re

# Список флагов (теперь в обычном виде, скрипт сам их найдет после декодирования)
ALLOWED_FLAGS = {
    '🇷🇺': 'Россия',
    '🇩🇪': 'Германия',
    '🇫🇮': 'Финляндия',
    '🇳🇱': 'Нидерланды'
}

def filter_links(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            links = file.readlines()

        filtered_links = []
        
        # Регулярка для поиска флага (двух символов региона)
        flag_pattern = re.compile(r'([\U0001F1E6-\U0001F1FF]{2})')

        for link in links:
            # 1. Декодируем ссылку (%F0%9F%87%B7 -> 🇷🇺)
            decoded_link = urllib.parse.unquote(link)
            
            # 2. Ищем флаг в части после символа #
            if '#' in decoded_link:
                anchor = decoded_link.split('#')[-1]
                match = flag_pattern.search(anchor)
                
                if match:
                    flag = match.group(1)
                    if flag in ALLOWED_FLAGS:
                        filtered_links.append(link)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(filtered_links)
        
        print(f"Готово! Найдено подходящих ссылок: {len(filtered_links)}")
    
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    filter_links('cleaned_links.txt', 'filtered_links.txt')
