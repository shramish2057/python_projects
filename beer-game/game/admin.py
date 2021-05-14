from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Week)
admin.site.register(Role)
admin.site.register(Game)
admin.site.register(GameRole)
admin.site.register(UserRole)
admin.site.register(RoleWeek)
