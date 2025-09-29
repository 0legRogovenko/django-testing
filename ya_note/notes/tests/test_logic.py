from http import HTTPStatus

from notes.models import Note
from .base import BaseTestCase, ADD_URL, SUCCESS_URL, NOTES_EDIT, NOTES_DELETE


class TestLogic(BaseTestCase):
    """Тестирование логики работы заметок."""

    def test_note_create(self):
        """Автор создаёт заметку: редирект и корректная запись в базе."""
        ids_before = set(Note.objects.values_list('id', flat=True))

        response = self.author_client.post(ADD_URL, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = ids_after - ids_before
        self.assertEqual(len(new_ids), 1)

        created = Note.objects.get(id=new_ids.pop())
        self.assertEqual(created.title, self.form_data['title'])
        self.assertEqual(created.text, self.form_data['text'])
        self.assertEqual(created.slug, self.form_data['slug'])
        self.assertEqual(created.author, self.author)

    def test_unique_notes_slug(self):
        """Slug заметки должен быть уникальным."""
        duplicate_data = {**self.form_data, 'slug': self.note.slug}
        ids_before = set(Note.objects.values_list('id', flat=True))

        response = self.author_client.post(ADD_URL, duplicate_data)
        form = response.context['form']
        error_msg = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(form, 'slug', error_msg)
        self.assertEqual(ids_before, set(
            Note.objects.values_list('id', flat=True)))

    def test_slug_is_generated_if_not_provided(self):
        """Если slug не указан, он генерируется автоматически."""
        data = {k: v for k, v in self.form_data.items() if k != 'slug'}
        ids_before = set(Note.objects.values_list('id', flat=True))

        response = self.author_client.post(ADD_URL, data)
        self.assertRedirects(response, SUCCESS_URL)

        ids_after = set(Note.objects.values_list('id', flat=True))
        new_ids = ids_after - ids_before
        self.assertEqual(len(new_ids), 1)

        created = Note.objects.get(id=new_ids.pop())
        self.assertEqual(created.title, data['title'])
        self.assertEqual(created.text, data['text'])
        self.assertEqual(created.author, self.author)
        # Проверяем, что slug сгенерировался и не равен пустой строке
        self.assertTrue(created.slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        data = {**self.form_data, 'title': 'Обновлённый заголовок',
                'text': 'Обновлённый текст'}

        response = self.author_client.post(NOTES_EDIT, data)
        self.assertRedirects(response, SUCCESS_URL)

        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, data['title'])
        self.assertEqual(updated_note.text, data['text'])
        self.assertEqual(updated_note.slug, data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        count_before = Note.objects.count()

        response = self.author_client.post(NOTES_DELETE)
        self.assertRedirects(response, SUCCESS_URL)

        count_after = Note.objects.count()
        self.assertEqual(count_after, count_before - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_reader_cannot_edit_foreign_note(self):
        """Чужой пользователь не может редактировать заметку автора."""
        response = self.reader_client.post(NOTES_EDIT, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        unchanged = Note.objects.get(pk=self.note.pk)
        self.assertEqual(unchanged.title, self.note.title)
        self.assertEqual(unchanged.text, self.note.text)
        self.assertEqual(unchanged.slug, self.note.slug)
        self.assertEqual(unchanged.author, self.note.author)

    def test_reader_cannot_delete_foreign_note(self):
        """Чужой пользователь не может удалить заметку автора."""
        count_before = Note.objects.count()

        response = self.reader_client.post(NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        count_after = Note.objects.count()
        self.assertEqual(count_after, count_before)

        # Проверяем, что запись осталась неизменной
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
