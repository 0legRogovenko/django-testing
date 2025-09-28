from http import HTTPStatus
import pytest

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND

CLIENT = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')

HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')


@pytest.mark.parametrize(
    'client_fixture, url, method, expected_status',
    [
        (CLIENT, HOME_URL, 'get', OK),
        (AUTHOR_CLIENT, HOME_URL, 'get', OK),
        (READER_CLIENT, HOME_URL, 'get', OK),

        (CLIENT, LOGIN_URL, 'get', OK),
        (AUTHOR_CLIENT, LOGIN_URL, 'get', OK),
        (READER_CLIENT, LOGIN_URL, 'get', OK),

        (CLIENT, DETAIL_URL, 'get', OK),
        (AUTHOR_CLIENT, DETAIL_URL, 'get', OK),
        (READER_CLIENT, DETAIL_URL, 'get', OK),

        (CLIENT, EDIT_URL, 'get', FOUND),
        (AUTHOR_CLIENT, EDIT_URL, 'get', OK),
        (READER_CLIENT, EDIT_URL, 'get', NOT_FOUND),

        (CLIENT, DELETE_URL, 'get', FOUND),
        (AUTHOR_CLIENT, DELETE_URL, 'get', OK),
        (READER_CLIENT, DELETE_URL, 'get', NOT_FOUND),
    ],
)
def test_status_codes_for_various_pages(client_fixture,
                                        url, method, expected_status):
    """Проверка доступности страниц
    для разных пользователей с точным кодом возврата.
    """
    response = getattr(client_fixture, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_redirect',
    [
        (EDIT_URL, pytest.lazy_fixture('login_url_with_edit')),
        (DELETE_URL, pytest.lazy_fixture('login_url_with_delete')),
    ],
)
def test_anonymous_redirects(client, url, expected_redirect):
    """Аноним перенаправляется на логин при попытке редактировать/удалить."""
    response = client.get(url)
    assert response.url == expected_redirect
