from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ArtistSearchForm, SubscriptionForm
from .utils import get_tm_artist
from .utils import get_tm_artist_details
import json 
from django.db.models import Q 
from django.utils import timezone
from .models import Artist, Subscription, Event

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
        messages.error(request, "Не удалось получить данные об артисте")
        return redirect('search')

    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']

            
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
                city=city
            )

            if sub_created:
                messages.success(request, f"Вы подписались на {artist.name} в городе {city}")
            else:
                messages.info(request, "Вы уже подписаны на этого артиста в этом городе")
            
            return redirect('search')
    else:
        form = SubscriptionForm()

    context = {
        'form': form,
        'artist': artist_data
    }
    return render(request, 'events/subscribe.html', context)

def dashboard(request):
    
    user_subscriptions = Subscription.objects.filter(user=request.user, is_active=True)
    
    
    q_objects = Q()
    for sub in user_subscriptions:
        q_objects |= Q(artist=sub.artist, city=sub.city) 

    
    events = Event.objects.filter(q_objects, date__gte=timezone.now()).order_by('date')
    
    
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
        'map_data_json': json.dumps(map_data) 
    }
    return render(request, 'events/dashboard.html', context)