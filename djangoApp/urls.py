
from django.urls import path
from . import views

from django.conf.urls.static import static


urlpatterns=[

path('hello/', views.say_hello),
path('hello/search/', views.search_tickets, name='search-tickets'),
path('hello/create_ticket/', views.create_ticket, name='create_ticket'),
]
