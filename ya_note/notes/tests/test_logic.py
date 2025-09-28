from notes.models import Note
from .base import BaseTestCase, ADD_URL, SUCCESS_URL


class TestLogic(BaseTestCase):
    """Тестирование логики работы заметок."""

    def test_note_create(self):
        """Автор создаёт заметку: редирект и корректная запись в базе."""
        ids = set(Note.objects.values_list('id', flat=True))

        response = self.author_client.post(ADD_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        new_ids = set(Note.objects.values_list('id', flat=True)) - ids
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

        ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_URL, duplicate_data)

        form = response.context['form']
        error_msg = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(form, 'slug', error_msg)
        self.assertEqual(ids, set(Note.objects.values_list('id', flat=True)))

    def test_slug_is_generated_if_not_provided(self):
        """Если slug не указан, он генерируется автоматически."""
        data = self.form_data.copy()
        data.pop('slug')
        response = self.author_client.post(ADD_URL, data)
        self.assertRedirects(response, SUCCESS_URL)

        note = Note.objects.latest('id')
        self.assertTrue(note.slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        data = {
            'title': 'Обновлённый заголовок',
            'text': 'Обновлённый текст',
            'slug': self.note.slug,
        }
        response = self.author_client.post(self.EDIT_URL, data)
        self.assertRedirects(response, SUCCESS_URL)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, data['title'])
        self.assertEqual(self.note.text, data['text'])

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())
