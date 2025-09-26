from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_poll, name='create_poll'),
    path('my-polls/', views.my_polls, name='my_polls'),
    path('<int:poll_id>/', views.detail, name='detail'),
    path('<int:poll_id>/vote/', views.vote, name='vote'),
    path('<int:poll_id>/results/', views.results, name='results'),
    path('<int:poll_id>/edit/', views.edit_poll, name='edit_poll'),
    path('<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
    path('api/<int:poll_id>/results/', views.api_poll_results, name='api_poll_results'),
]