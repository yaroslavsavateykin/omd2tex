import os

def find_file(filename, search_path=None):
    """
    Ищет файл в текущей директории и её поддиректориях.
    
    Параметры:
        filename (str): Имя файла для поиска (например "file.txt")
        search_path (str, optional): Стартовая директория. По умолчанию - текущая.
    
    Возвращает:
        str: Абсолютный путь к файлу если найден, иначе None.
    """
    # Обработка пути поиска
    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)
    
    # Проверка существования директории
    if not os.path.exists(search_path):
        raise FileNotFoundError(f"Directory doesn't exist: {search_path}")
    
    # Регистронезависимый поиск для Windows/MacOS
    filename_lower = filename.lower()
    for root, dirs, files in os.walk(search_path):
        for f in files:
            if f.lower() == filename_lower:
                return os.path.join(root, f)
    
    return None  # Явное указание на отсутствие результата

def get_image_dimensions(file_path):
    """Получает ширину и высоту изображения."""
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except FileNotFoundError:
        return None
