from notes.models import Note
from .base import BaseTestCase, ADD_URL, SUCCESS_URL


class TestLogic(BaseTestCase):
    """Тестирование логики работы заметок."""

    def test_note_create(self):
        """Автор создаёт заметку: редирект и корректная запись в базе."""
        response = self.author_client.post(ADD_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        self.assertEqual(Note.objects.count(), 2)
        created = Note.objects.exclude(pk=self.note.pk).get()
        self.assertEqual(created.title, self.form_data['title'])
        self.assertEqual(created.text, self.form_data['text'])
        self.assertEqual(created.slug, self.form_data['slug'])
        self.assertEqual(created.author, self.author)

    def test_unique_notes_slug(self):
        """Slug заметки должен быть уникальным."""
        self.author_client.post(ADD_URL, self.form_data)

        duplicate_data = self.form_data.copy()
        duplicate_data['slug'] = Note.objects.get(
            slug=self.form_data['slug']
        ).slug
        response = self.author_client.post(ADD_URL, duplicate_data)

        form = response.context['form']
        error_msg = (
            f"{self.form_data['slug']} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(form, 'slug', error_msg)
        self.assertEqual(Note.objects.count(), 2)

    def test_slug_is_generated_automatically(self):
        """Если slug не указан, он генерируется автоматически из title."""
        self.form_data.copy()
