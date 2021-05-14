from django.test import SimpleTestCase
from django.urls import reverse, resolve
from game.views import *

class TestUrls(SimpleTestCase):
    
    def test_home_url_is_resolved(self):
        url = reverse('game:home')
        self.assertEquals(resolve(url).func, home)

    def test_login_url_is_resolved(self):
        url = reverse('game:login')
        self.assertEquals(resolve(url).func, loginPage)
    
    def test_register_url_is_resolved(self):
        url = reverse('game:register')
        self.assertEquals(resolve(url).func, registerPage)
    
    def test_logout_url_is_resolved(self):
        url = reverse('game:logout')
        self.assertEquals(resolve(url).func, logoutUser)
    
    def test_createGame_url_is_resolved(self):
        url = reverse('game:create_game')
        self.assertEquals(resolve(url).func, createGame)

    
    def test_join_url_is_resolved(self):
        url = reverse('game:join')
        self.assertEquals(resolve(url).func, assignedGames)

    def test_demand_url_is_resolved(self):
        url = reverse('game:demand', kwargs={'game_id':1})
        self.assertEquals(resolve(url).func, createDemand)
    
    def test_enterGame_url_is_resolved(self):
        url = reverse('game:enterGame', kwargs={'role_id':1})
        self.assertEquals(resolve(url).func, enterGame)
    
    def test_deleteGame_url_is_resolved(self):
        url = reverse('game:deleteGame', kwargs={'game_id':1})
        self.assertEquals(resolve(url).func, deleteGame)
    
    def test_monitorGames_url_is_resolved(self):
        url = reverse('game:monitorGames')
        self.assertEquals(resolve(url).func, monitorGames)
    
    def test_adminPlots_url_is_resolved(self):
        url = reverse('game:adminPlots', kwargs={'game_id':1})
        self.assertEquals(resolve(url).func, adminPlots)

    def test_startGame_url_is_resolved(self):
        url = reverse('game:startGame', kwargs={'game_id':1})
        self.assertEquals(resolve(url).func, startGame)
    
    def test_gameInsights_url_is_resolved(self):
        url = reverse('game:gameInsights', kwargs={'game_id':1})
        self.assertEquals(resolve(url).func, gameInsights)
    
    def test_updateGame_url_is_resolved(self):
        url = reverse('game:updateGame', kwargs={'game_id':1})
        self.assertEquals(resolve(url).func, updateGame)
    
    def test_accountSettings_url_is_resolved(self):
        url = reverse('game:accountSettings')
        self.assertEquals(resolve(url).func, accountSettings)