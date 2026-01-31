#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def create_user(username, password):
    from django.contrib.auth.models import User
    from superadmin.models import UserManageAccount

    user = User.objects.create_user(username=username, password=password)
    UserManageAccount.objects.create(user=user)
    return user


def main():
    
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if "--development" in sys.argv:
        os.environ["DEVELOPMENT_MODE"] = "True"
        sys.argv.remove("--development")
    # 自定义的命令
    if "createuser" == sys.argv[1]:
        username = sys.argv[2]
        password = sys.argv[3]
        execute_from_command_line(["manage.py", "runserver", "8080"])
        create_user(username, password)
        print(f"User \"{username}\" created successfully")
        return
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
