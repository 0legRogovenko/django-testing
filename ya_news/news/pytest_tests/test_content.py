from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment, News


@pytest.mark.django_db
def test_news_count_on_homepage(client):
    """Проверка количества новостей на главной странице.

    На главной странице должно отображаться не более 10 новостей.
    """
    for i in range(11):
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
        )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


@pytest.mark.django_db
def test_news_order_on_homepage(client):
    """Проверка сортировки новостей на главной странице.

    Новости должны быть отсортированы от старых к новым.
    """
    news_old = News.objects.create(
        title='Старая новость',
        text='Текст',
    )
    news_new = News.objects.create(
        title='Свежая новость',
        text='Текст',
    )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list[0] == news_old
    assert object_list[1] == news_new


@pytest.mark.django_db
def test_comments_order_on_detail_page(client, news, author):
    """Проверка сортировки комментариев на странице новости.

    Комментарии должны быть отсортированы по возрастанию даты публикации.
    """
    comment_old = Comment.objects.create(
        news=news,
        author=author,
        text='Старый комментарий',
    )
    comment_new = Comment.objects.create(
        news=news,
        author=author,
        text='Новый комментарий',
    )
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    object_list = response.context['news'].comment_set.all()
    assert list(object_list) == [comment_old, comment_new]


@pytest.mark.django_db
def test_comment_form_visibility(client, author_client, news):
    """Проверка отображения формы комментария.

    Форма должна быть доступна только авторизованным пользователям.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
    response = author_client.get(url)
    assert 'form' in response.context
    assert response.status_code == HTTPStatus.OK
