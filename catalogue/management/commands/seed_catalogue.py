from django.core.management.base import BaseCommand
from faker import Faker
import random
from catalogue.models import Category, Product, ProductImage

fake = Faker()

IT_CATEGORIES = [
    "Laptops", "Desktops", "Monitors", "Keyboards", "Mice", "Networking",
    "Servers", "Storage Devices", "Printers", "Software"
]

IT_PRODUCTS = {
    "Laptops": ["Dell XPS 13", "MacBook Pro", "Lenovo ThinkPad X1", "HP Spectre x360"],
    "Desktops": ["Dell OptiPlex", "HP EliteDesk", "iMac 24-inch", "Lenovo ThinkCentre"],
    "Monitors": ["Dell UltraSharp 27", "LG UltraWide", "Samsung Odyssey G9", "ASUS ProArt"],
    "Keyboards": ["Logitech MX Keys", "Keychron K2", "Razer Huntsman", "Corsair K95"],
    "Mice": ["Logitech MX Master 3", "Razer DeathAdder", "Apple Magic Mouse", "SteelSeries Rival 600"],
    "Networking": ["TP-Link Archer AX6000", "Netgear Nighthawk", "Ubiquiti UniFi", "Cisco Catalyst"],
    "Servers": ["Dell PowerEdge R740", "HP ProLiant DL380", "Lenovo ThinkSystem SR650"],
    "Storage Devices": ["Samsung T7 SSD", "WD My Passport", "Seagate IronWolf HDD", "SanDisk Extreme Pro"],
    "Printers": ["HP LaserJet Pro", "Canon PIXMA", "Epson EcoTank", "Brother HL-L2395DW"],
    "Software": ["Microsoft Office 365", "Adobe Photoshop", "AutoCAD", "Slack"]
}

BRANDS = {
    "Laptops": ["Dell", "HP", "Lenovo", "Asus", "Acer", "Apple", "Microsoft"],
    "Desktops": ["Dell", "HP", "Lenovo", "Acer", "Apple", "MSI"],
    "Monitors": ["Dell", "LG", "Samsung", "ASUS", "BenQ", "ViewSonic"],
    "Keyboards": ["Logitech", "Corsair", "Razer", "Keychron", "Microsoft"],
    "Mice": ["Logitech", "Razer", "SteelSeries", "HP", "Microsoft"],
    "Networking": ["TP-Link", "Netgear", "Ubiquiti", "Cisco", "D-Link"],
    "Servers": ["Dell", "HP", "Lenovo", "IBM", "Supermicro"],
    "Storage Devices": ["Samsung", "WD", "Seagate", "SanDisk", "Kingston"],
    "Printers": ["HP", "Canon", "Epson", "Brother", "Lexmark"],
    "Software": ["Microsoft", "Adobe", "Autodesk", "Corel", "JetBrains"]
}

TOTAL_PRODUCTS = 90

class Command(BaseCommand):
    help = 'Seed the database with realistic IT categories, products, and images'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing data...")
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Creating IT categories...")
        categories = {}
        for cat_name in IT_CATEGORIES:
            category = Category.objects.create(
                name=cat_name,
                description=f"{cat_name} for your IT needs."
            )
            categories[cat_name] = category

        self.stdout.write("Creating IT products...")
        products = []

        # Add predefined products
        for cat_name, cat_obj in categories.items():
            for product_name in IT_PRODUCTS[cat_name]:
                product = Product.objects.create(
                    category=cat_obj,
                    name=product_name,
                    description=fake.paragraph(nb_sentences=3),
                    price=round(random.uniform(50.00, 5000.00), 2),
                    stock_quantity=random.randint(1, 50)
                )
                products.append(product)

        # Generate extra products with real brands & model numbers
        while len(products) < TOTAL_PRODUCTS:
            category_name = random.choice(IT_CATEGORIES)
            category_obj = categories[category_name]
            brand = random.choice(BRANDS[category_name])
            model_number = f"{random.randint(100, 999)}-{random.choice(['A', 'B', 'C', 'D', 'X', 'Z'])}{random.randint(10, 99)}"
            product_name = f"{brand} {category_name[:-1]} {model_number}"
            product = Product.objects.create(
                category=category_obj,
                name=product_name,
                description=fake.paragraph(nb_sentences=3),
                price=round(random.uniform(50.00, 5000.00), 2),
                stock_quantity=random.randint(1, 50)
            )
            products.append(product)

        self.stdout.write("Creating product images...")
        for product in products:
            num_images = random.randint(1, 3)
            primary_index = random.randint(0, num_images - 1)

            for i in range(num_images):
                ProductImage.objects.create(
                    product=product,
                    image_url=fake.image_url(width=600, height=400),
                    is_primary=(i == primary_index)
                )

        self.stdout.write(self.style.SUCCESS(f"IT product database seeded successfully with {len(products)} products!"))




# RANDOM ITEMS
# from django.core.management.base import BaseCommand
# from faker import Faker
# import random
# import uuid
# from catalogue.models import Category, Product, ProductImage

# fake = Faker()

# class Command(BaseCommand):
#     help = 'Seed the database with sample categories, products, and product images'

#     def handle(self, *args, **kwargs):
#         self.stdout.write("Clearing existing data...")
#         ProductImage.objects.all().delete()
#         Product.objects.all().delete()
#         Category.objects.all().delete()

#         self.stdout.write("Creating categories...")
#         categories = []
#         for _ in range(10):
#             category = Category.objects.create(
#                 name=fake.unique.word().title(),
#                 description=fake.sentence()
#             )
#             categories.append(category)

#         self.stdout.write("Creating products...")
#         products = []
#         for _ in range(100):
#             category = random.choice(categories)
#             product = Product.objects.create(
#                 category=category,
#                 name=fake.unique.sentence(nb_words=3),
#                 description=fake.paragraph(nb_sentences=3),
#                 price=round(random.uniform(10.00, 1000.00), 2),
#                 stock_quantity=random.randint(1, 100)
#             )
#             products.append(product)
#         self.stdout.write("Creating product images...")
#         for product in products:
#             num_images = random.randint(1, 4)
#             primary_index = random.randint(0, num_images - 1)

#             for i in range(num_images):
#                 ProductImage.objects.create(
#                     product=product,
#                     image_url=fake.image_url(width=600, height=400),
#                     is_primary=(i == primary_index)
#                 )

#         self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
