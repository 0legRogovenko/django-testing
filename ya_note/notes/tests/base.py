from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LIST_URL = reverse('notes:list')
LOGIN_URL = reverse('users:login')
HOME_URL = reverse('notes:home')


class BaseTestCase(TestCase):
    """Базовый класс с общими данными и клиентами."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олег Роговенко')
        cls.reader = User.objects.create(username='Анна Путилина')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

        # Динамические урлы считаем после создания заметки
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))

        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
