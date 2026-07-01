from django.urls import path , re_path 
from . import views

urlpatterns = [
path('home/' ,  views.home_view, name='home' ),
path('chat/<int:user_id>/' , views.chat_view , name = 'chat_page'),
path('api/search-users/', views.search_users_api, name='search_users_api'),

]