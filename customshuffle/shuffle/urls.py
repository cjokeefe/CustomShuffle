from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name="index"),
	path('callback/', views.callback, name="callback"),
	path('playlists/', views.ListPlaylists, name="playlists"),
	path('playlists/<str:pl_id>/submit/', views.ShufflePlaylist, name="submit"),
	path('playlists/<str:pl_id>/', views.PlaylistView, name="view-playlist"),
]