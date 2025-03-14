
from django.urls import path
from . import views
from .views import say_hello

from django.conf.urls.static import static


urlpatterns=[

path('hello/', say_hello, name='say_hello'),
path('hello/search/', views.search_tickets, name='search_tickets'),
path('hello/create_ticket/', views.create_ticket, name='create_ticket'),
path('hello/create_comment/', views.create_comment, name='create_comment'),
path('hello/create_reply/', views.create_reply, name='create_reply'),
]
