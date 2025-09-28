from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс с общими данными и клиентами."""

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
        cls.form = NoteForm()

        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))


class TestContent(BaseTestCase):
    """Тестирование контента страниц приложения заметок."""

    def test_note_list_context(self):
        """Проверка наличия заметки в списке заметок автора."""
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

        note_from_context = object_list[0]
        self.assertEqual(note_from_context.title, self.note.title)
        self.assertEqual(note_from_context.text, self.note.text)
        self.assertEqual(note_from_context.author, self.note.author)
        self.assertEqual(note_from_context.slug, self.note.slug)

    def test_outside_notes(self):
        """Читатель не видит чужие заметки в списке."""
        response = self.reader_client.get(self.list_url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_form_on_add_and_edit(self):
        """На страницах добавления и редактирования есть форма NoteForm."""
        for url in (self.add_url, self.edit_url):
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
