from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ArtistSearchForm, SubscriptionForm
from .utils import get_tm_artist
from .models import Artist, Subscription

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
   
    return redirect('search')