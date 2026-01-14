# countries.py
import re

# Допустимые коды флагов стран
ALLOWED_FLAGS = {
    '🇷🇺': 'Россия',    # Россия
    '🇩🇪': 'Германия',  # Германия
    '🇫Финляндия': 'Финляндия',  # Финляндия
    '🇳🇱': 'Нидерланды'  # Нидерланды
}

def filter_links(input_file, output_file):
    try:
        # Читаем исходный файл
        with open(input_file, 'r', encoding='utf-8') as file:
            links = file.readlines()

        # Создаем список для отфильтрованных ссылок
        filtered_links = []

        # Регулярное выражение для поиска флага в описании
        flag_pattern = re.compile(r'^(.*)#([\u2700-\uE0FF]+)')

        for link in links:
            # Ищем флаг в описании
            match = flag_pattern.search(link)
            if match:
                flag = match.group(2)
                # Проверяем, есть ли флаг в разрешенном списке
                if flag in ALLOWED_FLAGS:
                    filtered_links.append(link)

        # Записываем отфильтрованные ссылки в новый файл
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(filtered_links)
        
        print(f"Отфильтровано {len(filtered_links)} ссылок")
    
    except Exception as e:
        print(f"Ошибка при обработке файла: {str(e)}")

if __name__ == "__main__":
    # Запускаем фильтрацию
    filter_links('cleaned_links.txt', 'filtered_links.txt')
