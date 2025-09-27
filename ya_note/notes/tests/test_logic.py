from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    """Тестирование логики работы заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных.

        Создается автор заметки, читатель и тестовая заметка.
        """
        cls.author = User.objects.create(username='Олег Роговенко')
        cls.reader = User.objects.create(username='Анна Путилина')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_note_create(self):
        """Тестирование создания заметки."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('notes:success'))

    def test_unique_notes_slug(self):
        """Тестирование уникальности slug заметки."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
        self.client.post(url, data, follow=True)
        response = self.client.post(url, data)
        form = response.context['form']
        error_msg = (
            'new-note - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertFormError(
            form,
            'slug',
            error_msg,
        )
        notes = Note.objects.filter(slug='new-note')
        self.assertEqual(notes.count(), 1)
        self.client.logout()

    def test_slug_is_generated_automatically(self):
        """Тестирование автоматической генерации slug."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
        }
        self.client.post(url, data, follow=True)
        notes = Note.objects.get(title=data['title'])
        expected_slug = slugify(data['title'])
        self.assertEqual(notes.slug, expected_slug)
