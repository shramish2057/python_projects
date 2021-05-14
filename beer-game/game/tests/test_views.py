from django.test import TestCase, Client
from django.urls import reverse
from game.models import *

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('player', 'player@gmail.com', 'beergame123')
        self.userprofile = UserProfile.objects.create(user=self.user, is_instructor=False)
        self.client.login(username='player', password='beergame123')
        

    def test_home(self):
        response = self.client.get(reverse('game:home'), follow=True)
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/main.html')

        
