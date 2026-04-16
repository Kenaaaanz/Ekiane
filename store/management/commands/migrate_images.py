from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product
import os
import cloudinary.uploader
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Migrate existing local product images to Cloudinary'

    def handle(self, *args, **options):
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING('This command should only be run in production with Cloudinary configured')
            )
            return

        products_with_images = Product.objects.exclude(image='')

        if not products_with_images:
            self.stdout.write('No products with images found.')
            return

        self.stdout.write(f'Found {products_with_images.count()} products with images to migrate')

        for product in products_with_images:
            try:
                # Get the local file path
                image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))

                if os.path.exists(image_path):
                    self.stdout.write(f'Migrating image for product: {product.name}')

                    # Upload to Cloudinary
                    with open(image_path, 'rb') as image_file:
                        result = cloudinary.uploader.upload(image_file, folder='products/')

                    # Update the product image field with Cloudinary URL
                    product.image = result['public_id'] + '.' + result['format']
                    product.save()

                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully migrated image for {product.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Image file not found for {product.name}: {image_path}')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error migrating image for {product.name}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Migration completed!'))