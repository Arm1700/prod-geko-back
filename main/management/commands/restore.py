import os
import subprocess
import re
import environ
from datetime import datetime
from django.core.management import BaseCommand

# Инициализация environ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
environ.Env.read_env()

# Инициализация переменных окружения
env = environ.Env()


class Command(BaseCommand):
    help = 'Restore database and media files from a backup'

    def handle(self, *args, **kwargs):
        # Получаем значение поддомена из .env
        subdomain = env('SUBDOMAIN', default='default')

        # Путь для бэкапов: SUBDOMAIN/backups
        backup_dir = os.path.abspath(os.path.join(BASE_DIR, '..', '..', subdomain, 'backups'))

        # Получаем все папки в директории бэкапов, которые начинаются с числа и даты
        existing_backups = [f for f in os.listdir(backup_dir) if re.match(r'^\d+_\d{4}-\d{2}-\d{2}$', f)]

        if not existing_backups:
            self.stdout.write("No backups found.")
            return

        # Показываем список доступных бэкапов
        self.stdout.write("Available backups:")
        for idx, backup in enumerate(existing_backups, start=1):
            self.stdout.write(f"{idx}. {backup}")

        # Просим выбрать номер бэкапа для восстановления
        self.stdout.write("Enter the number of the backup to restore:")
        backup_number = input().strip()

        # Проверка на корректность ввода
        try:
            backup_number = int(backup_number)
            if backup_number < 1 or backup_number > len(existing_backups):
                raise ValueError
        except ValueError:
            self.stdout.write("Invalid backup number.")
            return

        # Получаем выбранный бэкап
        selected_backup = existing_backups[backup_number - 1]
        backup_folder = os.path.join(backup_dir, selected_backup)

        # Пути к файлам бэкапов
        db_backup_file = os.path.join(backup_folder, "db_backup.sql")
        media_backup_file = os.path.join(backup_folder, "media_backup.tar.gz")

        # Восстановление базы данных
        self.stdout.write(f"Restoring database from {db_backup_file}...")
        try:
            with open(db_backup_file, "rb") as f:
                subprocess.run(
                    ["psql", "-U", env('DB_USER'), "-h", env('DB_HOST'), "-p", env('DB_PORT'), env('DB_NAME')],
                    input=f.read(),
                    check=True,
                    env={**os.environ, "PGPASSWORD": env('DB_PASSWORD')}
                )
        except subprocess.CalledProcessError as e:
            self.stdout.write(f"Error during database restore: {e}")
            return

        # Восстановление медиа файлов
        self.stdout.write(f"Restoring media files from {media_backup_file}...")
        try:
            subprocess.run(
                ["tar", "-xzvf", media_backup_file, "-C", os.path.join(BASE_DIR, 'media')],
                check=True
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(f"Error during media files restore: {e}")
            return

        self.stdout.write(f"Restore completed from {selected_backup}")
