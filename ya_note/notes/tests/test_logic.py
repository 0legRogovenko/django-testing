from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
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

        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.list_url = reverse('notes:list')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
        cls.note_data_without_slug = {
            'title': 'Новая заметка без slug',
            'text': 'Текст новой заметки',
        }


class TestLogic(BaseTestCase):
    """Тестирование логики работы заметок."""

    def test_note_create(self):
        """Автор создаёт заметку: редирект и корректная запись в базе."""
        response = self.author_client.post(
            self.add_url, self.note_data, follow=True
        )
        self.assertRedirects(response, self.success_url)

        self.assertEqual(Note.objects.count(), 2)
        created = Note.objects.latest('id')
        self.assertEqual(created.title, self.note_data['title'])
        self.assertEqual(created.text, self.note_data['text'])
        self.assertEqual(created.slug, self.note_data['slug'])
        self.assertEqual(created.author, self.author)

    def test_unique_notes_slug(self):
        """Slug заметки должен быть уникальным."""
        self.author_client.post(self.add_url, self.note_data, follow=True)
        response = self.author_client.post(self.add_url, self.note_data)
        form = response.context['form']
        error_msg = (
            'new-note - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertFormError(form, 'slug', error_msg)
        self.assertEqual(Note.objects.filter(slug='new-note').count(), 1)

    def test_slug_is_generated_automatically(self):
        """Если slug не указан, он генерируется автоматически из title."""
        self.author_client.post(
            self.add_url,
            self.note_data_without_slug,
            follow=True
        )

        self.assertEqual(Note.objects.count(), 2)
        created = Note.objects.latest('id')
        expected_slug = slugify(self.note_data_without_slug['title'])
        self.assertEqual(created.slug, expected_slug)
        self.assertEqual(created.title, self.note_data_without_slug['title'])
        self.assertEqual(created.text, self.note_data_without_slug['text'])
        self.assertEqual(created.author, self.author)
