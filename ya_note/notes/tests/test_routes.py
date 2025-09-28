from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseRoutesTestCase(TestCase):
    """Базовый класс с общими данными, клиентами и урлами."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных перед запуском тестов."""
        cls.author = User.objects.create(username='Олег Роговенко')
        cls.reader = User.objects.create(username='Анна Путилина')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')


class TestNoteRoutes(BaseRoutesTestCase):
    """Тестирование доступности маршрутов приложения заметок."""

    def test_routes_status_codes(self):
        """Проверка доступности маршрутов для разных пользователей."""
        cases = [
            (self.client, self.home_url, 200),
            (self.author_client, self.home_url, 200),
            (self.reader_client, self.home_url, 200),

            (self.author_client, self.list_url, 200),
            (self.reader_client, self.list_url, 200),
            (self.client, self.list_url, 302),

            (self.author_client, self.add_url, 200),
            (self.reader_client, self.add_url, 200),
            (self.client, self.add_url, 302),

            (self.author_client, self.success_url, 200),
            (self.reader_client, self.success_url, 200),
            (self.client, self.success_url, 302),

            (self.author_client, self.detail_url, 200),
            (self.reader_client, self.detail_url, 404),
            (self.client, self.detail_url, 302),

            (self.author_client, self.edit_url, 200),
            (self.reader_client, self.edit_url, 404),
            (self.client, self.edit_url, 302),

            (self.author_client, self.delete_url, 200),
            (self.reader_client, self.delete_url, 404),
            (self.client, self.delete_url, 302),
        ]

        for client, url, expected_status in cases:
            with self.subTest(
                url=url,
                client=getattr(client, 'user', 'anonymous')
            ):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_anonymous_redirects(self):
        """Анонимный пользователь перенаправляется на логин."""
        urls = [
            self.list_url,
            self.add_url,
            self.success_url,
            self.edit_url,
            self.delete_url,
            self.detail_url
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                expected_redirect = f'{self.login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)
