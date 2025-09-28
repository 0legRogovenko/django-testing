from http import HTTPStatus

import pytest

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND

HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')


@pytest.mark.parametrize(
    'client_fixture, url, method, expected_status',
    [
        ('client', HOME_URL, 'get', OK),
        ('author_client', HOME_URL, 'get', OK),
        ('reader_client', HOME_URL, 'get', OK),

        ('client', LOGIN_URL, 'get', OK),
        ('author_client', LOGIN_URL, 'get', OK),
        ('reader_client', LOGIN_URL, 'get', OK),

        ('client', DETAIL_URL, 'get', OK),
        ('author_client', DETAIL_URL, 'get', OK),
        ('reader_client', DETAIL_URL, 'get', OK),

        ('client', EDIT_URL, 'get', FOUND),
        ('author_client', EDIT_URL, 'get', OK),
        ('reader_client', EDIT_URL, 'get', NOT_FOUND),

        ('client', DELETE_URL, 'get', FOUND),
        ('author_client', DELETE_URL, 'get', OK),
        ('reader_client', DELETE_URL, 'get', NOT_FOUND),
    ],
)
def test_status_codes_for_various_pages(request, client_fixture,
                                        url, method, expected_status):
    """Проверка доступности страниц
    для разных пользователей с точным кодом возврата.
    """
    client = request.getfixturevalue(client_fixture)
    response = getattr(client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_redirect',
    [
        (EDIT_URL, LOGIN_URL),
        (DELETE_URL, LOGIN_URL),
    ],
)
def test_anonymous_redirects(client, url, expected_redirect):
    """Аноним перенаправляется на логин при попытке редактировать/удалить."""
    response = client.get(url)
    assert response.status_code == FOUND
    assert response.url == f'{expected_redirect}?next={url}'
