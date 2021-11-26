from django.urls import path, re_path
from . import views

urlpatterns = [ 
    # path('/room', views.index, name='chat-index'),
    path('search/', views.room_index, name='chat-index'),
    path('rooms/<str:room_name>/', views.room, name='chat-room'),
    # path('rooms/id/<int:room_id>/', views.fetch_rooms, name='room'),
    # path('rooms/<int:room_id>/', views.get_room, name='get-rooms'),
    # path('create/<str:room_name>/', views.create_room, name='create-room'),

]