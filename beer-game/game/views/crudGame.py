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


#length of round in minutes
round_length = 3


@login_required(login_url='game:login')
def createGame(request):
    if request.method == "POST":
        form1 = GameCreationForm(request.POST)
        form2 = ExtendedGameCreationForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            # get the data from the forms
            retailer = form2.cleaned_data.get("retailer")
            wholesaler = form2.cleaned_data.get("wholesaler")
            distributor = form2.cleaned_data.get("distributor")
            factory = form2.cleaned_data.get("factory")

            isDistributor = form1.cleaned_data['distributor_present']
            isWholesaler = form1.cleaned_data['wholesaler_present']
            startingInventory = form1.cleaned_data['starting_inventory']
            nrRounds = form1.cleaned_data['nr_rounds']


            # ## check for the errors
            # # check if we have selected more than specified
            if(isDistributor==False and distributor):
                messages.info(request, 'Distributor is not selected')
                return render(request, 'game/createGame.html', {})
            if(isWholesaler==False and wholesaler):
                messages.info(request, 'Wholesaler is not selected')
                return render(request, 'game/createGame.html', {})
            


            # #if no errors than save the game, set the admin
            game = form1.save(commit = False)
            user31 = UserProfile.objects.get(user_id=request.user.id)
            game.admin = user31
            game.save()


            #create the respective roles and specify the relationship between them
            r1 = r2 = r3 = r4 = None
            
            r1 = Role(role_name="retailer")
            r1.save()
            r4 = Role(role_name="factory")
            r4.save()
            if isWholesaler:
                r2 = Role(role_name="wholesaler")
                r2.save()
                r2.downstream_player = r1.id
                r1.upstream_player = r2.id
                if isDistributor:
                    r3 = Role(role_name="distributor")
                    r3.save()
                    r3.downstream_player = r2.id
                    r2.upstream_player = r3.id
                    r4.downstream_player = r3.id
                    r3.upstream_player = r4.id
                else:
                    r4.downstream_player = r2.id
                    r2.upstream_player = r4.id
            else:
                if isDistributor:
                    r3 = Role(role_name="distributor")
                    r3.save()
                    r3.downstream_player = r1.id
                    r1.upstream_player = r3.id
                    r3.upstream_player = r4.id
                    r4.downstream_player = r3.id
                else:
                    r1.upstream_player = r4.id
                    r4.downstream_player = r1.id
            
            r1.save()
            if(r2): r2.save()
            if(r3): r3.save()
            r4.save()

            #add the roles to the userProfile and the game
            user1 = UserProfile.objects.get(user__pk=retailer.id)
            user1.roles.add(r1)
            user4 = UserProfile.objects.get(user__pk=factory.id)
            user4.roles.add(r4)
            game.roles.add(r1, r4)

            if r2 != None:
                user2 = UserProfile.objects.get(user__pk=wholesaler.id)
                user2.roles.add(r2)
                game.roles.add(r2)
            if r3 != None:
                user3 = UserProfile.objects.get(user__pk=distributor.id)
                user3.roles.add(r3)
                game.roles.add(r3)


            #create the weeks, with the respective times, number and starting inventory
            # and add them to the role
            for i in range(nrRounds):
                if i == 0:
                    week1 = Week(date=timezone.now()+datetime.timedelta(weeks=(i+5)*3), number= i+1, inventory=startingInventory)
                else:
                    week1 = Week(date=timezone.now()+datetime.timedelta(weeks=(i+5)*3), number= i+1)
                week1.save()
                r1.weeks.add(week1)
                if(r2): 
                    if i == 0:
                        week2 = Week(date=timezone.now()+datetime.timedelta(weeks=(i+5)*3), number= i+1, inventory=startingInventory)
                    else:
                        week2 = Week(date=timezone.now()+datetime.timedelta(weeks=(i+5)*3), number= i+1)
                    week2.save()
                    r2.weeks.add(week2)
                if(r3):
                    if i == 0:
                        week3 = Week(date=timezone.now()+datetime.timedelta(weeks= (i+5)*3), number= i+1, inventory=startingInventory)
                    else:
                        week3 = Week(date=timezone.now()+datetime.timedelta(weeks= (i+5)*3), number = i+1)
                    week3.save()
                    r3.weeks.add(week3)
                if i == 0:
                    week4 = Week(date=timezone.now()+datetime.timedelta(weeks=(i+5)*3), number= i+1, inventory=startingInventory)
                else:
                    week4 = Week(date=timezone.now()+datetime.timedelta(weeks=(i+5)*3), number= i+1)
                week4.save()
                r4.weeks.add(week4)
    
            return HttpResponseRedirect(reverse('game:demand', args=(game.id,)))
    else:
        form2 = ExtendedGameCreationForm()
        form1 = GameCreationForm()	
    
    context = {'form1':form1, 'form2':form2, 'user': request.user.userprofile}
    return render(request, 'game/createGame.html', context)


