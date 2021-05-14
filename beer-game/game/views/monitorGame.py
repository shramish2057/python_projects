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


@login_required(login_url='game:login')
def monitorGames(request):
    game_created = Game.objects.filter(admin=request.user.userprofile, is_active = True)
    games_info = []


# games_info[[game1, factory_cost1, dist_cost1, wh_cost1, ret_cost1, total_cost ]
#             [game2, factory_cost2, dist_cost2, wh_cost2, ret_cost2, total_cost ]....  ]
    for game in game_created:
        game_info = []
        game_info.append(game)
        
        if(game.rounds_completed == 0):
            nr = 1
        else: nr = game.rounds_completed

        total_cost = 0
        #get the last week of each role
        week4 = Week.objects.get(role__game__id = game.id, role__role_name= 'factory', number=nr)
        game_info.append(week4.cost)
        total_cost += week4.cost
        
        if(game.distributor_present):
            week3 = Week.objects.get(role__game__id = game.id, role__role_name= 'distributor', number=nr)
            game_info.append(week3.cost)
            total_cost += week3.cost
        if(game.wholesaler_present):
            week2 = Week.objects.get(role__game__id = game.id, role__role_name= 'wholesaler', number=nr)
            game_info.append(week2.cost)
            total_cost += week2.cost
        
        week1 = Week.objects.get(role__game__id = game.id, role__role_name= 'retailer', number=nr)
        game_info.append(week1.cost)
        total_cost += week1.cost
        print(total_cost,end=' ')
        print(week1.cost,end=' ')
        print(week2.cost,end=' ')
        print(week3.cost,end=' ')
        print(week4.cost)
        game_info.append(total_cost)
        games_info.append(game_info)

    for game_info in games_info:
        print(game_info)
    context={'games_info': games_info, 'user': request.user.userprofile}
    return render(request, 'game/monitorGames.html', context)


# helper function for constructing the graph for a single role of the game
def graph_single(last_weeks):
    if(last_weeks):
        inventories = []
        demands = []
        incoming_shipments = []
        outgoing_shipments = []
        orders = []
        weeknr = []
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
        plt.ioff()
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


def graph_all(last_weeks_all, data_type):
    if(last_weeks_all):
        last_weeks_retailer = last_weeks_all[0]
        last_weeks_wholesaler = last_weeks_all[1]
        last_weeks_distributor = last_weeks_all[2]
        last_weeks_factory = last_weeks_all[3]
        if(data_type == 'inventory'):
            i = 0
            weeknr = []
            inventories_retailer = []
            inventories_wholesaler = []
            inventories_distributor = []
            inventories_factory = []
            for week in last_weeks_retailer:
                inventories_retailer.append(week.inventory-week.backlog)
                i+=1
                weeknr.append(i)
            for week in last_weeks_wholesaler:
                inventories_wholesaler.append(week.inventory-week.backlog)
            for week in last_weeks_distributor:
                inventories_distributor.append(week.inventory-week.backlog)
            for week in last_weeks_factory:
                inventories_factory.append(week.inventory-week.backlog)
            
            fig = plt.figure()
            plt.plot(weeknr,inventories_retailer, label='Retailer')
            if(inventories_wholesaler):
                plt.plot(weeknr,inventories_wholesaler, label = 'Wholesaler')
            if(inventories_distributor):
                plt.plot(weeknr,inventories_distributor, label = 'Distributor')
            plt.plot(weeknr,inventories_factory, label='Factory')
            legend = plt.legend(loc='upper center', shadow=True)
            plt.title('Inventory')
        elif data_type == 'demand':
            i = 0
            weeknr = []
            demands_retailer = []
            demands_wholesaler = []
            demands_distributor = []
            demands_factory = []
            for week in last_weeks_retailer:
                demands_retailer.append(week.demand)
                i+=1
                weeknr.append(i)
            for week in last_weeks_wholesaler:
                demands_wholesaler.append(week.demand)
            for week in last_weeks_distributor:
                demands_distributor.append(week.demand)
            for week in last_weeks_factory:
                demands_factory.append(week.demand)
            
            fig = plt.figure()
            plt.plot(weeknr,demands_retailer, label='Retailer')
            if(demands_wholesaler):
                plt.plot(weeknr,demands_wholesaler, label = 'Wholesaler')
            if(demands_distributor):
                plt.plot(weeknr,demands_distributor, label = 'Distributor')
            plt.plot(weeknr,demands_factory, label='Factory')
            legend = plt.legend(loc='upper center', shadow=True)
            plt.title('Demand')
        elif data_type == 'incoming_shipment':
            i = 0
            weeknr = []
            incoming_shipments_retailer = []
            incoming_shipments_wholesaler = []
            incoming_shipments_distributor = []
            incoming_shipments_factory = []
            for week in last_weeks_retailer:
                incoming_shipments_retailer.append(week.incoming_shipment)
                i+=1
                weeknr.append(i)
            for week in last_weeks_wholesaler:
                incoming_shipments_wholesaler.append(week.incoming_shipment)
            for week in last_weeks_distributor:
                incoming_shipments_distributor.append(week.incoming_shipment)
            for week in last_weeks_factory:
                incoming_shipments_factory.append(week.incoming_shipment)
            
            fig = plt.figure()
            plt.plot(weeknr,incoming_shipments_retailer, label='Retailer')
            if(incoming_shipments_wholesaler):
                plt.plot(weeknr,incoming_shipments_wholesaler, label = 'Wholesaler')
            if(incoming_shipments_distributor):
                plt.plot(weeknr,incoming_shipments_distributor, label = 'Distributor')
            plt.plot(weeknr,incoming_shipments_factory, label='Factory')
            legend = plt.legend(loc='upper center', shadow=True)
            plt.title('Incoming Shipment')
        elif data_type == 'outgoing_shipment':
            i = 0
            weeknr = []
            outgoing_shipments_retailer = []
            outgoing_shipments_wholesaler = []
            outgoing_shipments_distributor = []
            outgoing_shipments_factory = []
            for week in last_weeks_retailer:
                outgoing_shipments_retailer.append(week.outgoing_shipment)
                i+=1
                weeknr.append(i)
            for week in last_weeks_wholesaler:
                outgoing_shipments_wholesaler.append(week.outgoing_shipment)
            for week in last_weeks_distributor:
                outgoing_shipments_distributor.append(week.outgoing_shipment)
            for week in last_weeks_factory:
                outgoing_shipments_factory.append(week.outgoing_shipment)
            
            fig = plt.figure()
            plt.plot(weeknr,outgoing_shipments_retailer, label='Retailer')
            if(outgoing_shipments_wholesaler):
                plt.plot(weeknr,outgoing_shipments_wholesaler, label = 'Wholesaler')
            if(outgoing_shipments_distributor):
                plt.plot(weeknr,outgoing_shipments_distributor, label = 'Distributor')
            plt.plot(weeknr,outgoing_shipments_factory, label='Factory')
            legend = plt.legend(loc='upper center', shadow=True)
            plt.title('Outgoing Shipment')
        elif data_type == 'order':
            i = 0
            weeknr = []
            orders_retailer = []
            orders_wholesaler = []
            orders_distributor = []
            orders_factory = []
            for week in last_weeks_retailer:
                orders_retailer.append(week.order_placed)
                i+=1
                weeknr.append(i)
            for week in last_weeks_wholesaler:
                orders_wholesaler.append(week.order_placed)
            for week in last_weeks_distributor:
                orders_distributor.append(week.order_placed)
            for week in last_weeks_factory:
                orders_factory.append(week.order_placed)
            
            fig = plt.figure()
            plt.plot(weeknr,orders_retailer, label='Retailer')
            if(orders_wholesaler):
                plt.plot(weeknr,orders_wholesaler, label = 'Wholesaler')
            if(orders_distributor):
                plt.plot(weeknr,orders_distributor, label = 'Distributor')
            plt.plot(weeknr,orders_factory, label='Factory')
            legend = plt.legend(loc='upper center', shadow=True)
            plt.title('Order')
        else:
            return False



        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)

        data = imgdata.getvalue()
        return data
    return False


