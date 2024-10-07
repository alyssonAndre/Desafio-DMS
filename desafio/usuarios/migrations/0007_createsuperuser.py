import os
from django.db import migrations
from django.contrib.auth.models import User


class Migration(migrations.Migration):
    
    dependencies = [
        ('usuarios','0006_userprofile_is_2fa_enabled')
    ]

    def generate_superuser(apps,schema_editor):
        
        DJANGO_SU_EMAIL = os.environ.get('SU_EMAIL')
        DJANGO_SU_PASSWORD = os.environ.get('SU_PASSWORD')

        if not User.objects.filter(email=DJANGO_SU_EMAIL).exists():
            superuser = User.objects.create_superuser(

                username= DJANGO_SU_EMAIL,
                email= DJANGO_SU_EMAIL,
                password= DJANGO_SU_PASSWORD
            )
            
            superuser.save()

    
    operations = {
        migrations.RunPython(generate_superuser),
    } 
