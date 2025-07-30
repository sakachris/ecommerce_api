# catalogue/management/commands/block_ip.py

from django.core.management.base import BaseCommand
from catalogue.models import BlockedIP


class Command(BaseCommand):
    help = "Block an IP address"

    def add_arguments(self, parser):
        parser.add_argument('ip', type=str, help='IP address to block')

    def handle(self, *args, **kwargs):
        ip = kwargs['ip']
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked IP: {ip}"))
        else:
            self.stdout.write(self.style.WARNING(f"IP already blocked: {ip}"))
