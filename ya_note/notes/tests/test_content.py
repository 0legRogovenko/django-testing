from django.urls import reverse

from notes.forms import NoteForm
from .base import BaseTestCase

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')


class TestContent(BaseTestCase):
    """Тестирование контента страниц приложения заметок."""

    @classmethod
    def setUpClass(cls):
        """Добавляет урл редактирования,
        зависящий от slug созданной заметки.
        """
        super().setUpClass()
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_list_context(self):
        """Автор видит свою заметку в списке заметок."""
        response = self.author_client.get(LIST_URL)
        notes = response.context['object_list']
        self.assertIn(self.note, notes)

        note = next(n for n in notes if n.pk == self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_outside_notes(self):
        """Читатель не видит чужие заметки в своём списке."""
        response = self.reader_client.get(LIST_URL)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_form_on_add_and_edit(self):
        """На страницах добавления и редактирования есть форма NoteForm."""
        for url in (ADD_URL, self.edit_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
