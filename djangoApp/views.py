from django.shortcuts import render
from django.http import HttpResponse
from .models import Ticket

def say_hello(request):
    # Fetch all tickets with related comments
    tickets = Ticket.objects.prefetch_related('commented_ticket__replied_comment').all()
    return render(request, 'hello.html', {'tickets': tickets})
