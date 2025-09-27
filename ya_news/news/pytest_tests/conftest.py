import pytest
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура создает автора комментария."""
    return django_user_model.objects.create_user(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Фикстура создает пользователя-читателя."""
    return django_user_model.objects.create_user(username='Читатель')


@pytest.fixture
def news():
    """Фикстура создает тестовую новость."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    """Фикстура создает тестовый комментарий."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def author_client(author):
    """Фикстура создает клиент с авторизацией автора комментария."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура создает клиент с авторизацией пользователя-читателя."""
    client = Client()
    client.force_login(reader)
    return client
