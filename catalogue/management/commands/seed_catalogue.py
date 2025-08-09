from django.core.management.base import BaseCommand
from faker import Faker
import random
import uuid
from catalogue.models import Category, Product, ProductImage

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample categories, products, and product images'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing data...")
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Creating categories...")
        categories = []
        for _ in range(10):
            category = Category.objects.create(
                name=fake.unique.word().title(),
                description=fake.sentence()
            )
            categories.append(category)

        self.stdout.write("Creating products...")
        products = []
        for _ in range(100):
            category = random.choice(categories)
            product = Product.objects.create(
                category=category,
                name=fake.unique.sentence(nb_words=3),
                description=fake.paragraph(nb_sentences=3),
                price=round(random.uniform(10.00, 1000.00), 2),
                stock_quantity=random.randint(1, 100)
            )
            products.append(product)
        self.stdout.write("Creating product images...")
        for product in products:
            num_images = random.randint(1, 4)
            primary_index = random.randint(0, num_images - 1)

            for i in range(num_images):
                ProductImage.objects.create(
                    product=product,
                    image_url=fake.image_url(width=600, height=400),
                    is_primary=(i == primary_index)
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
