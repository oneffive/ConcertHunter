import requests
import time
import unicodedata  
from django.conf import settings
from deep_translator import GoogleTranslator

def normalize_text(text):
    
    if not text:
        return ""
    
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
    except:
        translated = text
    
    
    normalized = unicodedata.normalize('NFKD', translated).encode('ASCII', 'ignore').decode('utf-8')
    return normalized.strip().title()

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
        if '_embedded' not in data: return []

        artists_data = []
        for item in data['_embedded']['attractions']:
            image_url = item['images'][0]['url'] if 'images' in item else ""
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

def get_tm_artist_details(tm_id):
    
    url = f"https://app.ticketmaster.com/discovery/v2/attractions/{tm_id}.json"
    params = {'apikey': settings.TM_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        image_url = data['images'][0]['url'] if 'images' in data else ""
        return {
            'tm_id': data['id'],
            'name': data['name'],
            'image_url': image_url,
            'external_url': data.get('url', '')
        }
    except Exception as e:
        print(f"Error fetching details: {e}")
        return None

def get_tm_events(artist_tm_id, city):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        'apikey': settings.TM_API_KEY,
        'attractionId': artist_tm_id,
        'city': city,
        'sort': 'date,asc',
        'size': 20,
    }

    try:
        time.sleep(0.5)
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if '_embedded' not in data or 'events' not in data['_embedded']:
            return []

        events_list = []
        for event_item in data['_embedded']['events']:
            venue_name = ""
            raw_city_name = city
            latitude = None
            longitude = None

            if '_embedded' in event_item and 'venues' in event_item['_embedded']:
                venue = event_item['_embedded']['venues'][0]
                venue_name = venue.get('name', 'Неизвестная площадка')
                
                
                raw_city_name = venue.get('city', {}).get('name', city)
                
                location = venue.get('location', {})
                if 'latitude' in location:
                    latitude = float(location['latitude'])
                if 'longitude' in location:
                    longitude = float(location['longitude'])
            
            
            final_city = normalize_text(raw_city_name)
           

            ticket_status = event_item.get('dates', {}).get('status', {}).get('code', 'unknown')
            start_dates = event_item.get('dates', {}).get('start', {})
            event_date_str = start_dates.get('dateTime')

            
            if not event_date_str:
                local_date = start_dates.get('localDate')
                if local_date:
                    event_date_str = f"{local_date}T00:00:00Z"
                else:
                    continue 
            events_list.append({
                'tm_event_id': event_item['id'],
                'name': event_item['name'],
                'date': event_date_str,
                'venue_name': venue_name,
                'city': final_city, 
                'latitude': latitude,
                'longitude': longitude,
                'ticket_url': event_item.get('url', '#'),
                'ticket_status': ticket_status
            })
        return events_list

    except requests.RequestException as e:
        print(f"Error fetching events from TM: {e}")
        return []
def get_general_events_in_city(city, genre=None, start_date=None):
    
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    params = {
        'apikey': settings.TM_API_KEY,
        'city': city,
        'sort': 'date,asc',
        'size': 20,
    }

   
    if genre and genre != 'All':
        params['classificationName'] = genre  
    
    if start_date:
        
        params['startDateTime'] = f"{start_date}T00:00:00Z"

    try:
        time.sleep(0.5)
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if '_embedded' not in data or 'events' not in data['_embedded']:
            return []

        events_list = []
        for event_item in data['_embedded']['events']:
            
            
            image_url = ""
            if 'images' in event_item:
                image_url = event_item['images'][0]['url']

            venue_name = "Unknown Venue"
            if '_embedded' in event_item and 'venues' in event_item['_embedded']:
                venue_name = event_item['_embedded']['venues'][0].get('name', '')

            events_list.append({
                'name': event_item['name'],
                'date': event_item['dates']['start'].get('localDate', 'TBA'),
                'time': event_item['dates']['start'].get('localTime', ''),
                'venue': venue_name,
                'image_url': image_url,
                'ticket_url': event_item.get('url', '#'),
                'genre': event_item['classifications'][0]['segment']['name'] if 'classifications' in event_item else 'Unknown'
            })
        return events_list

    except requests.RequestException as e:
        print(f"Error fetching city events: {e}")
        return []