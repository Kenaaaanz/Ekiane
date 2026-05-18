
from django.http import HttpResponsePermanentRedirect
from django.urls import resolve

class DomainRedirectMiddleware:
    """
    Safe domain redirect - ONLY redirects from old .shop domain to new .com domain
    No redirects for www vs non-www - let the web server handle that
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Only redirect from these exact old domains
        self.old_domains = {'ekianeonsare.shop', 'www.ekianeonsare.shop'}
        self.new_domain = 'ekianeonsare.com'

    def __call__(self, request):
        # Get host without port number
        host = request.get_host().split(':')[0].lower()
        
        # Check if this is a request to the OLD domain
        if host in self.old_domains:
            # Build the new URL preserving path and query string
            new_url = f'https://{self.new_domain}{request.get_full_path()}'
            return HttpResponsePermanentRedirect(new_url)
        
        # For new domain, just pass through - NO REDIRECTS!
        return self.get_response(request)