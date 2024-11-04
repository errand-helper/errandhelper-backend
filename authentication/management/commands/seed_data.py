import random
from django.core.management.base import BaseCommand
# from apps.clientcore.models import County, SKTeams, SubCounty, Venue, Ward
from django.utils.text import slugify
from faker import Faker

from authentication.models import User
from service.models import Category
# from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Seed football teams into the database'

    def handle(self, *args, **kwargs):
       
        self.seed_super_admin()
        self.seed_category(**kwargs)
        # self.seed_venues()
        # self.seed_business_data()
        self.stdout.write(self.style.SUCCESS(
            'Database seeded'))

   
        # return


    def seed_super_admin(self):
        """
        Seed a default super admin if none exists.
        """
        first_name = 'admin'
        last_name = 'admin'
        email = 'admin@example.com'
        password = 'admin1234'  

        # Check if a superuser with the given username exists
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                first_name=first_name,last_name=last_name, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(
                f'Super admin "{email}" WITH PASSWORD "{password}" has been created successfully.'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Super admin "{email}" already exists.'))

    def seed_category(self, **kwargs):
        # fake = Faker()

        sample_categories = ['farming', 'building and construction', 'house chores']
        existing_category_names = set(Category.objects.values_list("name", flat=True))

        # Create each category if it doesn’t already exist
        for category_name in sample_categories:
            if category_name not in existing_category_names:
                Category.objects.create(name=category_name)
                existing_category_names.add(category_name)


        self.stdout.write(self.style.SUCCESS("Database seeding completed."))    