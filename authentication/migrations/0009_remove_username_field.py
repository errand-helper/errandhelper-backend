# Generated manually to fix username constraint issue
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_alter_user_role'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE authentication_user DROP CONSTRAINT IF EXISTS authentication_user_username_key;",
            reverse_sql="ALTER TABLE authentication_user ADD CONSTRAINT authentication_user_username_key UNIQUE (username);"
        ),
        migrations.RunSQL(
            "ALTER TABLE authentication_user DROP COLUMN IF EXISTS username;",
            reverse_sql="ALTER TABLE authentication_user ADD COLUMN username VARCHAR(150) NOT NULL DEFAULT '';"
        ),
        migrations.RunSQL(
            "ALTER TABLE authentication_user DROP COLUMN IF EXISTS date_joined;",
            reverse_sql="ALTER TABLE authentication_user ADD COLUMN date_joined TIMESTAMP WITH TIME ZONE;"
        ),
    ]