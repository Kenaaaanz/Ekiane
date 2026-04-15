from django.db import models

class ContactInfo(models.Model):
    email = models.EmailField(verbose_name="Contact Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    address = models.TextField(blank=True, verbose_name="Address")
    business_hours = models.TextField(blank=True, verbose_name="Business Hours")
    social_facebook = models.URLField(blank=True, verbose_name="Facebook URL")
    social_instagram = models.URLField(blank=True, verbose_name="Instagram URL")
    social_twitter = models.URLField(blank=True, verbose_name="Twitter URL")

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return "Contact Information"


class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Ekiane", verbose_name="Page Title")
    hero_title = models.CharField(max_length=200, default="Our Story", verbose_name="Hero Title")
    hero_subtitle = models.TextField(blank=True, verbose_name="Hero Subtitle")
    brand_story = models.TextField(verbose_name="Brand Story")
    mission = models.TextField(blank=True, verbose_name="Mission Statement")
    values = models.TextField(blank=True, verbose_name="Core Values")
    timeline = models.TextField(blank=True, verbose_name="Company Timeline")
    philosophy = models.TextField(blank=True, verbose_name="Beauty Philosophy")

    # Images
    hero_image = models.ImageField(upload_to='about/', blank=True, verbose_name="Hero Image")
    brand_image = models.ImageField(upload_to='about/', blank=True, verbose_name="Brand Image")
    timeline_image = models.ImageField(upload_to='about/', blank=True, verbose_name="Timeline Image")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Page Content"
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return self.title