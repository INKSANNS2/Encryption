#!/usr/bin/env python3
"""
МИНИМАЛЬНЫЙ ШИФРОВАЛЬЩИК с поддержкой паролей
"""

import os
import sys
from pathlib import Path

# Импорт наших модулей
from crypto_utils import FileEncryptor, CryptoError
from file_utils import validate_path, read_file, write_file, get_files_from_directory, FileError

def main():
    """Главная функция"""
    while True:
        print("\n" + "="*50)
        print("ФАЙЛОВЫЙ ШИФРОВАЛЬЩИК")
        print("="*50)
        print("1. Зашифровать файл")
        print("2. Расшифровать файл")
        print("3. Создать ключ")
        print("4. Выйти")
        print("="*50)
        
        choice = input("Выберите действие (1-4): ").strip()
        
        if choice == "1":
            encrypt_file()
        elif choice == "2":
            decrypt_file()
        elif choice == "3":
            create_key()
        elif choice == "4":
            print("\nДо свидания!")
            break
        else:
            print("\nНеверный выбор!")

def encrypt_file():
    """Шифрование файла"""
    print("\n--- ШИФРОВАНИЕ ФАЙЛА ---")
    
    try:
        # Ввод пути
        path = input("Введите путь к файлу: ").strip()
        input_path = validate_path(path)
        
        if not input_path.is_file():
            print("❌ Это не файл!")
            return
        
        # Выбор метода
        print("\nВыберите метод:")
        print("1. С паролем")
        print("2. С ключом")
        method = input("Ваш выбор (1-2): ").strip()
        
        encryptor = None
        
        if method == "1":
            # С паролем
            password = input("Введите пароль: ")
            password2 = input("Повторите пароль: ")
            
            if password != password2:
                print("❌ Пароли не совпадают!")
                return
            
            key, salt = FileEncryptor.derive_key_from_password(password)
            encryptor = FileEncryptor(key)
            print("✅ Используется шифрование с паролем")
            
            # Сохраняем соль для возможности дешифрования
            key_path = Path("password_encrypted.key")
            with open(key_path, 'wb') as f:
                f.write(salt)
            print(f"⚠️  Для дешифрования нужен будет этот же пароль!")
            
        elif method == "2":
            # С ключом
            key_path = input("Введите путь к файлу ключа: ").strip()
            if not Path(key_path).exists():
                print("❌ Файл ключа не найден!")
                return
            
            # Проверяем, защищен ли ключ паролем
            try:
                encryptor = FileEncryptor.load_key(key_path)
            except CryptoError:
                # Если ошибка, возможно нужен пароль
                password = input("Введите пароль для ключа: ")
                encryptor = FileEncryptor.load_key(key_path, password)
        else:
            print("❌ Неверный выбор!")
            return
        
        # Шифрование
        data = read_file(input_path)
        encrypted_data = encryptor.encrypt(data)
        
        # Сохранение результата
        output_path = input_path.with_suffix(input_path.suffix + '.enc')
        write_file(output_path, encrypted_data, overwrite=True)
        
        print(f"✅ Файл зашифрован: {output_path}")
        
        # Удаление оригинала
        if input("Удалить оригинальный файл? (y/n): ").strip().lower() in ['y', 'д']:
            os.remove(input_path)
            print("✅ Оригинал удален")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def decrypt_file():
    """Дешифрование файла"""
    print("\n--- РАСШИФРОВАНИЕ ФАЙЛА ---")
    
    try:
        # Ввод пути
        path = input("Введите путь к зашифрованному файлу: ").strip()
        input_path = validate_path(path)
        
        if not input_path.is_file():
            print("❌ Это не файл!")
            return
        
        # Выбор метода дешифрования
        print("\nКак был зашифрован файл?")
        print("1. С паролем")
        print("2. С ключом")
        method = input("Ваш выбор (1-2): ").strip()
        
        encryptor = None
        
        if method == "1":
            # Дешифрование по паролю
            password = input("Введите пароль: ")
            
            # Пробуем использовать стандартный файл с солью
            salt_path = Path("password_encrypted.key")
            if salt_path.exists():
                with open(salt_path, 'rb') as f:
                    salt = f.read()
                key, _ = FileEncryptor.derive_key_from_password(password, salt)
                encryptor = FileEncryptor(key)
                print("✅ Используется дешифрование с паролем")
            else:
                print("❌ Не найден файл с солью. Используйте ключ для дешифрования.")
                return
            
        elif method == "2":
            # Дешифрование по ключу
            key_path = input("Введите путь к файлу ключа: ").strip()
            if not Path(key_path).exists():
                print("❌ Файл ключа не найден!")
                return
            
            # Проверяем, защищен ли ключ паролем
            password = None
            try:
                encryptor = FileEncryptor.load_key(key_path)
            except CryptoError:
                # Если ошибка, запрашиваем пароль
                password = input("Введите пароль для ключа: ")
                encryptor = FileEncryptor.load_key(key_path, password)
        else:
            print("❌ Неверный выбор!")
            return
        
        # Дешифрование
        data = read_file(input_path)
        decrypted_data = encryptor.decrypt(data)
        
        # Сохранение результата
        if input_path.suffix == '.enc':
            output_path = input_path.with_suffix('')
        else:
            output_path = input_path.with_name(input_path.stem + '_decrypted' + input_path.suffix)
        
        write_file(output_path, decrypted_data, overwrite=True)
        print(f"✅ Файл расшифрован: {output_path}")
        
    except CryptoError as e:
        print(f"❌ Ошибка дешифрования: {e}")
        print("Возможно неверный пароль или ключ")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def create_key():
    """Создание нового ключа"""
    print("\n--- СОЗДАНИЕ КЛЮЧА ---")
    
    try:
        # Генерация ключа
        encryptor = FileEncryptor()
        
        # Имя файла
        filename = input("Введите имя файла для ключа (по умолчанию: key.key): ").strip()
        if not filename:
            filename = "key.key"
        
        # Защита паролем
        use_password = input("Защитить ключ паролем? (y/n): ").strip().lower() in ['y', 'д']
        
        if use_password:
            password = input("Введите пароль: ")
            password2 = input("Повторите пароль: ")
            
            if password != password2:
                print("❌ Пароли не совпадают!")
                return
            
            encryptor.save_key(filename, password)
            print(f"✅ Ключ защищенный паролем сохранен в: {filename}")
        else:
            encryptor.save_key(filename)
            print(f"✅ Ключ сохранен в: {filename}")
        
        print("\n⚠️  ВАЖНО: Сохраните этот ключ в безопасном месте!")
        print("Без ключа невозможно восстановить зашифрованные файлы!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    # Проверка модулей
    try:
        from crypto_utils import FileEncryptor
        from file_utils import validate_path
    except ImportError as e:
        print(f"❌ Ошибка: {e}")
        print("Убедитесь что файлы crypto_utils.py и file_utils.py в той же папке")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")