@login_required(login_url='game:login')
def adminPlots(request, game_id):
    game = Game.objects.get(pk=game_id)


    
    last_weeks_wholesaler = []
    last_weeks_distributor = []
    last_weeks_retailer = Week.objects.filter(role__game__id=game_id, role__role_name='retailer', number__lt=game.rounds_completed).order_by('date')
    if (game.wholesaler_present):
        last_weeks_wholesaler = Week.objects.filter(role__game__id=game_id, role__role_name='distributor', number__lt=game.rounds_completed).order_by('date')
    if (game.distributor_present):
        last_weeks_distributor = Week.objects.filter(role__game__id=game_id, role__role_name='distributor', number__lt=game.rounds_completed).order_by('date')
    
    last_weeks_factory = Week.objects.filter(role__game__id=game_id, role__role_name='factory', number__lt=game.rounds_completed).order_by('date')

    last_weeks_all = []
    last_weeks_all.append(last_weeks_retailer)
    last_weeks_all.append(last_weeks_wholesaler)
    last_weeks_all.append(last_weeks_distributor)
    last_weeks_all.append(last_weeks_factory)

    context = {
    'game_id':game_id, 'graph_retailer': graph_single(last_weeks_retailer)
    , 'graph_wholesaler': graph_single(last_weeks_wholesaler), 'graph_distributor': graph_single(last_weeks_distributor), 
    'graph_factory': graph_single(last_weeks_factory), 'graph_all_inventory': graph_all(last_weeks_all, 'inventory'),
    'graph_all_demand': graph_all(last_weeks_all, 'demand'), 'graph_all_incoming_shipment': graph_all(last_weeks_all, 'incoming_shipment'),
    'graph_all_outgoing_shipment': graph_all(last_weeks_all, 'outgoing_shipment'), 'graph_all_order': graph_all(last_weeks_all, 'order'),
    }
    return render(request, 'game/adminPlots.html', context)



@login_required(login_url='game:login')
def gameInsights(request, game_id):
    game = Game.objects.get(pk=game_id)
    game_info = []
    game_info.append(game)
    
    if(game.rounds_completed == 0):
        nr = 1
    else: nr = game.rounds_completed

    total_cost = 0
    #get the last week of each role
    week4 = Week.objects.get(role__game__id = game.id, role__role_name= 'factory', number=nr)
    game_info.append(week4.cost)
    total_cost += week4.cost
    
    if(game.distributor_present):
        week3 = Week.objects.get(role__game__id = game.id, role__role_name= 'distributor', number=nr)
        game_info.append(week3.cost)
        total_cost+=week3.cost
    if(game.wholesaler_present):
        week2 = Week.objects.get(role__game__id = game.id, role__role_name= 'wholesaler', number=nr)
        game_info.append(week2.cost)
        total_cost += week2.cost
    
    week1 = Week.objects.get(role__game__id = game.id, role__role_name= 'retailer', number=nr)
    game_info.append(week1.cost)
    total_cost += week1.cost
    game_info.append(total_cost)

    context={'game_info': game_info, 'user': request.user.userprofile}
    return render(request, 'game/gameInsights.html', context)