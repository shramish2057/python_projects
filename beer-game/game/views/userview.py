from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
import datetime
import matplotlib.pyplot as plt
from io import StringIO

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from game.models import *
from game.forms import *


def registerPage(request):
    if request.method == "POST":
        form = ExtendedUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
                   
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
          
            return redirect('game:login')
    else:
        form = ExtendedUserCreationForm()
        profile_form = UserProfileForm()	
    
    context = {'form':form, 'profile_form': profile_form}
    return render(request, 'game/register.html', context)



def loginPage(request):
    if request.user.is_authenticated:
	    return redirect('game:home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password =request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('game:home')
            else:
                messages.info(request, 'Username OR password is incorrect')
        
        context = {}
        return render(request, 'game/login.html', context)



def logoutUser(request):
	logout(request)
	return redirect('game:login')


@login_required(login_url='game:login')
def home(request):
    game_created = Game.objects.filter(admin=request.user.userprofile)
    context={'game_created': game_created, 'user': request.user.userprofile}
    return render(request, 'game/main.html', context)

@login_required(login_url='game:login')
def assignedGames(request):
    list_roles = Role.objects.filter(userprofile=request.user.userprofile)
    context={'list_roles': list_roles, 'user': request.user.userprofile}
    return render(request, 'game/assignedGames.html', context)

@login_required(login_url='game:login')
def accountSettings(request):
    context={'user': request.user.userprofile}
    return render(request, 'game/accountSettings.html', context)