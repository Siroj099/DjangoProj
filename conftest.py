import pytest

from pytest_factoryboy import register
from tests.create_tests.factories import AuthorFactory, TicketFactory, CommentFactory

register(AuthorFactory)
register(TicketFactory)
register(CommentFactory)

@pytest.fixture
def new_ticket(db, ticket_factory):
    ticket = ticket_factory.create()
    return ticket

@pytest.fixture
def new_comment(db, comment_factory):
    comment = comment_factory.create()
    return comment

@pytest.fixture
def new_author(db, author_factory):
    author = author_factory.create()
    return author