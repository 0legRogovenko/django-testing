from datetime import timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


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
def login_redirect_to_detail(login_url, detail_url):
    """URL редиректа на логин при попытке добавления комментария анонимом."""
    return f'{login_url}?next={detail_url}'


@pytest.fixture
def many_news(db):
    """Создаёт больше новостей, чем помещается на главной странице."""
    News.objects.bulk_create(
        News(
            title=f'Новость {i}',
            text='Текст',
            date=timezone.now().date() - timedelta(days=i),
        )
        for i in range(NEWS_COUNT_ON_HOME_PAGE + 2)
    )


@pytest.fixture
def many_comments(news, author):
    """Создаёт 222 комментария с разными датами."""
    comments = []
    for i in range(222):
        comment = Comment.objects.create(
            text=f'Комментарий {i}',
            news=news, author=author
        )
        comment.created = comment.created.replace(microsecond=i)
        comments.append(comment)
    Comment.objects.bulk_update(comments, ['created'])
    return comments


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


@pytest.fixture
def login_url_with_edit(login_url, edit_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def login_url_with_delete(login_url, delete_url):
    return f'{login_url}?next={delete_url}'
