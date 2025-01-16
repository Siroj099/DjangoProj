from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Author(models.Model):
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['last_name', 'first_name']

class Ticket(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ticket_author')
    title = models.CharField(max_length=80, db_index=True)
    date = models.DateTimeField(default=timezone.now, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    def get_direct_comments(self):
        return self.comments_ticket.filter(parent = None)
    
    def get_comment_count(self):
        return self.comments_ticket.count()
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['description'])
        ]

class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comments_author')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments_ticket')
    comment = models.TextField()
    date = models.DateTimeField(default=timezone.now, db_index=True)
    parent = models.ForeignKey(
        'self', null = True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )

    def __str__(self):
        if self.parent:  # Check if the comment is a reply
            return f"Reply to {self.parent.author} on comment: {self.parent.comment[:20]}"
        else:  # Otherwise, it's a top-level comment
            return f"Comment by {self.author} on ticket: {self.ticket.title[:20]}..."
        
    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
        ]   
        
    def clean(self):
        # Ensure parent comment belongs to the same ticket
        if self.parent and self.parent.ticket != self.ticket:
            raise ValidationError("Reply must belong to the same ticket as comment.")
    
    def save(self, *args, **kwargs): # Calls functions before saving
        self.full_clean()  # Call clean to enforce validation before saving
        super().save(*args, **kwargs)