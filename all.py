import os
import sys
import subprocess
import django


def main():
    # Path to the virtual environment
    venv_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'project', 'backend','geko-back', 'venv')

    # Path to manage.py
    project_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'project', 'backend', 'geko-back')
    manage_path = os.path.join(project_path, "manage.py")

    # Set DJANGO_SETTINGS_MODULE environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geko.settings")

    # Run Django commands within the virtual environment
    subprocess.run([os.path.join(venv_path, 'Scripts', 'python'), manage_path, 'makemigrations'])
    subprocess.run([os.path.join(venv_path, 'Scripts', 'python'), manage_path, 'migrate'])
    subprocess.run(
        [os.path.join(venv_path, 'Scripts', 'python'), manage_path, 'createsuperuser', '--email=admin@gmail.com',
         '--username=admin', '--noinput'])

    # Set the password for the superuser
    from django.contrib.auth.models import User

    user = User.objects.get(username='admin')
    user.set_password('admin')
    user.save()


if __name__ == "__main__":
    # Set up Django settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geko.settings")
    django.setup()

    # Call the main function
    main()
