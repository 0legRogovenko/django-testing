from datetime import timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


FORM_DATA = {'text': 'Текст формы'}


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create_user(username='Читатель')


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def many_news(db):
    """Создаёт больше новостей, чем помещается на главной странице."""
    today = timezone.now().date()
    News.objects.bulk_create([
        News(
            title=f'Новость {i}',
            text='Текст',
            date=today - timedelta(days=i),
        )
        for i in range(NEWS_COUNT_ON_HOME_PAGE + 2)
    ])
    return News.objects.all()


@pytest.fixture
def many_comments(news, author):
    """Создаёт 222 комментария с разными датами."""
    now = timezone.now()
    Comment.objects.bulk_create([
        Comment(
            news=news,
            author=author,
            text=f'Комментарий {i}',
            created=now - timedelta(minutes=i),
        )
        for i in range(222)
    ])
    return Comment.objects.filter(news=news)


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def home_url():
    return reverse('news:home')
