from http import HTTPStatus

from django.urls import reverse

from .base import (
    BaseTestCase,
    LIST_URL,
    ADD_URL,
    SUCCESS_URL,
    LOGIN_URL,
    HOME_URL,
)


class TestNoteRoutes(BaseTestCase):
    """Тестирование доступности маршрутов приложения заметок."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

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

            (self.author_client, self.detail_url, HTTPStatus.OK),
            (self.reader_client, self.detail_url, HTTPStatus.NOT_FOUND),
            (self.client, self.detail_url, HTTPStatus.FOUND),

            (self.author_client, self.edit_url, HTTPStatus.OK),
            (self.reader_client, self.edit_url, HTTPStatus.NOT_FOUND),
            (self.client, self.edit_url, HTTPStatus.FOUND),

            (self.author_client, self.delete_url, HTTPStatus.OK),
            (self.reader_client, self.delete_url, HTTPStatus.NOT_FOUND),
            (self.client, self.delete_url, HTTPStatus.FOUND),
        ]

        for client, url, expected_status in cases:
            with self.subTest(
                url=url,
                client=getattr(client, 'user', 'anonymous'),
            ):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_anonymous_redirects(self):
        """Анонимный пользователь перенаправляется на логин."""
        urls = [
            LIST_URL,
            ADD_URL,
            SUCCESS_URL,
            self.edit_url,
            self.delete_url,
            self.detail_url,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected_redirect = f'{LOGIN_URL}?next={url}'
                self.assertRedirects(response, expected_redirect)
