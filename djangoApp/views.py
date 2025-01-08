from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import Ticket, Comment



def say_hello(request):
    # Get all tickets ( Tickets join author )
    tickets = Ticket.objects.select_related('author').all()
    
    # Get page number from request
    page_number = request.GET.get('page', 1)
    
    # Create paginator object
    paginator = Paginator(tickets, 15)  # 15 tickets per page
    
    try:
        # Get the requested page
        page_obj = paginator.get_page(page_number)
    except Exception as e:
        # Handle errors
        page_obj = paginator.get_page(1)
    
    return render(request, 'main_page.html', {
        'tickets': page_obj,
        'page_range': paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
    })
                                              


def search_tickets(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            # method try used to handle exceptions in future
            # research parameters
            query = request.GET.get('query', '')
            page = int(request.GET.get('page', 1))
            
            # filtering Ticket data
            tickets = Ticket.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).select_related('author')
            
            # pagination
            paginator = Paginator(tickets, 15)
            current_page = paginator.get_page(page)
        
            
            html_from_java = render_to_string('ticket_list.html',{
                'tickets': current_page.object_list
            },request)
            
            return JsonResponse({
                "success": True,
                "html": html_from_java,
                "tickets": list(tickets.values('id', 'title', 'description', 'date', 'author')),
                "count": tickets.count(),
                "pagination": {
                
                    "current_page": page,
                    "total_pages": paginator.num_pages,
                    "has_next": current_page.has_next(),
                    "has_previous": current_page.has_previous()
                
                }
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=400)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
