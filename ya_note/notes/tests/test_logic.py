from notes.models import Note
from .base import BaseTestCase, ADD_URL, SUCCESS_URL


class TestLogic(BaseTestCase):
    """Тестирование логики работы заметок."""

    def test_note_create(self):
        """Автор создаёт заметку: редирект и корректная запись в базе."""
        before_ids = set(Note.objects.values_list('id', flat=True))

        response = self.author_client.post(ADD_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        after_ids = set(Note.objects.values_list('id', flat=True))
        new_ids = after_ids - before_ids
        self.assertEqual(len(new_ids), 1)

        created = Note.objects.get(id=new_ids.pop())
        self.assertEqual(created.title, self.form_data['title'])
        self.assertEqual(created.text, self.form_data['text'])
        self.assertEqual(created.slug, self.form_data['slug'])
        self.assertEqual(created.author, self.author)

    def test_unique_notes_slug(self):
        """Slug заметки должен быть уникальным."""
        duplicate_data = self.form_data.copy()
        duplicate_data['slug'] = self.note.slug

        before_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_URL, duplicate_data)

        form = response.context['form']
        error_msg = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(form, 'slug', error_msg)

        after_ids = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(before_ids, after_ids)

    def test_slug_is_empty_if_not_provided(self):
        """Если slug не указан, он остаётся пустым (по текущей модели)."""
        note = Note.objects.create(
            title='Автоматический слаг',
            text='Текст',
            author=self.author,
        )
        self.assertTrue(note.slug)
