from django.contrib import admin
from .models import Author, Ticket, Comment


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'date', 'description', 'comment_count']   # Display columns
    list_per_page = 20   # Set number of displayed tickets per page
    
    def comment_count(self, ticket):
        return ticket.commented_ticket.count()  # Count number of comment under the ticket using reverse relation
    
    comment_count.short_description = "Comment count" # Change column name
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'ticket_name', 'date', 'parent', 'comment']

    def ticket_name(self, Ticket):
        return Ticket.ticket.title
    ticket_name.short_description = "Ticket"

admin.site.register(Author)

