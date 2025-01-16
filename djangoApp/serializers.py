from rest_framework import serializers
from .models import Author, Ticket, Comment

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the Comment model, including nested replies."""
    author = AuthorSerializer()  # Serialize the author
    replies = serializers.SerializerMethodField()  # Serialize nested replies

    class Meta:
        model = Comment
        fields = ['id', 'comment', 'date', 'author', 'replies']

    def get_replies(self, obj):
        # Get all replies for the comment
        replies = obj.replies.all() if hasattr(obj, 'replies') else []
        return CommentSerializer(replies, many=True).data


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for the Ticket model, including nested comments."""
    author = AuthorSerializer()  # Serialize the author
    direct_comments = serializers.SerializerMethodField()  # Serialize direct comments

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'author', 'date', 'direct_comments']

    def get_direct_comments(self, obj):
        # Get direct comments for the ticket
        direct_comments = obj.get_direct_comments()
        return CommentSerializer(direct_comments, many=True).data
