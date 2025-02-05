import pytest
from djangoApp.models import Ticket, Comment, Author  


def test_ticket_create(db, ticket_factory):
    ticket = ticket_factory.create()
    print(ticket.description)
    
    db_ticket = Ticket.objects.get(id = ticket.id)
    
    assert db_ticket.description == ticket.description
    assert db_ticket.title == 'ticket_title'
    
def test_comment_create(db, comment_factory):
    comment = comment_factory.create()
    child_comment = comment_factory.create(parent = comment)
    print(comment.comment)
    
    db_comment = Comment.objects.get(id = comment.id)
    db_child = Comment.objects.get(id = child_comment.id)
    
    assert child_comment.parent == comment
    assert child_comment.ticket == comment.ticket
    assert db_child.ticket == db_comment.ticket
    assert db_child.parent_id == db_comment.id
    
def test_author_create(db, author_factory):
    author = author_factory.create()
    print(author.first_name)
    print(author.last_name)
    
    db_author = Author.objects.get(id = author.id)
    
    assert db_author.first_name == author.first_name
    assert db_author.last_name == author.last_name