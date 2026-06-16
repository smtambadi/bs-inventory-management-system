import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth.models import User

admin_user, created = User.objects.get_or_create(username='admin')
admin_user.set_password('password123')
admin_user.is_staff = True
admin_user.save()
print("Admin user created/updated.")

cashier_user, created = User.objects.get_or_create(username='cashier')
cashier_user.set_password('password123')
cashier_user.is_staff = False
cashier_user.save()
print("Cashier user created/updated.")
