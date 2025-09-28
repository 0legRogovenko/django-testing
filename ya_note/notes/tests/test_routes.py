from http import HTTPStatus
from .base import (
    BaseTestCase,
    LIST_URL, ADD_URL, SUCCESS_URL, HOME_URL,
    ANON_REDIRECT_LIST, ANON_REDIRECT_ADD, ANON_REDIRECT_SUCCESS,
    ANON_REDIRECT_EDIT, ANON_REDIRECT_DELETE, ANON_REDIRECT_DETAIL,
)


class TestNoteRoutes(BaseTestCase):
    """Тестирование доступности маршрутов приложения заметок."""

    def test_routes_status_codes(self):
        """Проверка доступности маршрутов для разных пользователей."""
        cases = [
            (self.client, HOME_URL, HTTPStatus.OK),
            (self.author_client, HOME_URL, HTTPStatus.OK),
            (self.reader_client, HOME_URL, HTTPStatus.OK),

            (self.author_client, LIST_URL, HTTPStatus.OK),
            (self.reader_client, LIST_URL, HTTPStatus.OK),
            (self.client, LIST_URL, HTTPStatus.FOUND),

            (self.author_client, ADD_URL, HTTPStatus.OK),
            (self.reader_client, ADD_URL, HTTPStatus.OK),
            (self.client, ADD_URL, HTTPStatus.FOUND),

            (self.author_client, SUCCESS_URL, HTTPStatus.OK),
            (self.reader_client, SUCCESS_URL, HTTPStatus.OK),
            (self.client, SUCCESS_URL, HTTPStatus.FOUND),

            (self.author_client, self.DETAIL_URL, HTTPStatus.OK),
            (self.reader_client, self.DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.client, self.DETAIL_URL, HTTPStatus.FOUND),

            (self.author_client, self.EDIT_URL, HTTPStatus.OK),
            (self.reader_client, self.EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.client, self.EDIT_URL, HTTPStatus.FOUND),

            (self.author_client, self.DELETE_URL, HTTPStatus.OK),
            (self.reader_client, self.DELETE_URL, HTTPStatus.NOT_FOUND),
            (self.client, self.DELETE_URL, HTTPStatus.FOUND),
        ]

        for client, url, expected_status in cases:
            with self.subTest(url=url,
                              client=getattr(client, 'user', 'anonymous')):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_anonymous_redirects(self):
        """Анонимный пользователь перенаправляется на логин."""
        cases = [
            (LIST_URL, ANON_REDIRECT_LIST),
            (ADD_URL, ANON_REDIRECT_ADD),
            (SUCCESS_URL, ANON_REDIRECT_SUCCESS),
            (self.EDIT_URL, ANON_REDIRECT_EDIT),
            (self.DELETE_URL, ANON_REDIRECT_DELETE),
            (self.DETAIL_URL, ANON_REDIRECT_DETAIL),
        ]
        for url, expected_redirect in cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
