from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олег Роговенко')
        cls.reader = User.objects.create(username='Анна Путилина')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_note_list_for_reader_and_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest('notes:list'):
                url = reverse('notes:list')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
            self.client.logout()

    def test_notes_for_anonymous_without_args(self):
        """Проверка редиректа для анонимных пользователей.

        Тестирование редиректа на маршрутах без аргументов.
        """
        login_url = reverse('users:login')
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_notes_for_anonymous_with_args(self):
        """Проверка редиректа для анонимных пользователей.

        Тестирование редиректа на маршрутах, требующих аргументы.
        """
        login_url = reverse('users:login')
        urls = (
            'notes:edit',
            'notes:delete',
            'notes:detail',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_edit_and_delete(self):
        """Проверка доступности маршрутов редактирования и удаления.

        Тестирование доступа разных пользователей к функциям
        редактирования и удаления заметок.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = ('notes:edit', 'notes:delete')
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
            self.client.logout()

    def test_availability_for_add(self):
        """Проверка доступности маршрута добавления заметки.

        Тестирование доступа разных пользователей к созданию новых заметок.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest('notes:add'):
                url = reverse('notes:add')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
            self.client.logout()

    def test_availability_for_detail(self):
        """Проверка доступности детальной страницы заметки.

        Тестирование доступа разных пользователей к просмотру заметок.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest('notes:detail'):
                url = reverse('notes:detail', args=(self.notes.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
            self.client.logout()

    def test_availability_for_home(self):
        """Проверка доступности главной страницы для всех пользователей."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
            (None, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            if user is not None:
                self.client.force_login(user)
            with self.subTest(users=getattr(user, 'username', 'anonymous')):
                url = reverse('notes:home')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
            if user is not None:
                self.client.logout()

    def test_availability_for_success(self):
        """Проверка доступности страницы успешного добавления.

        Тестирование доступа разных пользователей к странице
        успешного добавления заметки.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest('notes:success'):
                url = reverse('notes:success')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
            self.client.logout()
