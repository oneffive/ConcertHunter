from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ArtistSearchForm, SubscriptionForm
from .utils import get_tm_artist
from .models import Artist, Subscription
from .utils import get_tm_artist_details

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