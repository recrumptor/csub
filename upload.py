import yadisk
import os

# --- КОНФИГУРАЦИЯ ---
TOKEN = os.getenv("YANDEX_DISK_TOKEN")
FILE_TO_UPLOAD = "filtered_links.txt"
DESTINATION_PATH = "/filtered_links.txt"  # Путь на Яндекс Диске

def upload_to_yandex_disk():
    # Инициализация клиента
    y = yadisk.YaDisk(token=TOKEN)

    # Проверка токена
    if not y.check_token():
        print("Ошибка: Невалидный токен Яндекс Диска!")
        return

    # Проверка наличия локального файла
    if not os.path.exists(FILE_TO_UPLOAD):
        print(f"Ошибка: Файл {FILE_TO_UPLOAD} не найден в текущей директории.")
        return

    try:
        # Проверяем, существует ли файл на диске, чтобы избежать ошибки перезаписи
        if y.exists(DESTINATION_PATH):
            print(f"Файл {DESTINATION_PATH} уже существует. Перезаписываю...")
            y.remove(DESTINATION_PATH, permanently=True)

        # Загрузка
        print(f"Начинаю загрузку {FILE_TO_UPLOAD}...")
        y.upload(FILE_TO_UPLOAD, DESTINATION_PATH)
        print(f"Успешно! Файл загружен в {DESTINATION_PATH}")

    except Exception as e:
        print(f"Произошла ошибка при загрузке: {e}")

if __name__ == "__main__":
    upload_to_yandex_disk()
