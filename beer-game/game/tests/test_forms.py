from django.test import TestCase
from game.forms import *


class TestForms(TestCase):

    def test_extendedUserCreationForm_valid_data(self):
        form = ExtendedUserCreationForm(data={
            'username':'player', 
            'email':'player@gmail.com', 
            'first_name': 'player', 
            'last_name':'player', 
            'password1':'beergame123', 
            'password2': 'beergame123'
        })
        self.assertTrue(form.is_valid())

    def test_extendedUserCreationForm_no_data(self):
        form = ExtendedUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 6)

    def test_extendedUserCreationForm_password_not_matching(self):
        form = ExtendedUserCreationForm(data={
            'username':'player', 
            'email':'player@gmail.com', 
            'first_name': 'player', 
            'last_name':'player', 
            'password1':'beergame123', 
            'password2': 'beergame1'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
    
    def test_userProfileForm_valid_data(self):
        form = UserProfileForm(data={
            'is_instructor':True
        })
        self.assertTrue(form.is_valid())

    def test_userProfileForm_no_data(self):
        form = UserProfileForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEquals(len(form.errors), 0)

    def test_gameCreationForm_valid_data(self):
        form = GameCreationForm(data={
            'nr_rounds':2, 
            'info_delay':2, 
            'holding_cost': 4, 
            'backlog_cost':5, 
            'starting_inventory':12, 
            'distributor_present': True, 
            'wholesaler_present':True
        })
        self.assertTrue(form.is_valid())

    def test_gameCreationForm_no_data(self):
        form = GameCreationForm(data={})
        self.assertFalse(form.is_valid())
        # distributor, wholesaler can be left unchecked
        self.assertEquals(len(form.errors), 5)
    
    def test_extendedGameCreationForm_valid_data(self):
        user1 = User.objects.create(username='user1', email='user1@gmail.com', password='beergame123')
        user2 = User.objects.create(username='user2', email='user2@gmail.com', password='beergame345')
        user3 = User.objects.create(username='user3', email='user3@gmail.com', password='beergame567')
        user4 = User.objects.create(username='user4', email='user4@gmail.com', password='beergame678')

        userProfile1 = UserProfile.objects.create(user=user1, is_instructor=False)
        userProfile2 = UserProfile.objects.create(user=user2, is_instructor=False)
        userProfile3 = UserProfile.objects.create(user=user3, is_instructor=False)
        userProfile4 = UserProfile.objects.create(user=user4, is_instructor=False)
        form = ExtendedGameCreationForm(data={
            'retailer':user1, 
            'wholesaler':user2, 
            'distributor': user3, 
            'factory':user4
        })
        self.assertTrue(form.is_valid())

    def test_extendedGameCreationForm_no_data(self):
        form = ExtendedGameCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_extendedGameCreationForm_wrong_data(self):
        # add instructor instead of student
        user1 = User.objects.create(username='user1', email='user1@gmail.com', password='beergame123')
        user2 = User.objects.create(username='user2', email='user2@gmail.com', password='beergame345')
        user3 = User.objects.create(username='user3', email='user3@gmail.com', password='beergame567')
        user4 = User.objects.create(username='user4', email='user4@gmail.com', password='beergame678')
        instructor = User.objects.create(username='instructor', email='instructor@gmail.com', is_superuser=False, is_staff=False, password='beergame891')

        userProfile1 = UserProfile.objects.create(user=user1, is_instructor=False)
        userProfile2 = UserProfile.objects.create(user=user2, is_instructor=False)
        userProfile3 = UserProfile.objects.create(user=user3, is_instructor=False)
        userProfile4 = UserProfile.objects.create(user=user4, is_instructor=False)
        instructorProfile = UserProfile.objects.create(user=instructor, is_instructor=True)
        form = ExtendedGameCreationForm(data={
            'retailer':user1, 
            'wholesaler':user2, 
            'distributor': user3, 
            'factory':instructor
        })
        # false, because instructor added
        self.assertFalse(form.is_valid())
    
    def test_gameUpdateForm_valid_data(self):
        form = GameUpdateForm(data={
            'nr_rounds':2, 
            'info_delay':2, 
            'holding_cost': 4, 
            'backlog_cost':5, 
            'is_active':True, 
            'distributor_present': True, 
            'wholesaler_present':True
        })
        self.assertTrue(form.is_valid())

    def test_gameUpdateForm_no_data(self):
        form = GameUpdateForm(data={})
        self.assertFalse(form.is_valid())
        # distributor, wholesaler, active can be left unchecked
        self.assertEquals(len(form.errors), 4)
    
    def test_extendedGameUpdateForm_valid_data(self):
        user1 = User.objects.create(username='user1', email='user1@gmail.com', password='beergame123')
        user2 = User.objects.create(username='user2', email='user2@gmail.com', password='beergame345')
        user3 = User.objects.create(username='user3', email='user3@gmail.com', password='beergame567')
        user4 = User.objects.create(username='user4', email='user4@gmail.com', password='beergame678')

        userProfile1 = UserProfile.objects.create(user=user1, is_instructor=False)
        userProfile2 = UserProfile.objects.create(user=user2, is_instructor=False)
        userProfile3 = UserProfile.objects.create(user=user3, is_instructor=False)
        userProfile4 = UserProfile.objects.create(user=user4, is_instructor=False)
        form = ExtendedGameUpdateForm(data={
            'retailer':user1, 
            'wholesaler':user2, 
            'distributor': user3, 
            'factory':user4
        })
        self.assertTrue(form.is_valid())

    def test_extendedGameUpdateForm_no_data(self):
        form = ExtendedGameUpdateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_extendedGameUpdateForm_wrong_data(self):
        # add instructor instead of student
        user1 = User.objects.create(username='user1', email='user1@gmail.com', password='beergame123')
        user2 = User.objects.create(username='user2', email='user2@gmail.com', password='beergame345')
        user3 = User.objects.create(username='user3', email='user3@gmail.com', password='beergame567')
        user4 = User.objects.create(username='user4', email='user4@gmail.com', password='beergame678')
        instructor = User.objects.create(username='instructor', email='instructor@gmail.com', is_superuser=False, is_staff=False, password='beergame891')

        userProfile1 = UserProfile.objects.create(user=user1, is_instructor=False)
        userProfile2 = UserProfile.objects.create(user=user2, is_instructor=False)
        userProfile3 = UserProfile.objects.create(user=user3, is_instructor=False)
        userProfile4 = UserProfile.objects.create(user=user4, is_instructor=False)
        instructorProfile = UserProfile.objects.create(user=instructor, is_instructor=True)
        form = ExtendedGameUpdateForm(data={
            'retailer':user1, 
            'wholesaler':user2, 
            'distributor': user3, 
            'factory':instructor
        })
        # false, because instructor added
        self.assertFalse(form.is_valid())