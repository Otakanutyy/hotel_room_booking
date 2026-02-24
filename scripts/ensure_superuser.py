import os
import sys
from pathlib import Path

import django


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from django.contrib.auth import get_user_model

    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")

    if not username or not password:
        return

    User = get_user_model()
    user = User.objects.filter(username=username).first()

    if user is None:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Created superuser '{username}'")
        return

    # If it already exists, ensure it's superuser/staff
    changed = False
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if changed:
        user.save(update_fields=["is_staff", "is_superuser"])
        print(f"Updated user '{username}' to be superuser")


if __name__ == "__main__":
    main()
