from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тестирование контента страниц приложения заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных.

        Создается автор заметки, читатель, тестовая заметка
        и экземпляр формы заметки.
        """
        cls.author = User.objects.create(username='Олег Роговенко')
        cls.reader = User.objects.create(username='Анна Путилина')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.form = NoteForm()

    def test_note_list_context(self):
        """Проверка отображения заметки в списке для автора."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.notes, response.context['object_list'])
        self.client.logout()

    def test_outside_notes(self):
        """Проверка отсутствия чужих заметок в списке."""
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertNotIn(self.notes, response.context['object_list'])
        self.client.logout()

    def test_form_on_add(self):
        """Проверка формы в контексте страницы добавления заметки."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], NoteForm)
        self.client.logout()

    def test_form_on_edit(self):
        """Проверка формы в контексте страницы редактирования."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.notes.slug,))
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], NoteForm)
        self.client.logout()
