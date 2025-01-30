import pytest

from pytest_factoryboy import register
from tests.create_tests.factories import AuthorFactory, TicketFactory

register(AuthorFactory)
register(TicketFactory)   

@pytest.fixture
def new_user1(db, ticket_factory):
    ticket = ticket_factory.create()
    return ticket