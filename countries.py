import urllib.parse

# Список флагов, которые мы ищем
ALLOWED_FLAGS = ['🇷🇺', '🇩🇪', '🇫🇮', '🇳🇱']

def filter_links(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            links = file.readlines()

        filtered_links = []

        for link in links:
            link = link.strip()
            if not link:
                continue
                
            # Декодируем ссылку (превращаем %F0%9F... в эмодзи)
            # unquote отлично справляется с твоим примером
            decoded_text = urllib.parse.unquote(link)

            # Проверяем, есть ли хоть один разрешенный флаг в декодированной строке
            if any(flag in decoded_text for flag in ALLOWED_FLAGS):
                filtered_links.append(link + '\n')

        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(filtered_links)
        
        print(f"Успех! Найдено: {len(filtered_links)}")
    
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    filter_links('cleaned_links.txt', 'filtered_links.txt')
