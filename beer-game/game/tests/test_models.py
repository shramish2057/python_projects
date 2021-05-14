from django.test import TestCase
from game.models import *
from django.utils import timezone
import datetime


# testing of the models and the relationships between them
# specific testing about them according to the views is found in test_views
class TestModels(TestCase):
    
    def setUp(self):
        ### ////////////
        ### create users
        ### \\\\\\\\\\\\
        self.user1 = User.objects.create(username='user1', email='user1@gmail.com', is_superuser=False, is_staff=False, password='beergame123')
        self.user2 = User.objects.create(username='user2', email='user2@gmail.com', is_superuser=False, is_staff=False, password='beergame345')
        self.user3 = User.objects.create(username='user3', email='user3@gmail.com', is_superuser=False, is_staff=False, password='beergame567')
        self.user4 = User.objects.create(username='user4', email='user4@gmail.com', is_superuser=False, is_staff=False, password='beergame678')
        self.instructor = User.objects.create(username='instructor', email='instructor@gmail.com', is_superuser=False, is_staff=False, password='beergame891')
        
        ### ///////////////////
        ### create userprofiles
        ### \\\\\\\\\\\\\\\\\\\
        self.userProfile1 = UserProfile.objects.create(user=self.user1, is_instructor=False)
        self.userProfile2 = UserProfile.objects.create(user=self.user2, is_instructor=False)
        self.userProfile3 = UserProfile.objects.create(user=self.user3, is_instructor=False)
        self.userProfile4 = UserProfile.objects.create(user=self.user4, is_instructor=False)
        self.instructorProfile = UserProfile.objects.create(user=self.instructor, is_instructor=True)
       
        ### ////////////
        ### create games
        ### \\\\\\\\\\\\

        #with wholesaler, with distributor, admin instructor
        self.game1 = Game.objects.create(admin=self.instructorProfile, nr_rounds=3, distributor_present=True, 
        wholesaler_present=True, holding_cost=1, backlog_cost=1, is_active=False, info_sharing=False, 
        info_delay=2, rounds_completed=0, is_completed=False, starting_inventory=4)
        #with wholesaler, without distributor, admin user1
        self.game2 = Game.objects.create(admin=self.userProfile1, nr_rounds=2, distributor_present=False, 
        wholesaler_present=True, holding_cost=1, backlog_cost=1, is_active=False, info_sharing=False, 
        info_delay=2, rounds_completed=0, is_completed=False, starting_inventory=3)
        #without wholesaler, with distributor, admin userProfile2
        self.game3 = Game.objects.create(admin=self.userProfile2, nr_rounds=7, distributor_present=True, 
        wholesaler_present=False, holding_cost=1, backlog_cost=1, is_active=False, info_sharing=False, 
        info_delay=2, rounds_completed=0, is_completed=False, starting_inventory=2)
        #without wholesaler, without distributor, admin userProfile3
        self.game4 = Game.objects.create(admin=self.userProfile3, nr_rounds=2, distributor_present=False, 
        wholesaler_present=False, holding_cost=1, backlog_cost=1, is_active=False, info_sharing=False, 
        info_delay=2, rounds_completed=0, is_completed=False, starting_inventory=1)

        ### ////////////
        ### create roles
        ### \\\\\\\\\\\\

        ### roles for game 1
        self.role_game1_retailer = Role.objects.create(role_name='retailer')
        self.role_game1_wholesaler = Role.objects.create(role_name='wholesaler')
        self.role_game1_distributor = Role.objects.create(role_name='distributor')
        self.role_game1_factory = Role.objects.create(role_name='factory')
        #define the relation
        self.role_game1_retailer.upstream_player = self.role_game1_wholesaler.id
        self.role_game1_wholesaler.upstream_player = self.role_game1_distributor.id
        self.role_game1_wholesaler.downstream_player = self.role_game1_retailer.id
        self.role_game1_distributor.upstream_player = self.role_game1_factory.id
        self.role_game1_distributor.downstream_player = self.role_game1_wholesaler.id
        self.role_game1_factory.downstream_player = self.role_game1_distributor.id
        self.role_game1_retailer.save()
        self.role_game1_wholesaler.save()
        self.role_game1_distributor.save()
        self.role_game1_factory.save()

        ### roles for game 2
        self.role_game2_retailer = Role.objects.create(role_name='retailer')
        self.role_game2_wholesaler = Role.objects.create(role_name='wholesaler')
        self.role_game2_factory = Role.objects.create(role_name='factory')
        #define the relation
        self.role_game2_retailer.upstream_player = self.role_game2_wholesaler.id
        self.role_game2_wholesaler.downstream_player = self.role_game2_retailer.id
        self.role_game2_wholesaler.upstream_player = self.role_game2_factory.id
        self.role_game2_factory.downstream_player = self.role_game2_wholesaler.id
        self.role_game2_retailer.save()
        self.role_game2_wholesaler.save()
        self.role_game2_factory.save()

        ### roles for game 3
        self.role_game3_retailer = Role.objects.create(role_name='retailer')
        self.role_game3_distributor = Role.objects.create(role_name='distributor')
        self.role_game3_factory = Role.objects.create(role_name='factory')
        #define the relation
        self.role_game3_retailer.upstream_player = self.role_game3_distributor.id
        self.role_game3_distributor.downstream_player = self.role_game3_retailer.id
        self.role_game3_distributor.upstream_player = self.role_game3_factory.id
        self.role_game3_factory.downstream_player = self.role_game3_distributor.id
        self.role_game3_retailer.save()
        self.role_game3_distributor.save()
        self.role_game3_factory.save()

        ### roles for game 4
        self.role_game4_retailer = Role.objects.create(role_name='retailer')
        self.role_game4_factory = Role.objects.create(role_name='factory')
        #define the relation
        self.role_game4_retailer.upstream_player = self.role_game4_factory.id
        self.role_game4_factory.downstream_player = self.role_game4_retailer.id
        self.role_game4_retailer.save()
        self.role_game4_factory.save()
        
        ### ////////////
        ### create weeks
        ### \\\\\\\\\\\\
        # creating weeks which can be used in game3
        for i in range(1, self.game3.nr_rounds+1):
            if i == 1:
                date_created = timezone.now()
                Week.objects.create(number = i, date=date_created+datetime.timedelta(weeks=i-1))
                
            else:
                Week.objects.create(number = i, date=date_created+datetime.timedelta(weeks=i-1))



    #check if users are created
    def test_num_users(self):
        user_count = len(User.objects.all())
        self.assertEqual(user_count, 5)

    #check if users are created
    def test_num_userProfiles(self):
        userProfile_count = len(UserProfile.objects.all())
        self.assertEqual(userProfile_count, 5)

    #check if games is created
    def test_num_games(self):
        game_count = len(Game.objects.all())
        self.assertEqual(game_count, 4)

    #check if games is created
    def test_num_roles(self):
        role_count = len(Role.objects.all())
        self.assertEqual(role_count, 12)

    def test_user_property(self):
        user1 = User.objects.get(username='user1')
        instructor = User.objects.get(username='instructor')

        self.assertEqual(user1.username, 'user1')
        self.assertEqual(user1.email, 'user1@gmail.com')
        self.assertEqual(user1.password, 'beergame123')
        self.assertEqual(user1.is_superuser, False)
        self.assertEqual(user1.is_staff, False)

        self.assertEqual(instructor.username, 'instructor')
        self.assertEqual(instructor.email, 'instructor@gmail.com')
        self.assertEqual(instructor.password, 'beergame891')
        self.assertEqual(instructor.is_superuser, False)
        self.assertEqual(instructor.is_staff, False)

    def test_userProfile_property(self):
        userProfile = UserProfile.objects.get(user=self.user3)
        instructorProfile = UserProfile.objects.get(user=self.instructor)

        self.assertEqual(userProfile.is_instructor, False)
        self.assertEqual(instructorProfile.is_instructor, True)

    def test_game_main_property(self):
        game1 = Game.objects.get(admin=self.instructorProfile)
        game4 = Game.objects.get(admin=self.userProfile3)
        
        self.assertEqual(game1.admin, self.instructorProfile)
        self.assertEqual(game1.nr_rounds, 3)
        self.assertEqual(game1.distributor_present, True)
        self.assertEqual(game1.wholesaler_present, True)
        self.assertEqual(game1.holding_cost, 1)
        self.assertEqual(game1.backlog_cost, 1)
        self.assertEqual(game1.is_active, False)
        self.assertEqual(game1.info_sharing, False)
        self.assertEqual(game1.info_delay, 2)
        self.assertEqual(game1.rounds_completed, 0)
        self.assertEqual(game1.is_completed, False)
        self.assertEqual(game1.starting_inventory, 4)

        self.assertEqual(game4.admin, self.userProfile3)
        self.assertEqual(game4.nr_rounds, 2)
        self.assertEqual(game4.distributor_present, False)
        self.assertEqual(game4.wholesaler_present, False)
        self.assertEqual(game4.holding_cost, 1)
        self.assertEqual(game4.backlog_cost, 1)
        self.assertEqual(game4.is_active, False)
        self.assertEqual(game4.info_sharing, False)
        self.assertEqual(game4.info_delay, 2)
        self.assertEqual(game4.rounds_completed, 0)
        self.assertEqual(game4.is_completed, False)
        self.assertEqual(game4.starting_inventory, 1)

    #test role properties and the relationship between them in different cases defined in setup
    def test_role_property(self):
        role_game_retailer1 = Role.objects.get(role_name='retailer', upstream_player=self.role_game1_wholesaler.id)
        role_game_retailer4 = Role.objects.get(role_name='retailer', upstream_player=self.role_game4_factory.id)

        role_game_wholesaler1 = Role.objects.get(downstream_player=role_game_retailer1.id)
        role_game_distributor1 = Role.objects.get(downstream_player=role_game_wholesaler1.id)
        role_game_factory1 = Role.objects.get(downstream_player=role_game_distributor1.id)
        role_game_factory4 = Role.objects.get(downstream_player=role_game_retailer4.id)

        self.assertEqual(role_game_retailer1.role_name, 'retailer')
        self.assertEqual(role_game_wholesaler1.role_name, 'wholesaler')
        self.assertEqual(role_game_distributor1.role_name, 'distributor')
        self.assertEqual(role_game_factory1.role_name, 'factory')
        self.assertEqual(role_game_retailer4.role_name, 'retailer')
        self.assertEqual(role_game_factory4.role_name, 'factory')

    def test_week_property(self):
        week1 = Week.objects.get(number=1)
        week4 = Week.objects.get(number=4)
        
        self.assertEqual(week4.date, week1.date+datetime.timedelta(weeks=3))

    def test_userRole_relationship(self):
        userProfile3 = UserProfile.objects.get(user=self.user3)
        userProfile3.roles.add(self.role_game1_retailer, self.role_game2_factory, self.role_game3_distributor, self.role_game3_retailer)
        
        role1 = Role.objects.get(userprofile=userProfile3, role_name='factory')
        # dsitributor missing, so we expect wholesaler
        role1_predecessor = Role.objects.get(pk=role1.downstream_player)

        self.assertEqual(userProfile3.roles.count(), 4)
        self.assertEqual(role1.role_name, 'factory')
        self.assertEqual(role1_predecessor.role_name, 'wholesaler')

    def test_gameRole_relationship(self):
        # this game created in setup has no wholesaler, we add the respective roles
        # the relationship between roles is predefined in the setup
        game = Game.objects.get(admin=self.userProfile1)
        game.roles.add(self.role_game3_retailer, self.role_game3_factory, self.role_game3_distributor)

        role = Role.objects.get(game=game, role_name='retailer')
        role_successor = Role.objects.get(pk = role.upstream_player)

        self.assertEqual(game.roles.count(), 3)
        self.assertEqual(role_successor.role_name, 'distributor')

    def test_roleWeek_relationship(self):
        role = self.role_game4_factory
        weeks = Week.objects.all()
        for week in weeks:
            role.weeks.add(week)
        
        self.assertEqual(role.weeks.count(), self.game3.nr_rounds)



    