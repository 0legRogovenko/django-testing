from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_available_for_anonymous(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_available_for_anonymous(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_delete_available_for_author(author_client, comment):
    """Страницы редактирования и удаления комментария доступны автору."""
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    assert author_client.get(edit_url).status_code == HTTPStatus.OK
    assert author_client.get(delete_url).status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonymous_redirected_from_edit_delete(client, comment):
    """Проверка редиректа анонимного пользователя.

    При попытке редактировать или удалить комментарий происходит
    перенаправление на страницу логина.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    login_url = reverse('users:login')

    response = client.get(edit_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={edit_url}'

    response = client.get(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={delete_url}'


@pytest.mark.django_db
def test_user_cannot_edit_or_delete_foreign_comment(reader_client, comment):
    """Проверка доступа к чужим комментариям.

    Авторизованный пользователь не может редактировать
    или удалять чужие комментарии.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    assert reader_client.get(edit_url).status_code == HTTPStatus.NOT_FOUND
    assert reader_client.get(delete_url).status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    ('users:signup', 'users:login'),
)
def test_auth_pages_available_for_anonymous(client, url_name):
    """Проверка доступности страниц регистрации и входа.

    Тестирование доступности страниц для анонимных пользователей.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout_page_available_for_anonymous(client):
    """Проверка доступности страницы выхода.

    Страница возвращает код 200 OK при POST-запросе.
    """
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
