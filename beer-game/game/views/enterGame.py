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

# helper function for constructing the graph
def return_graph(last_weeks, dataType):
    if(last_weeks):
        inventories = []
        demands = []
        incoming_shipments = []
        outgoing_shipments = []
        orders = []
        weeknr = []
        if(dataType == 'inventory'):
            i = 0
            for week in last_weeks:
                inventories.append(week.inventory-week.backlog)
                i+=1
                weeknr.append(i)
            fig = plt.figure()
            plt.ylabel('Inventory')
            # plt.xlabel('Week Nr')
            plt.title('Inventory')
            plt.plot(weeknr,inventories)
        elif dataType == 'demand':
            i = 0
            for week in last_weeks:
                demands.append(week.demand)
                i+=1
                weeknr.append(i)
            fig = plt.figure()
            plt.ylabel('Demand')
            # plt.xlabel('Week Nr')
            plt.title('Demand')
            plt.plot(weeknr,demands)
        elif dataType == 'incoming_shipment':
            i = 0
            for week in last_weeks:
                incoming_shipments.append(week.incoming_shipment)
                i+=1
                weeknr.append(i)
            fig = plt.figure()
            plt.ylabel('Incoming Shipment')
            # plt.xlabel('Week Nr')
            plt.title('Incoming Shipment')
            plt.plot(weeknr,incoming_shipments)
        elif dataType == 'outgoing_shipment':
            i = 0
            for week in last_weeks:
                outgoing_shipments.append(week.outgoing_shipment)
                i+=1
                weeknr.append(i)
            fig = plt.figure()
            plt.ylabel('Outgoing Shipment')
            # plt.xlabel('Week Nr')
            plt.title('Outgoing Shipment')
            plt.plot(weeknr,outgoing_shipments)
        elif dataType == 'order':
            i = 0
            for week in last_weeks:
                orders.append(week.order_placed)
                i+=1
                weeknr.append(i)
            fig = plt.figure()
            plt.ylabel('Order')
            # plt.xlabel('Week Nr')
            plt.title('Order')
            plt.plot(weeknr,orders)
        else:
            i = 0
            for week in last_weeks:
                outgoing_shipments.append(week.outgoing_shipment)
                demands.append(week.demand)
                incoming_shipments.append(week.incoming_shipment)
                inventories.append(week.inventory-week.backlog)
                orders.append(week.order_placed)
                i+=1
                weeknr.append(i)
            fig = plt.figure()
            # plt.xlabel('Week Nr')

            plt.plot(weeknr,inventories, label='Inventory')
            plt.plot(weeknr,outgoing_shipments, label = 'Outgoing Shipment')
            plt.plot(weeknr,demands, label= 'Demand')
            plt.plot(weeknr,incoming_shipments, label = 'Incoming Shipment')
            plt.plot(weeknr,orders, label = 'Orders')
            legend = plt.legend(loc='upper center', shadow=True)



        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        data = imgdata.getvalue()
        return data
    return False


