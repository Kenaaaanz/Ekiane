from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import ContactInfo, AboutPage

@staff_member_required
def website_settings(request):
    """Main website settings page"""
    contact_info, created = ContactInfo.objects.get_or_create(id=1)
    about_page, created = AboutPage.objects.get_or_create(id=1)

    if request.method == 'POST':
        # Handle contact info update
        if 'contact_submit' in request.POST:
            contact_info.email = request.POST.get('email', '')
            contact_info.phone = request.POST.get('phone', '')
            contact_info.address = request.POST.get('address', '')
            contact_info.business_hours = request.POST.get('business_hours', '')
            contact_info.social_facebook = request.POST.get('social_facebook', '')
            contact_info.social_instagram = request.POST.get('social_instagram', '')
            contact_info.social_twitter = request.POST.get('social_twitter', '')
            contact_info.save()
            messages.success(request, 'Contact information updated successfully.')

        # Handle about page update
        elif 'about_submit' in request.POST:
            about_page.title = request.POST.get('title', '')
            about_page.hero_title = request.POST.get('hero_title', '')
            about_page.hero_subtitle = request.POST.get('hero_subtitle', '')
            about_page.brand_story = request.POST.get('brand_story', '')
            about_page.mission = request.POST.get('mission', '')
            about_page.values = request.POST.get('values', '')
            about_page.timeline = request.POST.get('timeline', '')
            about_page.philosophy = request.POST.get('philosophy', '')

            # Handle image uploads
            if request.FILES.get('hero_image'):
                about_page.hero_image = request.FILES['hero_image']
            if request.FILES.get('brand_image'):
                about_page.brand_image = request.FILES['brand_image']
            if request.FILES.get('timeline_image'):
                about_page.timeline_image = request.FILES['timeline_image']

            about_page.save()
            messages.success(request, 'About page content updated successfully.')

        return redirect('website_settings:settings')

    context = {
        'contact_info': contact_info,
        'about_page': about_page,
    }
    return render(request, 'website_settings/settings.html', context)