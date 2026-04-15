import requests
import time

base_url = 'http://127.0.0.1:8000'
pages = ['/accounts/login/', '/accounts/signup/', '/accounts/logout/']

for page in pages:
    try:
        response = requests.get(base_url + page, timeout=10)
        print(f'{page}: Status {response.status_code}, Content length: {len(response.text)} chars')
        if 'min-height' in response.text:
            print(f'  WARNING: Found min-height in {page}')
        if 'height: 100%' in response.text:
            print(f'  WARNING: Found height: 100% in {page}')
    except Exception as e:
        print(f'{page}: Error - {e}')
    time.sleep(1)