from http import HTTPStatus

import pytest

from news.forms import CommentForm
from news.models import News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count_on_homepage(client, many_news, home_url):
    """На главной странице выводится ограниченное число новостей."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['object_list']) == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_homepage(client, many_news, home_url):
    """Новости на главной странице отсортированы от новых к старым."""
    response = client.get(home_url)
    expected = list(News.objects.order_by('-date')[:NEWS_COUNT_ON_HOME_PAGE])
    assert list(response.context['object_list']) == expected


@pytest.mark.django_db
def test_comments_order_on_detail_page(client, many_comments, detail_url):
    """Комментарии на странице новости отсортированы по возрастанию даты."""
    response = client.get(detail_url)
    comments = response.context['news'].comment_set.all()
    assert list(comments) == sorted(many_comments, key=lambda c: c.created)


@pytest.mark.django_db
def test_comment_form_not_visible_for_anonymous(client, detail_url):
    """Анонимный пользователь не видит форму комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_visible_for_authorized(author_client, detail_url):
    """Авторизованный пользователь видит форму комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
