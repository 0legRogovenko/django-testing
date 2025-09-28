import pytest
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


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


@pytest.fixture
def many_news():
    """Фикстура создает расширенный список новостей.

    Создает на 2 новости больше, чем задано
    в настройках NEWS_COUNT_ON_HOME_PAGE.
    """
    news_list = [
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
        )
        for i in range(NEWS_COUNT_ON_HOME_PAGE + 2)
    ]
    return news_list


@pytest.fixture
def many_comments(news, author):
    """Фикстура создает много комментариев к одной новости."""
    comments = [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        for i in range(20)
    ]
    return comments


@pytest.fixture
def detail_url(news):
    """Фикстура возвращает URL страницы новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    """Фикстура возвращает URL страницы редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Фикстура возвращает URL страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    """Фикстура возвращает URL страницы авторизации."""
    return reverse('users:login')


@pytest.fixture
def form_data():
    """Фикстура возвращает данные для формы комментария."""
    return {'text': 'Текст комментария'}


@pytest.fixture
def updated_form_data():
    """Фикстура возвращает данные для обновления комментария."""
    return {'text': 'Обновлённый текст'}
