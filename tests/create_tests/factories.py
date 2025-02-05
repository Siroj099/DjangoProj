import factory
from faker import Faker
fake = Faker()

from djangoApp.models import Author, Ticket, Comment

class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    first_name = fake.first_name()
    last_name = fake.last_name()

class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    title = 'ticket_title'
    author = factory.SubFactory(AuthorFactory)
    description = fake.text()
    
class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment
        skip_postgeneration_save = True
    
    author = factory.SubFactory(AuthorFactory)
    ticket = factory.SubFactory(TicketFactory)
    comment = fake.text()
    @factory.post_generation
    def parent(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.parent = extracted
            self.ticket = extracted.ticket
            self.save()