@login_required(login_url='game:login')
def createDemand(request, game_id):
    game = Game.objects.get(pk=game_id)
    if request.method == "POST":
        text = request.POST['demand']
        demands = text.split(", ")
        if len(demands) != game.nr_rounds:
            messages.info(request, 'You have not specified all rounds')
            return HttpResponseRedirect(reverse('game:demand', args=(game_id,)))
        
        k=1
        for customer_demand in demands:
            week1 = Week.objects.get(role__game=game, number=k, role__role_name="retailer")
            week1.demand = customer_demand
            week1.save()
            k+=1
        return redirect('game:home')

    context = {'game': game, 'user': request.user.userprofile}
    return render(request, 'game/demandPattern.html', context)

@login_required(login_url='game:login')
def deleteGame(request, game_id):
    # delete all the related roles, weeks related to the game
    game = Game.objects.get(pk=game_id)
    roles = Role.objects.filter(game__id = game_id)
    
    for role in roles:
        weeks = Week.objects.filter(role__id=role.id)
        for week in weeks:
            week.delete()
        role.delete()
    game.delete()
    return redirect('game:home')

# tbd
@login_required(login_url='game:login')
def updateGame(request, game_id):
    game = Game.objects.get(pk = game_id)
    rounds_remaining_prev = game.nr_rounds - game.rounds_completed
    nr_rounds_prev = game.nr_rounds
    distributor_present_prev = game.distributor_present
    wholesaler_present_prev = game.wholesaler_present
    is_active_prev = game.is_active
    if request.method == "POST":
        form = GameUpdateForm(request.POST, instance=game)
        form2 = ExtendedGameUpdateForm(request.POST)
        if form.is_valid() and form2.is_valid():
            #check whether enough fields are specified in the demands pattern
            #other fields are checked by form validation
            text = request.POST.get("demands", "1, 2")
            demands = text.split(", ")
            rounds_remaining_new = game.nr_rounds - game.rounds_completed
            if len(demands) != rounds_remaining_new:
                messages.info(request, 'You have not specified all remaining rounds')
                return HttpResponseRedirect(reverse('game:updateGame', args=(game_id,)))
            
            print(game.info_delay)
            #if no errors then the settings of the game should be updated accordingly
            distributor_present_new = game.distributor_present
            wholesaler_present_new = game.wholesaler_present
            nr_rounds_new = game.nr_rounds
            current_round = game.rounds_completed
            retailer = Role.objects.get(game__id = game_id, role_name= 'retailer')
            factory = Role.objects.get(game__id = game_id, role_name='factory')
            
            #add the number of weeks to the retailer and factory (always existing) if nr_rounds changed
            if nr_rounds_new != nr_rounds_prev:
                last_week_prev = Week.objects.get(role__game__id = game_id, number=nr_rounds_prev, role__role_name= 'retailer')
                j = 1
                for i in range(nr_rounds_prev+1, nr_rounds_new+1):
                    new_week_retailer = Week(date = last_week_prev.date + datetime.timedelta(minutes=j*round_length),number=i)
                    new_week_factory = Week(date=last_week_prev.date + datetime.timedelta(minutes=j*round_length), number=i)
                    new_week_retailer.save()
                    retailer.weeks.add(new_week_retailer)
                    new_week_factory.save()
                    factory.weeks.add(new_week_factory)
                    j+=1
            
            #change the relationships between roles, nr weeks for distributor and wholesaler accordingly
            if wholesaler_present_new == wholesaler_present_prev and distributor_present_new == distributor_present_prev:
                #no change done, only add the nr of weeks
                if (distributor_present_new == True):
                    distributor = Role.objects.get(game__id = game_id, role_name = 'distributor')
                if (wholesaler_present_new == True):
                    wholesaler = Role.objects.get(game__id = game_id , role_name = 'wholesaler')
                for i in range(nr_rounds_prev+1, nr_rounds_new+1):
                    if distributor_present_new == True:
                        new_week_distributor = Week(date = last_week_prev.date + datetime.timedelta(minutes=j*round_length),number=i)
                        new_week_distributor.save()
                        distributor.weeks.add(new_week_distributor)
                    if wholesaler_present_new == True:
                        new_week_wholesaler = Week(date=last_week_prev.date + datetime.timedelta(minutes=j*round_length), number=i)
                        new_week_wholesaler.save()
                        wholesaler.weeks.add(new_week_wholesaler)
                    j+=1
            
            else:
                #the options are changed, prev != new
                ######  ///////////////
                ###### 1st existing case
                ###### \\\\\\\\\\\\\\\\\\
                if wholesaler_present_prev == True and distributor_present_prev == True:
                    if wholesaler_present_new == True and distributor_present_new == False:
                        #delete everything from distributor
                        all_weeks_distributor = Week.objects.filter(role__game__id = game_id, role__role_name='distributor')
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        for week in all_weeks_distributor:
                            week.delete()
                        distributor.delete()
                        #change the relation
                        factory.downstream_player = wholesaler.id
                        wholesaler.upstream_player = factory.id
                        factory.save()
                        wholesaler.save()
                        j = 0
                        #add the weeks to the wholesaler if nr rounds changed
                        if nr_rounds_prev != nr_rounds_new:
                            for i in range(nr_rounds_prev+1, nr_rounds_new+1):
                                new_week_wholesaler = Week(date=last_week_prev.date + datetime.timedelta(minutes=j*round_length), number=i)
                                new_week_wholesaler.save()
                                wholesaler.weeks.add(new_week_wholesaler)
                                j+=1
                        
                    elif wholesaler_present_new == False and distributor_present_new == True:
                        #delete everything from wholesaler
                        all_weeks_wholesaler = Week.objects.filter(role__game__id = game_id, role__role_name='wholesaler')
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        for week in all_weeks_wholesaler:
                            week.delete()
                        wholesaler.delete()
                        #change the relation
                        distributor.downstream_player = retailer.id
                        retailer.upstream_player = distributor.id
                        retailer.save()
                        distributor.save()
                        j = 0
                        #add the weeks to the distributor if nr rounds changed
                        if nr_rounds_prev != nr_rounds_new:
                            for i in range(nr_rounds_prev+1, nr_rounds_new+1):
                                new_week_distributor = Week(date=last_week_prev.date + datetime.timedelta(minutes=j*round_length), number=i)
                                new_week_distributor.save()
                                distributor.weeks.add(new_week_distributor)
                                j+=1
                    else:
                        #both of them are removed
                        all_weeks_wholesaler = Week.objects.filter(role__game__id = game_id, role__role_name='wholesaler')
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        for week in all_weeks_wholesaler:
                            week.delete()
                        wholesaler.delete()
                        all_weeks_distributor = Week.objects.filter(role__game__id = game_id, role__role_name='distributor')
                        for week in all_weeks_distributor:
                            week.delete()
                        distributor.delete()
                        #change the relation
                        factory.downstream_player = retailer.id
                        retailer.upstream_player = factory.id
                        factory.save()
                        retailer.save()
                

                ######  ///////////////
                ###### 2nd existing case
                ###### \\\\\\\\\\\\\\\\\\
                elif wholesaler_present_prev == True and distributor_present_prev == False:
                    if distributor_present_new == True and wholesaler_present_new == True:
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        distributor_user = form2.cleaned_data['distributor']
                        distributor_role_new = Role(role_name='distributor')
                        distributor_role_new.downstream_player = wholesaler.id
                        distributor_role_new.upstream_player = factory.id
                        distributor_role_new.save()
                        factory.downstream_player = distributor_role_new.id
                        wholesaler.upstream_player = distributor_role_new.id
                        wholesaler.save()
                        factory.save()

                        #add the new role to the user and game
                        user1 = UserProfile.objects.get(user__pk=distributor_user.id)
                        user1.roles.add(distributor_role_new)
                        game.roles.add(distributor_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_distributor = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_distributor.save()
                            distributor_role_new.weeks.add(new_week_distributor)
                            j+=1
                        
                        #add the weeks to the wholsaler if the nr rounds changed
                        j = 0
                        if nr_rounds_prev != nr_rounds_new:
                            for i in range(nr_rounds_prev+1, nr_rounds_new+1):
                                new_week_wholesaler = Week(date=last_week_prev.date + datetime.timedelta(minutes=j*round_length), number=i)
                                new_week_wholesaler.save()
                                wholesaler.weeks.add(new_week_wholesaler)
                                j+=1
                    
                    elif distributor_present_new == False and wholesaler_present_new == False:
                        #delete everything from the existing wholesaler
                        all_weeks_wholesaler = Week.objects.filter(role__game__id = game_id, role__role_name='wholesaler')
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        for week in all_weeks_wholesaler:
                            week.delete()
                        wholesaler.delete()

                        #change the relation
                        factory.downstream_player = retailer.id
                        retailer.upstream_player = factory.id
                        factory.save()
                        retailer.save()

                    else:
                        #create distributor, delete wholesaler
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        distributor_user = form2.cleaned_data['distributor']
                        distributor_role_new = Role(role_name='distributor')
                        #roles must be changed accordingly
                        distributor_role_new.downstream_player = retailer.id
                        distributor_role_new.upstream_player = factory.id
                        distributor_role_new.save()
                        factory.downstream_player = distributor_role_new.id
                        retailer.upstream_player = distributor_role_new.id
                        retailer.save()
                        factory.save()

                        #add the new role to the user and game
                        user1 = UserProfile.objects.get(user__pk=distributor_user.id)
                        user1.roles.add(distributor_role_new)
                        game.roles.add(distributor_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks for the distributor
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_distributor = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_distributor.save()
                            distributor_role_new.weeks.add(new_week_distributor)
                            j+=1
                        
                        #delete everything from the existing wholesaler
                        all_weeks_wholesaler = Week.objects.filter(role__game__id = game_id, role__role_name='wholesaler')
                        wholesaler = Role.objects.get(game__id = game_id, role_name='wholesaler')
                        for week in all_weeks_wholesaler:
                            week.delete()
                        wholesaler.delete()

                ######  ///////////////
                ###### 3rd existing case
                ###### \\\\\\\\\\\\\\\\\\
                elif wholesaler_present_prev == False and distributor_present_prev == True:
                    if distributor_present_new == True and wholesaler_present_new == True:
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        wholesaler_user = form2.cleaned_data['wholesaler']
                        wholesaler_role_new = Role(role_name='wholesaler')
                        wholesaler_role_new.downstream_player = retailer.id
                        wholesaler_role_new.upstream_player = distributor.id
                        wholesaler_role_new.save()
                        retailer.upstream_player = wholesaler_role_new.id
                        distributor.downstream_player = wholesaler_role_new.id
                        distributor.save()
                        retailer.save()

                        #add the new role to the user and game
                        user1 = UserProfile.objects.get(user__pk=wholesaler_user.id)
                        user1.roles.add(wholesaler_role_new)
                        game.roles.add(wholesaler_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_wholesaler = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_wholesaler.save()
                            wholesaler_role_new.weeks.add(new_week_wholesaler)
                            j+=1
                        
                        #add the weeks to the existing distributor if the nr rounds changed
                        j = 0
                        if nr_rounds_prev != nr_rounds_new:
                            for i in range(nr_rounds_prev+1, nr_rounds_new+1):
                                new_week_distributor = Week(date=last_week_prev.date + datetime.timedelta(minutes=j*round_length), number=i)
                                new_week_distributor.save()
                                distributor.weeks.add(new_week_distributor)
                                j+=1
                    
                    elif distributor_present_new == False and wholesaler_present_new == False:
                        #delete everything from the existing distributor
                        all_weeks_distributor = Week.objects.filter(role__game__id = game_id, role__role_name='distributor')
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        for week in all_weeks_distributor:
                            week.delete()
                        distributor.delete()

                        #change the relation
                        factory.downstream_player = retailer.id
                        retailer.upstream_player = factory.id
                        factory.save()
                        retailer.save()

                    else:
                        #create wholesaler, delete the existing distributor
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        wholesaler_user = form2.cleaned_data['wholesaler']
                        wholesaler_role_new = Role(role_name='wholesaler')
                        #roles must be changed accordingly
                        wholesaler_role_new.downstream_player = retailer.id
                        wholesaler_role_new.upstream_player = factory.id
                        wholesaler_role_new.save()
                        factory.downstream_player = wholesaler_role_new.id
                        retailer.upstream_player = wholesaler_role_new.id
                        retailer.save()
                        factory.save()

                        #add the new role to the user and game
                        user1 = UserProfile.objects.get(user__pk=wholesaler_user.id)
                        user1.roles.add(wholesaler_role_new)
                        game.roles.add(wholesaler_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks for the wholesaler
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_wholesaler = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_wholesaler.save()
                            wholesaler_role_new.weeks.add(new_week_wholesaler)
                            j+=1
                        
                        #delete everything from the existing distributor
                        all_weeks_distributor = Week.objects.filter(role__game__id = game_id, role__role_name='distributor')
                        distributor = Role.objects.get(game__id = game_id, role_name='distributor')
                        for week in all_weeks_distributor:
                            week.delete()
                        distributor.delete()
                ######  ///////////////
                ###### 4th existing case
                ###### \\\\\\\\\\\\\\\\\\
                elif wholesaler_present_prev == False and distributor_present_prev == False:
                    if distributor_present_new == True and wholesaler_present_new == False:
                        distributor_user = form2.cleaned_data['distributor']
                        distributor_role_new = Role(role_name='distributor')
                        distributor_role_new.downstream_player = retailer.id
                        distributor_role_new.upstream_player = factory.id
                        distributor_role_new.save()
                        factory.downstream_player = distributor_role_new.id
                        retailer.upstream_player = distributor_role_new.id
                        retailer.save()
                        factory.save()

                        #add the new role to the user and game
                        user1 = UserProfile.objects.get(user__pk=distributor_user.id)
                        user1.roles.add(distributor_role_new)
                        game.roles.add(distributor_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_distributor = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_distributor.save()
                            distributor_role_new.weeks.add(new_week_distributor)
                            j+=1
                    
                    elif distributor_present_new == False and wholesaler_present_new == True:
                        #add wholesaler
                        wholesaler_user = form2.cleaned_data['wholesaler']
                        wholesaler_role_new = Role(role_name='wholesaler')
                        wholesaler_role_new.downstream_player = retailer.id
                        wholesaler_role_new.upstream_player = factory.id
                        wholesaler_role_new.save()
                        factory.downstream_player = wholesaler_role_new.id
                        retailer.upstream_player = wholesaler_role_new.id
                        retailer.save()
                        factory.save()

                        #add the new role to the user and game
                        user1 = UserProfile.objects.get(user__pk=wholesaler_user.id)
                        user1.roles.add(wholesaler_role_new)
                        game.roles.add(wholesaler_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_wholesaler = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_wholesaler.save()
                            wholesaler_role_new.weeks.add(new_week_wholesaler)
                            j+=1

                    else:
                        #both of them are added
                        distributor_user = form2.cleaned_data['distributor']
                        distributor_role_new = Role(role_name='distributor')
                        wholesaler_user = form2.cleaned_data['wholesaler']
                        wholesaler_role_new = Role(role_name='wholesaler')
                        distributor_role_new.save()
                        wholesaler_role_new.save()



                        distributor_role_new.downstream_player = wholesaler_role_new.id
                        distributor_role_new.upstream_player = factory.id
                        
                        wholesaler_role_new.downstream_player = retailer.id
                        wholesaler_role_new.upstream_player = distributor_role_new.id
                        
                        factory.downstream_player = distributor_role_new.id
                        retailer.upstream_player = wholesaler_role_new.id
                        retailer.save()
                        factory.save()

                        if(wholesaler_role_new):
                            wholesaler_role_new.save()
                        if(distributor_role_new):
                            distributor_role_new.save()


                        #add the new role to the user and game
                        user2 = UserProfile.objects.get(user__pk=wholesaler_user.id)
                        user2.roles.add(wholesaler_role_new)
                        user1 = UserProfile.objects.get(user__pk=distributor_user.id)
                        user1.roles.add(distributor_role_new)

                        game.roles.add(distributor_role_new, wholesaler_role_new)

                        if current_round == 0:
                            weeknr = 1
                        else:
                            weeknr = current_round
                        
                        current_week = Week.objects.get(role__game__id = game_id, number=weeknr, role__role_name='retailer')
                        #create the corresponding weeks
                        j = 0
                        if (current_round == 0):
                            current_round = 1
                        for i in range(current_round, nr_rounds_new+1):
                            new_week_distributor = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_distributor.save()
                            distributor_role_new.weeks.add(new_week_distributor)
                            new_week_wholesaler = Week(date=current_week.date + datetime.timedelta(minutes=j*round_length), number=i)
                            new_week_wholesaler.save()
                            wholesaler_role_new.weeks.add(new_week_wholesaler)
                            j+=1
                        
            
            

            #add the demand to the retailer according to the demand pattern specified
            k=game.rounds_completed + 1
            for customer_demand in demands:
                week1 = Week.objects.get(role__game=game, number=k, role__role_name="retailer")
                week1.demand = customer_demand
                week1.save()
                k+=1
            
            #change the date if the game is active(you can call start game)
            if(is_active_prev == False and game.is_active==True):
                return HttpResponseRedirect(reverse('game:startGame', args=(game_id,)))



            form.save()
            # return HttpResponseRedirect(reverse('game:updateGame', args=(game_id,)))
            return redirect('game:home')
    else:
        form = GameUpdateForm(instance = game)
        retailer_user = User.objects.get(userprofile__roles__game__id = game_id, userprofile__roles__role_name='retailer')
        factory_user = User.objects.get(userprofile__roles__game__id = game_id, userprofile__roles__role_name='factory')
        if(game.wholesaler_present):
            wholesaler_user = User.objects.get(userprofile__roles__game__id = game_id, userprofile__roles__role_name='wholesaler')
            if(game.distributor_present):
                distributor_user = User.objects.get(userprofile__roles__game__id = game_id, userprofile__roles__role_name='distributor')
                form2 = ExtendedGameUpdateForm(initial={
                    'retailer':retailer_user,
                    'wholesaler':wholesaler_user, 
                    'distributor': distributor_user,
                    'factory':factory_user})
            else:
                print("aaa")
                form2 = ExtendedGameUpdateForm(initial={
                    'retailer':retailer_user,
                    'wholesaler':wholesaler_user, 
                    'factory':factory_user})
        else:
            if game.distributor_present:
                distributor_user = User.objects.get(userprofile__roles__game__id = game_id, userprofile__roles__role_name='distributor')
                form2 = ExtendedGameUpdateForm(initial={
                    'retailer':retailer_user,
                    'distributor': distributor_user,
                    'factory':factory_user})
            else: 
                form2 = ExtendedGameUpdateForm(initial={
                    'retailer':retailer_user,
                    'factory':factory_user})
            
    context = {'form':form,'form2':form2,  'game':game, 'rounds_remaining_prev': rounds_remaining_prev}
    return render(request, 'game/updateGame.html', context)

@login_required(login_url='game:login')
def startGame(request, game_id):
    game = Game.objects.get(pk = game_id)
    all_weeks = Week.objects.filter(role__game__id=game_id)
    for week in all_weeks:
        week.date = timezone.now()+datetime.timedelta(minutes=round_length*(week.number-1))
        week.save()
    game.is_active = True
    game.save()
    print(timezone.now())
    return redirect('game:home')



