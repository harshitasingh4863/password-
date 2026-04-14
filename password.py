"""
Secure Password Manager
======================
A CLI-based password manager with encryption, hashing, and secure storage.

Features:
- AES-256 encryption for passwords
- PBKDF2 key derivation from master password
- Secure file storage
- Add, view, update, delete passwords
- Generate strong random passwords
"""

import os
import json
import base64
import secrets
import getpass
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import argparse

class PasswordManager:
    def __init__(self, data_file="passwords.enc"):
        self.data_file = data_file
        self.salt = b'secure_salt_32_bytes!!'  # In production, generate/store randomly
        self.iterations = 100000
        
    def derive_key(self, master_password: str) -> bytes:
        """Derive encryption key from master password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    
    def encrypt(self, data: str, key: bytes) -> bytes:
        """Encrypt data using AES-256-CBC"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + encrypted_data)
    
    def decrypt(self, encrypted_data: bytes, key: bytes) -> str:
        """Decrypt data using AES-256-CBC"""
        raw_data = base64.b64decode(encrypted_data)
        iv = raw_data[:16]
        ciphertext = raw_data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad data
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data.decode()
    
    def load_passwords(self, master_password: str) -> dict:
        """Load encrypted passwords from file"""
        if not os.path.exists(self.data_file):
            return {}
        
        try:
            key = self.derive_key(master_password)
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt(encrypted_data, key)
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"❌ Error loading passwords: {e}")
            print("Master password might be incorrect!")
            return {}
    
    def save_passwords(self, passwords: dict, master_password: str):
        """Save passwords to encrypted file"""
        try:
            key = self.derive_key(master_password)
            json_data = json.dumps(passwords, indent=2)
            encrypted_data = self.encrypt(json_data, key)
            
            with open(self.data_file, 'wb') as f:
                f.write(encrypted_data)
            print("✅ Passwords saved securely!")
        except Exception as e:
            print(f"❌ Error saving passwords: {e}")
    
    def generate_password(self, length: int = 16) -> str:
        """Generate a strong random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def add_password(self, passwords: dict, service: str, username: str, password: str):
        """Add a new password entry"""
        passwords[service] = {
            'username': username,
            'password': password
        }
        print(f"✅ Added password for {service}")
    
    def view_password(self, passwords: dict, service: str):
        """View password for a service"""
        if service in passwords:
            entry = passwords[service]
            print(f"\n🔐 Service: {service}")
            print(f"   Username: {entry['username']}")
            print(f"   Password: {entry['password']}")
        else:
            print(f"❌ No password found for {service}")
    
    def update_password(self, passwords: dict, service: str, username: str = None, password: str = None):
        """Update existing password entry"""
        if service in passwords:
            if username:
                passwords[service]['username'] = username
            if password:
                passwords[service]['password'] = password
            print(f"✅ Updated password for {service}")
        else:
            print(f"❌ No password found for {service}")
    
    def delete_password(self, passwords: dict, service: str):
        """Delete password entry"""
        if service in passwords:
            del passwords[service]
            print(f"✅ Deleted password for {service}")
        else:
            print(f"❌ No password found for {service}")

def main():
    parser = argparse.ArgumentParser(description="Secure Password Manager")
    parser.add_argument('action', choices=['add', 'view', 'update', 'delete', 'list', 'generate'],
                       help="Action to perform")
    parser.add_argument('--service', '-s', help="Service name")
    parser.add_argument('--username', '-u', help="Username")
    parser.add_argument('--password', '-p', help="Password")
    parser.add_argument('--length', '-l', type=int, default=16, help="Password length for generation")
    
    args = parser.parse_args()
    
    # Get master password securely
    master_password = getpass.getpass("🔐 Enter master password: ")
    
    pm = PasswordManager()
    passwords = pm.load_passwords(master_password)
    
    if args.action == 'add':
        if not args.service or not args.username:
            print("❌ Usage: python password_manager.py add --service <service> --username <username> [--password <password>]")
            return
        
        password = args.password or pm.generate_password(args.length)
        print(f"🔑 Generated password: {password}")
        pm.add_password(passwords, args.service, args.username, password)
    
    elif args.action == 'view':
        if not args.service:
            print("❌ Usage: python password_manager.py view --service <service>")
            return
        pm.view_password(passwords, args.service)
    
    elif args.action == 'update':
        if not args.service:
            print("❌ Usage: python password_manager.py update --service <service> [--username <username>] [--password <password>]")
            return
        pm.update_password(passwords, args.service, args.username, args.password)
    
    elif args.action == 'delete':
        if not args.service:
            print("❌ Usage: python password_manager.py delete --service <service>")
            return
        pm.delete_password(passwords, args.service)
    
    elif args.action == 'list':
        if not passwords:
            print("📭 No passwords stored.")
        else:
            print("\n📋 Stored passwords:")
            for service in passwords.keys():
                print(f"   • {service}")
    
    elif args.action == 'generate':
        password = pm.generate_password(args.length)
        print(f"🔑 Generated password ({args.length} chars): {password}")
        return  # Don't save, just generate
    
    # Save changes
    pm.save_passwords(passwords, master_password)

if __name__ == "__main__":
    main()