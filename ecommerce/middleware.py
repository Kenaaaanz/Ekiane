# middleware.py
from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class DomainRedirectMiddleware:
    """
    Middleware to redirect old domain (ekianeonsare.shop) to new domain (ekianeonsare.com)
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure your domains here
        self.old_domains = [
            'ekianeonsare.shop',
            'www.ekianeonsare.shop',
            'ekianeonsare.shop:8000',  # If running on different port
        ]
        self.new_domain = 'ekianeonsare.com'
        self.new_domain_www = f'www.{self.new_domain}'

    def __call__(self, request):
        host = request.get_host().lower()
        
        # Check if this is a request to the old domain
        if any(host == old_domain or host.startswith(old_domain) for old_domain in self.old_domains):
            # Build the new URL with the same path and query string
            new_url = f'https://{self.new_domain}{request.get_full_path()}'
            return HttpResponsePermanentRedirect(new_url)
        
        # Also handle www vs non-www for the new domain (choose your preferred version)
        if host.startswith('www.'):
            # Option A: Redirect www to non-www
            new_url = f'https://{self.new_domain}{request.get_full_path()}'
            return HttpResponsePermanentRedirect(new_url)
        
        return self.get_response(request)