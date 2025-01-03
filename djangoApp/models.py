from django.db import models
from django.core.exceptions import ValidationError


class Author(models.Model):
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Ticket(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ticket_author')
    #user_nickname = models.CharField(max_length=80)
    title = models.CharField(max_length=80)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comment_author')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='commented_ticket')
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', null = True, blank=True, on_delete=models.CASCADE, related_name='replied_comment'
    )

    def __str__(self):
        if self.parent:  # Check if the comment is a reply
            return f"Reply to {self.author} on comment: {self.parent.comment[:20]}"
        else:  # Otherwise, it's a top-level comment
            return f"Comment by {self.author} on ticket: {self.ticket.title[:20]}..."
        
    class Meta:
        ordering = ['date']
        
    def clean(self):
        # Ensure parent comment belongs to the same ticket
        if self.parent and self.parent.ticket != self.ticket:
            raise ValidationError("Reply must belong to the same ticket as comment.")
    
    def save(self, *args, **kwargs): # Calls functions before saving
        self.full_clean()  # Call clean to enforce validation before saving
        super().save(*args, **kwargs)