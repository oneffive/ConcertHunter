import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .forms import ArtistSearchForm, SubscriptionForm
from .utils import get_tm_artist, get_tm_artist_details
from .models import Artist, Subscription, Event
from deep_translator import GoogleTranslator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .utils import get_general_events_in_city
from .utils import get_tm_events

def artist_search(request):
    search_form = ArtistSearchForm()
    results = []

    if 'artist_name' in request.GET:
        search_form = ArtistSearchForm(request.GET)
        if search_form.is_valid():
            name = search_form.cleaned_data['artist_name']
            results = get_tm_artist(name)

    context = {
        'form': search_form,
        'results': results
    }
    return render(request, 'events/search.html', context)



@login_required
def subscribe(request, tm_id):
    artist_data = get_tm_artist_details(tm_id)
    
    if not artist_data:
        messages.error(request, "Не удалось получить данные об артисте.")
        return redirect('search')

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            raw_city = form.cleaned_data['city']

            try:
                city_english = GoogleTranslator(source='auto', target='en').translate(raw_city)
                city_english = city_english.strip().title()
            except Exception as e:
                print(f"Ошибка перевода: {e}")
                city_english = raw_city.strip().title()

            artist, created = Artist.objects.get_or_create(
                tm_id=artist_data['tm_id'],
                defaults={
                    'name': artist_data['name'],
                    'image_url': artist_data['image_url']
                }
            )

            sub, sub_created = Subscription.objects.get_or_create(
                user=request.user,
                artist=artist,
                city=city_english
            )

            if sub_created:
                messages.success(request, f"Вы подписались на {artist.name} в городе {city_english}!")
                
                
                print(f"Мгновенный поиск событий для {artist.name} в {city_english}...")
                new_events_data = get_tm_events(artist.tm_id, city_english)
                
                count = 0
                for event_item in new_events_data:
                    
                    if not Event.objects.filter(tm_event_id=event_item['tm_event_id']).exists():
                        Event.objects.create(
                            artist=artist,
                            name=event_item['name'],
                            date=event_item['date'],
                            venue_name=event_item['venue_name'],
                            city=event_item['city'],
                            latitude=event_item['latitude'],
                            longitude=event_item['longitude'],
                            ticket_url=event_item['ticket_url'],
                            tm_event_id=event_item['tm_event_id']
                        )
                        count += 1
                
                if count > 0:
                    messages.success(request, f"Найдено {count} концертов! Они добавлены в ваш календарь.")
                else:
                    messages.warning(request, "Подписка создана, но концертов пока не найдено.")
                

            else:
                messages.info(request, f"Вы уже подписаны на этого артиста в городе {city_english}.")
            
            return redirect('search')
    else:
        form = SubscriptionForm()

    context = {
        'form': form,
        'artist': artist_data
    }
    return render(request, 'events/subscribe.html', context)

@login_required
def dashboard(request):
    user_subscriptions = Subscription.objects.filter(user=request.user, is_active=True)
    
    q_objects = Q()
    for sub in user_subscriptions:
       
        q_objects |= Q(artist=sub.artist, city__iexact=sub.city)

    if user_subscriptions.exists():
        events = Event.objects.filter(q_objects, date__gte=timezone.now()).order_by('date')
    else:
        events = Event.objects.none()
    
    map_data = []
    for event in events:
        if event.latitude and event.longitude:
            map_data.append({
                'lat': event.latitude,
                'lon': event.longitude,
                'title': f"{event.artist.name} - {event.name}",
                'date': event.date.strftime('%d.%m.%Y %H:%M'),
                'city': event.city,
                'venue': event.venue_name,
                'ticket_url': event.ticket_url,
            })

    context = {
        'events': events,
        'map_data_json': json.dumps(map_data),
        'subscriptions': user_subscriptions
    }
    return render(request, 'events/dashboard.html', context)

@login_required
def delete_subscription(request, sub_id):
    subscription = get_object_or_404(Subscription, id=sub_id, user=request.user)
    
    artist_name = subscription.artist.name
    subscription.delete()
    
    messages.success(request, f"Подписка на {artist_name} удалена.")
    return redirect('dashboard')
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})
@login_required
def delete_event(request, event_id):
    
    event = get_object_or_404(Event, id=event_id)
    
    
    event.delete()
    
    messages.success(request, "Событие удалено из ленты.")
    return redirect('dashboard')
@login_required
def city_events(request, city_name):
    
    genre_filter = request.GET.get('genre', 'Music') 
    date_filter = request.GET.get('date', '')

    
    events = get_general_events_in_city(city_name, genre=genre_filter, start_date=date_filter)

    context = {
        'city': city_name,
        'events': events,
        'current_genre': genre_filter,
        'current_date': date_filter
    }
    return render(request, 'events/city_events.html', context)