@login_required(login_url='game:login')
def enterGame(request, role_id):
    message = 'Welcome to the game'
    completed = False
    role = Role.objects.get(pk=role_id)
    upstream_role = '' 
    downstream_role = ''
    game= Game.objects.get(roles__id=role_id)
    current_week_up = False
    current_week_down = False

    if game.is_active:
        last_weeks = Week.objects.filter(date__lte=timezone.now(), role__id=role_id).order_by('-date')[:11]
        current_week_role = last_weeks[0]
        last_weeks = Week.objects.filter(number__lt=current_week_role.number, role__id = role_id).order_by('date')[:10]

        game.rounds_completed = current_week_role.number
        if(current_week_role.number == game.nr_rounds and current_week_role.order_placed != -1):
            message = 'Game completed'
            completed = True

        #find whether other player have ordered in this current round
        other_weeks = Week.objects.filter(role__game=game, number=current_week_role.number).exclude(role__id = role_id).order_by('id')


        total_requirements = current_week_role.demand + current_week_role.backlog
        total_available = current_week_role.inventory + current_week_role.incoming_shipment

        #check whether the role is factory
        if(role.upstream_player != 0):
            upstream_role = Role.objects.get(pk=role.upstream_player)
            current_week_up = Week.objects.filter(number=current_week_role.number, role__id=upstream_role.id)
        else:
            upstream_role = 'brewery'

        #check whether the role is retailer
        if(role.downstream_player != 0):
            downstream_role = Role.objects.get(pk=role.downstream_player)
            current_week_down = Week.objects.filter(number=current_week_role.number, role__id=downstream_role.id)
        else:
            downstream_role='consumer'
        
        context = {'message': message, 'completed': completed, 'role': role, 'upstream_role':upstream_role, 
        'downstream_role': downstream_role,'last_weeks':last_weeks, 'current_week_role': current_week_role,
        'other_weeks': other_weeks,'game': game, 'total_requirements': total_requirements, 'total_available': total_available, 
        'graph1': return_graph(last_weeks, 'inventory')
        , 'graph2': return_graph(last_weeks, 'demand'), 'graph3': return_graph(last_weeks, 'incoming_shipment'), 
        'graph4': return_graph(last_weeks, 'outgoing_shipment'), 'graph5': return_graph(last_weeks, 'order'), 
        'graph6': return_graph(last_weeks, 'all')
        # 'graph_div': graph_div
        }
    else:
        context = {'game':game }


    if request.method == "POST":
        # determine if the game has completed
        if current_week_role.number == game.nr_rounds:
                    
            if timezone.now() > current_week_role.date+datetime.timedelta(minutes=3):
                game.is_completed = True
            else: 
                completed = True
                for i in other_weeks:
                    if i.order_placed == -1:
                        completed = False
                if completed == True:
                    game.is_completed = True
        #some data taken from the game
        holding_cost = game.holding_cost
        backlog_cost = game.backlog_cost
        info_delay = game.info_delay
        order_placed = request.POST['order_placed']


        #calculating all the neccessary attributes for this current week
        total_requirements = current_week_role.demand + current_week_role.backlog
        total_available = current_week_role.inventory + current_week_role.incoming_shipment

        new_inventory = total_available - total_requirements
        new_backlog = 0
        if new_inventory < 0:
            new_backlog = abs(new_inventory)
            new_inventory = 0
            outgoing_shipment = total_available
        else:
            outgoing_shipment = total_requirements
        
        current_cost = current_week_role.cost + new_inventory * holding_cost + new_backlog*backlog_cost
        
        #saving all missing attributes to the corresponding week
        current_week_role.order_placed = order_placed
        current_week_role.inventory = new_inventory
        current_week_role.backlog = new_backlog
        current_week_role.outgoing_shipment = outgoing_shipment
        current_week_role.cost = current_cost
        current_week_role.save()


        #updating the attributes of the next week of the corresponding role according to the info obtained
        if(current_week_role.number+1 < game.nr_rounds):
            next_week = Week.objects.get(role__id=role_id, number=current_week_role.number+1)
            if(next_week):
                next_week.inventory = new_inventory
                next_week.backlog = new_backlog
                next_week.cost = current_cost
                next_week.save()
        
        
        #updating the attributes of the (future) weeks of other roles according to the 
        #corresponding relationship (upstream, downstream) and the info_delay
        
        if(current_week_role.number+info_delay < game.nr_rounds):   
            #1 and the order placed by the user, which will become the demand to the upstream player after info_delay  
            if(current_week_up):
                #not a factory
                #find the week of the upstream player, when the demand will arrive
                future_week_up = Week.objects.get(role= upstream_role, number=current_week_role.number+info_delay)
                if(future_week_up):
                    future_week_up.demand = order_placed
                    future_week_up.save()
            else:
                #factory, we will just update the week entity corresponding to the time after 2 weeks (1 + 1)
                #it does not rely on the info_delay
                future_week_role = Week.objects.get(role__id = role_id, number = current_week_role.number + 2)
                if(future_week_role):
                    future_week_role.incoming_shipment = order_placed
                    future_week_role.save()

            #2 and the outgoing shipment of the user, which will become the incoming shipment of the downstream player
            if(current_week_down):
                #not a retailer
                future_week_down = Week.objects.get(role=downstream_role, number = current_week_role.number+info_delay)
                if(future_week_down):
                    future_week_down.incoming_shipment = outgoing_shipment
                    future_week_down.save()

        game.save()
        return HttpResponseRedirect(reverse('game:enterGame', args=(role_id,)))

    
    
    return render(request, 'game/enterGame.html', context)




