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
        duplicate_data = {**self.form_data, 'slug': self.note.slug}

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
        data = {k: v for k, v in self.form_data.items() if k != 'slug'}

        count_before = Note.objects.count()
        response = self.author_client.post(ADD_URL, data)
        self.assertRedirects(response, SUCCESS_URL)

        self.assertEqual(Note.objects.count(), count_before + 1)

        note = Note.objects.latest('pk')

        self.assertEqual(note.title, data['title'])
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.author, self.author)

        self.assertTrue(note.slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        data = {**self.form_data, 'title': 'Обновлённый заголовок',
                'text': 'Обновлённый текст', 'slug': self.note.slug}

        response = self.author_client.post(self.EDIT_URL, data)
        self.assertRedirects(response, SUCCESS_URL)

        updated_note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(updated_note.title, data['title'])
        self.assertEqual(updated_note.text, data['text'])
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count_before = Note.objects.count()

        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_reader_cannot_edit_foreign_note(self):
        """Чужой пользователь не может редактировать заметку автора."""
        data = {
            **self.form_data,
            'title': 'Попытка взлома',
            'text': 'Чужой текст',
            'slug': self.note.slug
        }

        response = self.reader_client.post(self.EDIT_URL, data)
        self.assertEqual(response.status_code, 404)

        unchanged_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)

    def test_reader_cannot_delete_foreign_note(self):
        """Чужой пользователь не может удалить заметку автора."""
        notes_count_before = Note.objects.count()

        response = self.reader_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, 404)

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
