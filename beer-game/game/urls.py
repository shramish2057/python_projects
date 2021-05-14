from django.urls import path

from . import views


app_name = 'game'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('create_game/', views.createGame, name='create_game'),
    path('join/', views.assignedGames, name='join'),
    path('demand/<int:game_id>', views.createDemand, name='demand'),
    path('role/<int:role_id>', views.enterGame, name='enterGame'),
    path('delete/game/<int:game_id>', views.deleteGame, name='deleteGame'),
    path('monitor/games', views.monitorGames, name='monitorGames'),
    path('admin/plots/<int:game_id>', views.adminPlots, name ='adminPlots'),
    path('start/game/<int:game_id>', views.startGame, name='startGame'),
    path('insights/game/<int:game_id>', views.gameInsights, name='gameInsights'),
    path('update/game/<int:game_id>', views.updateGame, name='updateGame'),
    path('account_settings/', views.accountSettings, name ='accountSettings'),
]