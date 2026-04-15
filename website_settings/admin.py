from django.contrib import admin
from .models import ContactInfo, AboutPage

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Contact Details', {
            'fields': ('email', 'phone', 'address', 'business_hours')
        }),
        ('Social Media', {
            'fields': ('social_facebook', 'social_instagram', 'social_twitter'),
            'classes': ('collapse',)
        }),
    )
    list_display = ('email', 'phone')

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Page Settings', {
            'fields': ('title', 'hero_title', 'hero_subtitle')
        }),
        ('Content', {
            'fields': ('brand_story', 'mission', 'values', 'timeline', 'philosophy')
        }),
        ('Images', {
            'fields': ('hero_image', 'brand_image', 'timeline_image'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('title', 'updated_at')