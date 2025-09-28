from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


TEST_NOTE_SLUG = 'slug'

ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LIST_URL = reverse('notes:list')
LOGIN_URL = reverse('users:login')
HOME_URL = reverse('notes:home')

NOTES_EDIT = reverse('notes:edit', args=(TEST_NOTE_SLUG,))
NOTES_DETAIL = reverse('notes:detail', args=(TEST_NOTE_SLUG,))
NOTES_DELETE = reverse('notes:delete', args=(TEST_NOTE_SLUG,))

ANON_REDIRECT_LIST = f'{LOGIN_URL}?next={LIST_URL}'
ANON_REDIRECT_ADD = f'{LOGIN_URL}?next={ADD_URL}'
ANON_REDIRECT_SUCCESS = f'{LOGIN_URL}?next={SUCCESS_URL}'
ANON_REDIRECT_EDIT = f'{LOGIN_URL}?next={NOTES_EDIT}'
ANON_REDIRECT_DELETE = f'{LOGIN_URL}?next={NOTES_DELETE}'
ANON_REDIRECT_DETAIL = f'{LOGIN_URL}?next={NOTES_DETAIL}'


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
        cls.EDIT_URL = NOTES_EDIT
        cls.DETAIL_URL = NOTES_DETAIL
        cls.DELETE_URL = NOTES_DELETE

        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)

        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
