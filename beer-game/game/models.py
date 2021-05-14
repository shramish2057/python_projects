from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Week(models.Model):
    number = models.IntegerField()
    date = models.DateTimeField()
    inventory = models.IntegerField(default= 0)
    backlog = models.IntegerField(default= 0)
    demand = models.IntegerField(default= 0)
    incoming_shipment = models.IntegerField(default= 0)
    outgoing_shipment = models.IntegerField(default= 0)
    order_placed = models.IntegerField(default= -1)
    cost = models.IntegerField(default= 0)
    def __str__(self):
        return str(self.number)


class Role(models.Model):
    role_name = models.CharField(max_length=20)
    downstream_player = models.IntegerField(default=0)
    upstream_player = models.IntegerField(default=0)
    weeks = models.ManyToManyField(
        Week, 
        through='RoleWeek',
        # through_fields=('role_id', 'week_id'),
    )
    def __str__(self):
        return self.role_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_instructor = models.BooleanField(default=False)
    roles=models.ManyToManyField(
        Role,
        through='UserRole',
        # through_fields=('user_id', 'role_id'),
    )
    def __str__(self):
        return self.user.username


class Game(models.Model):
    admin = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    nr_rounds = models.IntegerField()
    distributor_present = models.BooleanField(default=True)
    wholesaler_present = models.BooleanField(default=True)
    holding_cost = models.IntegerField()
    backlog_cost = models.IntegerField()
    is_active = models.BooleanField(default=False)
    info_sharing = models.BooleanField(default=True)
    info_delay = models.IntegerField()
    rounds_completed = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    starting_inventory = models.IntegerField()
    roles=models.ManyToManyField(
        Role,
        through='GameRole',
        # through_fields=('user_id', 'role_id'),
    )
    def __str__(self):
        return str(self.nr_rounds)


class GameRole(models.Model):
    """
    A class that stores user ids and role ids
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE, db_column='game_id')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')


class UserRole(models.Model):
    """
    A class that stores user ids and role ids
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='user_id')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')


class RoleWeek(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    week = models.ForeignKey(Week, on_delete=models.CASCADE, db_column='week_id')   
