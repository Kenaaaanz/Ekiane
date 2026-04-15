# Generated manually for website_settings

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="ContactInfo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(verbose_name="Contact Email")),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="Phone Number")),
                ("address", models.TextField(blank=True, verbose_name="Address")),
                ("business_hours", models.TextField(blank=True, verbose_name="Business Hours")),
                ("social_facebook", models.URLField(blank=True, verbose_name="Facebook URL")),
                ("social_instagram", models.URLField(blank=True, verbose_name="Instagram URL")),
                ("social_twitter", models.URLField(blank=True, verbose_name="Twitter URL")),
            ],
            options={
                "verbose_name": "Contact Information",
                "verbose_name_plural": "Contact Information",
            },
        ),
        migrations.CreateModel(
            name="AboutPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(default="About Ekiane", max_length=200, verbose_name="Page Title")),
                ("hero_title", models.CharField(default="Our Story", max_length=200, verbose_name="Hero Title")),
                ("hero_subtitle", models.TextField(blank=True, verbose_name="Hero Subtitle")),
                ("brand_story", models.TextField(verbose_name="Brand Story")),
                ("mission", models.TextField(blank=True, verbose_name="Mission Statement")),
                ("values", models.TextField(blank=True, verbose_name="Core Values")),
                ("timeline", models.TextField(blank=True, verbose_name="Company Timeline")),
                ("philosophy", models.TextField(blank=True, verbose_name="Beauty Philosophy")),
                ("hero_image", models.ImageField(blank=True, upload_to="about/", verbose_name="Hero Image")),
                ("brand_image", models.ImageField(blank=True, upload_to="about/", verbose_name="Brand Image")),
                ("timeline_image", models.ImageField(blank=True, upload_to="about/", verbose_name="Timeline Image")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "About Page Content",
                "verbose_name_plural": "About Page Content",
            },
        ),
    ]