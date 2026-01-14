import re

# 1. Исправлен флаг Финляндии
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

        # 2. Исправлено RE: ищем # и два региональных символа в самом конце строки
        # \s* берет возможные пробелы перед концом строки
        flag_pattern = re.compile(r'#([\U0001F1E6-\U0001F1FF]{2})\s*$')

        for link in links:
            match = flag_pattern.search(link.strip())
            if match:
                flag = match.group(1)
                if flag in ALLOWED_FLAGS:
                    filtered_links.append(link)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(filtered_links)
        
        print(f"Готово! Сохранено ссылок: {len(filtered_links)}")
    
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    filter_links('cleaned_links.txt', 'filtered_links.txt')

