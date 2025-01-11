from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_POST
from django.core.cache import cache
from django.views.decorators.gzip import gzip_page
from django.utils import timezone
from .models import Ticket, Comment, Author

import json

def serialize_comments(comment):
    return {
        "id": comment.id,
        "comment": comment.comment,
        "date": comment.date,
        "author": comment.author,
        "replies":[
            serialize_comments(reply) for reply in getattr(comment, 'replies').all()
        ] if hasattr(comment, 'replies') else []
    }


def serialize_tickets(tickets):
    #Custom function to serialize tickets with comments
    return [{
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "author": ticket.author,
        "date": ticket.date,
        "direct_comments": [
            serialize_comments(comment) for comment in ticket.direct_comments
        ] if hasattr(ticket, 'direct_comments') else []
    } for ticket in tickets]


def get_prefetch_comments():
    """Helper function to create comment prefetch objects"""
    return [
        Prefetch(
            'comments_ticket',
            queryset=Comment.objects.filter(parent=None)
                .select_related('author')
                .order_by('date'),
            to_attr='direct_comments'
        ),
        Prefetch(
            'comments_ticket__replies',
            queryset=Comment.objects.select_related('author')
                .order_by('date'),
            to_attr='parent'
        )
    ]

@require_GET
def say_hello(request):
    page_number = int(request.GET.get('page', 1))
    cache_key = f'tickets_page_{page_number}'
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'main_page.html', cached_data)
    
    tickets = Ticket.objects.select_related('author').prefetch_related(
        *get_prefetch_comments()
    )
    
    paginator = Paginator(tickets, 10)
    try:
        page_obj = paginator.get_page(page_number)
    except Exception:
        page_obj = paginator.get_page(1)
    
    serialized_tickets = serialize_tickets(page_obj.object_list)  # Serialize tickets
    context = {
        'tickets': serialized_tickets,
        'page_range': list(paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)),
    }
    cache.set(cache_key, context, 30)
    return render(request, 'main_page.html', context)


@gzip_page
@require_GET
def search_tickets(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    
    try:
        query = request.GET.get('query', '').strip()
        page = int(request.GET.get('page', 1))
        
        cache_key = f'search_tickets_{query}_{page}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return JsonResponse(cached_result)
        
        if query:
            tickets = Ticket.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        else:
            tickets = Ticket.objects.all()
        
        tickets = tickets.select_related('author').prefetch_related(
            *get_prefetch_comments()
        )
        
        paginator = Paginator(tickets, 10)
        current_page = paginator.get_page(page)
        
        serialized_tickets = serialize_tickets(current_page.object_list)  # Serialize tickets
        
        response_data = {
            "success": True,
            "html": render_to_string(
                'ticket_list.html',
                {'tickets': serialized_tickets},
                request
            ),
            "count": tickets.count(),
            "pagination": {
                "current_page": current_page.number,
                "total_pages": paginator.num_pages,
                "has_next": current_page.has_next(),
                "has_previous": current_page.has_previous(),
            }
        }
        
        cache.set(cache_key, response_data, 300)
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    
    
@require_POST
def create_ticket(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        author_full_name = data.get('author', '').strip()
        
        if not title or not description or not author_full_name:
            return JsonResponse({
                "success": False,
                "error": "Title, author and description are required"
            }, status=400)
        
        # code to handle Foreign key in author model
        split_full_name = author_full_name.split()
        if len(split_full_name) < 2:
            return JsonResponse({
                "success": False,
                "error": "Please provide both first and last name!"
            }, status=400)
        
        first_name = split_full_name[0]
        last_name = ''.join(split_full_name[1:])
        
        author, created = Author.objects.get_or_create(
            first_name = first_name,
            last_name = last_name,
        )
        # Create new ticket
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            author=author,  
            date=timezone.now()
        )
        
        
        # Clear relevant cache
        cache.delete(f'tickets_page_1')  # Clear first page cache
        cache.delete(f'search_tickets__1')  # Clear empty search first page
        
        return JsonResponse({
            "success": True, 
            "ticket_id": ticket.id
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
