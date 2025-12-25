"""
Минимальные файловые операции
"""

import os
from pathlib import Path

class FileError(Exception):
    pass

def validate_path(path):
    """Проверка пути"""
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileError(f"Путь не существует: {path}")
    return path_obj

def read_file(filepath):
    """Чтение файла"""
    with open(filepath, 'rb') as f:
        return f.read()

def write_file(filepath, data, overwrite=False):
    """Запись файла"""
    if filepath.exists() and not overwrite:
        raise FileError(f"Файл уже существует: {filepath}")
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(data)
    return True

def get_files_from_directory(directory, recursive=True):
    """Получение файлов из директории"""
    if not directory.is_dir():
        return [directory]
    
    files = []
    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(Path(root) / filename)
    else:
        files = [f for f in directory.iterdir() if f.is_file()]
    
    return files