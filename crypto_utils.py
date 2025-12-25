"""
Минимальный криптомодуль с исправленной работой паролей
"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class CryptoError(Exception):
    pass

class FileEncryptor:
    def __init__(self, key=None):
        self.key = key or os.urandom(32)
        if len(self.key) != 32:
            raise CryptoError("Ключ должен быть 32 байта")
    
    @staticmethod
    def derive_key_from_password(password, salt=None):
        """Создание ключа из пароля"""
        if salt is None:
            salt = os.urandom(16)
        
        # Простой PBKDF2 через hashlib
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, 32)
        return key, salt
    
    @staticmethod
    def create_from_password(password, salt=None):
        """Создание шифратора напрямую из пароля"""
        key, salt = FileEncryptor.derive_key_from_password(password, salt)
        return FileEncryptor(key), salt
    
    def encrypt(self, data):
        """Шифрование данных"""
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return nonce + encryptor.tag + ciphertext
    
    def decrypt(self, data):
        """Дешифрование данных"""
        if len(data) < 28:
            raise CryptoError("Данные слишком короткие")
        
        nonce = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]
        
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def save_key(self, filename, password=None):
        """Сохранение ключа"""
        if password:
            salt = os.urandom(16)
            key, _ = self.derive_key_from_password(password, salt)
            
            # Шифруем основной ключ
            temp_encryptor = FileEncryptor(key)
            encrypted = temp_encryptor.encrypt(self.key)
            
            with open(filename, 'wb') as f:
                f.write(salt + encrypted)
        else:
            with open(filename, 'wb') as f:
                f.write(self.key)
    
    @staticmethod
    def load_key(filename, password=None):
        """Загрузка ключа"""
        with open(filename, 'rb') as f:
            data = f.read()
        
        if password:
            if len(data) < 16:
                raise CryptoError("Некорректный файл ключа")
            
            salt = data[:16]
            encrypted = data[16:]
            
            key, _ = FileEncryptor.derive_key_from_password(password, salt)
            decryptor = FileEncryptor(key)
            return FileEncryptor(decryptor.decrypt(encrypted))
        else:
            return FileEncryptor(data)