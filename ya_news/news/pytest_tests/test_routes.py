from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name, method, expected_status',
    [
        ('news:home', 'get', HTTPStatus.OK),
        ('users:signup', 'get', HTTPStatus.OK),
        ('users:login', 'get', HTTPStatus.OK),
        ('users:logout', 'post', HTTPStatus.OK),
    ],
)
def test_public_pages_available_for_anonymous(
    client, url_name, method, expected_status
):
    """Проверка доступности публичных страниц для анонимного пользователя."""
    from django.urls import reverse

    url = reverse(url_name)
    response = getattr(client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture, expected_status',
    [
        ('detail_url', HTTPStatus.OK),
        ('edit_url', HTTPStatus.OK),
        ('delete_url', HTTPStatus.OK),
    ],
)
def test_pages_for_author(author_client,
                          request, url_fixture, expected_status):
    """Автор имеет доступ к своим страницам комментариев и новости."""
    url = request.getfixturevalue(url_fixture)
    response = author_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url_fixture', ['edit_url', 'delete_url'])
def test_anonymous_redirected_from_edit_delete(
    client, request, url_fixture, login_url
):
    """Аноним перенаправляется на логин при попытке редактировать/удалить."""
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={url}'


@pytest.mark.parametrize(
    'url_fixture, expected_status',
    [
        ('edit_url', HTTPStatus.NOT_FOUND),
        ('delete_url', HTTPStatus.NOT_FOUND),
    ],
)
def test_user_cannot_edit_or_delete_foreign_comment(
    reader_client, request, url_fixture, expected_status
):
    """Авторизованный пользователь не может редактировать или удалять чужие
    комментарии.
    """
    url = request.getfixturevalue(url_fixture)
    response = reader_client.get(url)
    assert response.status_code == expected_status
