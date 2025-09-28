from django.urls import reverse

import pytest

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count_on_homepage(client, many_news):
    """Проверка количества новостей на главной странице.

    Количество новостей равно NEWS_COUNT_ON_HOME_PAGE.
    """
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    assert len(news_list) == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_homepage(client, many_news):
    """Проверка сортировки новостей на главной странице.

    Новости должны быть отсортированы от старых к новым.
    """
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    sorted_news = sorted(many_news, key=lambda n: n.date)
    assert list(news_list) == sorted_news[:NEWS_COUNT_ON_HOME_PAGE]


@pytest.mark.django_db
def test_comments_order_on_detail_page(client, news, many_comments):
    """Проверка сортировки комментариев на странице новости.

    Комментарии должны быть отсортированы по возрастанию даты.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    comments_list = response.context['news'].comment_set.all()
    sorted_comments = sorted(many_comments, key=lambda c: c.created)
    assert list(comments_list) == sorted_comments


@pytest.mark.django_db
def test_comment_form_not_visible_for_anonymous(client, news):
    """Проверка отсутствия формы комментария для анонимного пользователя."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comment_form_visible_for_authorized(author_client, news):
    """Проверка формы комментария для авторизованного пользователя.

    Форма должна быть доступна в контексте страницы.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
