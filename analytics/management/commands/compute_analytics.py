from django.core.management.base import BaseCommand
from analytics.signals import _compute_and_cache_analytics


class Command(BaseCommand):
    help = 'Compute and cache analytics data'

    def handle(self, *args, **options):
        self.stdout.write('Computing and caching analytics data...')
        _compute_and_cache_analytics()
        self.stdout.write(
            self.style.SUCCESS('Successfully computed and cached analytics data')
        )