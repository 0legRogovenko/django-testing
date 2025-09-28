import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db


def test_news_count_on_homepage(client, many_news, home_url):
    """На главной странице выводится ограниченное число новостей."""
    response = client.get(home_url)
    assert len(response.context['object_list']) == NEWS_COUNT_ON_HOME_PAGE


def test_news_order_on_homepage(client, home_url):
    """Новости на главной странице отсортированы от новых к старым."""
    response = client.get(home_url)
    expected = sorted(
        response.context['object_list'],
        key=lambda n: n.date,
        reverse=True
    )
    assert list(response.context['object_list']) == expected


def test_comments_order_on_detail_page(client, many_comments, detail_url):
    """Комментарии на странице новости отсортированы по возрастанию даты."""
    response = client.get(detail_url)
    expected = sorted(
        response.context['news'].comment_set.all(),
        key=lambda c: c.created
    )
    assert list(response.context['news'].comment_set.all()) == expected


def test_comment_form_not_visible_for_anonymous(client, detail_url):
    """Анонимный пользователь не видит форму комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_comment_form_visible_for_authorized(author_client, detail_url):
    """Авторизованный пользователь видит форму комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
