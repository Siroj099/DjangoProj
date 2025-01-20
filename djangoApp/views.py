from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_POST
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# from rest_framework.decorators import api_view
from dateutil import parser
from .models import Ticket, Comment, Author
from .serializers import TicketSerializer
import json


@require_GET
def say_hello(request):
    page_number = 1
    cache_key = f'tickets_page_{page_number}'
    
    cached_data = cache.get(cache_key)
    if cached_data:
        for ticket in cached_data['tickets']:
            if isinstance(ticket['date'], str):
                ticket['date'] = parser.parse(ticket['date'])             
            elif isinstance(ticket['date'], datetime):
                ticket['date'] = ticket['date'].strftime('%Y-%m-%d %H:%M:%S')
        return render(request, 'main_page.html', cached_data)
    
    tickets = Ticket.objects.select_related('author').prefetch_related(
        *get_prefetch_comments()
    )
    
    paginator = Paginator(tickets, 10)
    try:
        page_obj = paginator.get_page(page_number)
    except Exception:
        page_obj = paginator.get_page(1)
    
    serialized_tickets = TicketSerializer(page_obj.object_list, many = True)  # Serialize tickets
    context = {
        'tickets': serialized_tickets.data,
        'page_range': list(paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)),
    }
    cache.set(cache_key, context, 30)
    return render(request, 'main_page.html', context)



@require_GET
def search_tickets(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    
    try:
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))
        
        cache_key = f'search_tickets_{query}_{page}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return JsonResponse(cached_result)
        
        tickets = Ticket.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
        
        tickets = tickets.select_related('author').prefetch_related(
            *get_prefetch_comments()
        )
        
        paginator = Paginator(tickets, 10)
        current_page = paginator.get_page(page)
        
        serialized_tickets = TicketSerializer(current_page.object_list, many = True)
        
        response_data = {
            "success": True,
            "html": render_to_string(
                'ticket_list.html',
                {'tickets': serialized_tickets.data},
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
        
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            author=author,  
            date=timezone.now()
        )
        
        
        # Clear relevant cache
        cache.delete(f'tickets_page_1')  
        cache.delete(f'search_tickets__1')  
        
        return JsonResponse({
            "success": True, 
            "ticket_id": ticket.id
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)

@require_POST
def create_comment(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    
    try:
        data = json.loads(request.body)
        comment = data.get('comment')
        author_full_name = data.get('author', '').strip()
        ticket_id = data.get('ticketId')    
            
        if not author_full_name or not comment or not ticket_id:
            return JsonResponse({
                "success": False,
                "error": "Author or description are required"
            }, status=400)
                        
        try:
            ticket = Ticket.objects.select_related('author').prefetch_related(
                Prefetch(
                    'comments_ticket',
                    queryset=Comment.objects.filter(parent=None)
                                          .order_by('-date')
                                          .select_related('author'),
                    to_attr='direct_comments'
                )
            ).get(id=ticket_id)
        except Ticket.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Invalid ticket ID"
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
        
        comment = Comment.objects.create(
            comment=comment,
            ticket = ticket,
            author=author,  
            date=timezone.now(),
        )
        
        
        # Clear relevant cache
        cache.delete(f'tickets_page_1')  
        cache.delete(f'search_tickets__1') 
        
        # Render single ticket template
        updated_ticket_html = render_to_string('single_ticket.html', {
            #'ticket': ticket,
             'direct_comments': ticket.direct_comments,
        }, request=request ) 
        
        return JsonResponse({
            "success": True, 
            "ticketSection": updated_ticket_html,
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
 
@require_POST
def create_reply(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        reply_text = data.get('reply')  
        author_full_name = data.get('author', '').strip()
        ticket_id = data.get('ticketId')  
        comment_id = data.get('commentId') 

        if not author_full_name or not reply_text or not comment_id:
            return JsonResponse({
                "success": False,
                "error": "Author, reply text, and comment ID are required."
            }, status=400)

        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Comment.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Invalid comment ID."
            }, status=400)

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Invalid comment ID."
            }, status=400)

        split_full_name = author_full_name.split()
        if len(split_full_name) < 2:
            return JsonResponse({
                "success": False,
                "error": "Please provide both first and last name!"
            }, status=400)

        first_name = split_full_name[0]
        last_name = ''.join(split_full_name[1:])
        author, created = Author.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
        )

        reply = Comment.objects.create(
            comment=reply_text,
            ticket=ticket, 
            author=author,
            date=timezone.now(),
            parent=comment,  
        )

        # Clear cache
        cache.delete(f'tickets_page_1')
        cache.delete(f'search_tickets__1')

        return JsonResponse({"success": True, "reply_id": reply.id})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    
def get_prefetch_comments():
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