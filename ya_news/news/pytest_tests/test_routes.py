from http import HTTPStatus

import pytest

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url, method, expected_status',
    [
        (pytest.lazy_fixture('home_url'), 'get', OK),
        (pytest.lazy_fixture('login_url'), 'get', OK),
        (pytest.lazy_fixture('detail_url'), 'get', OK),
        (pytest.lazy_fixture('edit_url'), 'get', OK),
        (pytest.lazy_fixture('delete_url'), 'get', OK),
    ],
)
def test_status_codes_for_various_pages(client, author_client, reader_client,
                                        url, method, expected_status):
    """Проверка доступности страниц для разных пользователей."""
    response = getattr(client, method)(url)
    response_author = getattr(author_client, method)(url)
    response_reader = getattr(reader_client, method)(url)
    assert response.status_code in (OK, FOUND)
    assert response_author.status_code in (OK, FOUND, NOT_FOUND)
    assert response_reader.status_code in (OK, FOUND, NOT_FOUND)


@pytest.mark.parametrize(
    'url, expected_redirect',
    [
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('login_url'),
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('login_url'),
        ),
    ],
)
def test_anonymous_redirects(client, url, expected_redirect):
    """Аноним перенаправляется на логин при попытке редактировать/удалить."""
    response = client.get(url)
    assert response.status_code == FOUND
    assert response.url == f'{expected_redirect}?next={url}'


@pytest.mark.parametrize(
    'url, expected_status',
    [
        (pytest.lazy_fixture('edit_url'), NOT_FOUND),
        (pytest.lazy_fixture('delete_url'), NOT_FOUND),
    ],
)
def test_reader_cannot_edit_or_delete_foreign_comment(reader_client,
                                                      url, expected_status):
    """Читатель не может редактировать или удалять чужие комментарии."""
    response = reader_client.get(url)
    assert response.status_code == expected_status
