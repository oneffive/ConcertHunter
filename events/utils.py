import requests
from django.conf import settings

def get_tm_artist(artist_name):
    
    url = "https://app.ticketmaster.com/discovery/v2/attractions.json"
    params = {
        'apikey': settings.TM_API_KEY,
        'keyword': artist_name,
        'classificationName': 'music',  
        'size': 5  
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        
        if '_embedded' not in data:
            return []

        artists_data = []
        for item in data['_embedded']['attractions']:
            image_url = ""
            if 'images' in item:
                
                image_url = item['images'][0]['url']

            artists_data.append({
                'name': item['name'],
                'tm_id': item['id'],
                'image_url': image_url,
                'external_url': item.get('url', '')
            })
        
        return artists_data

    except requests.RequestException as e:
        print(f"Error fetching data from TM: {e}")
        return []