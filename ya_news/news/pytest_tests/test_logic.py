from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS
from news.models import Comment


pytestmark = pytest.mark.django_db

# Константы модуля
FORM_DATA = {'text': 'Текст формы'}
UPDATED_FORM_DATA = {'text': 'Обновлённый текст'}
HACKING_ATTEMPT_DATA = {'text': 'Попытка взлома'}


@pytest.fixture
def login_redirect_to_detail(login_url, detail_url):
    """URL редиректа на логин при попытке добавления комментария анонимом."""
    return f'{login_url}?next={detail_url}'


def test_anonymous_cannot_add_comment(client,
                                      detail_url, login_redirect_to_detail):
    """Анонимный пользователь не может добавить комментарий."""
    response = client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == login_redirect_to_detail
    assert Comment.objects.count() == 0


def test_authorized_user_can_add_comment(author_client,
                                         detail_url, author, news):
    """Авторизованный пользователь может добавить комментарий."""
    response = author_client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1

    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('text', BAD_WORDS)
def test_comment_with_forbidden_words_not_published(author_client,
                                                    detail_url, text):
    """Комментарий с запрещёнными словами не сохраняется (валидация формы)."""
    response = author_client.post(detail_url, data={'text': text})
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    form = response.context['form']
    assert 'text' in form.errors


def test_author_can_edit_own_comment(author_client, edit_url, comment):
    """Автор может редактировать свой комментарий; привязки не меняются."""
    before_author = comment.author
    before_news = comment.news

    response = author_client.post(edit_url, data=UPDATED_FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND

    updated = Comment.objects.get(id=comment.id)
    assert updated.text == UPDATED_FORM_DATA['text']
    assert updated.author == before_author
    assert updated.news == before_news


def test_author_can_delete_own_comment(author_client, delete_url, comment):
    """Автор может удалить свой комментарий."""
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cannot_edit_foreign_comment(reader_client, edit_url, comment):
    """Пользователь не может редактировать чужой комментарий"""
    before_text = comment.text
    before_author = comment.author
    before_news = comment.news

    response = reader_client.post(edit_url, data=HACKING_ATTEMPT_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged = Comment.objects.get(id=comment.id)
    assert unchanged.text == before_text
    assert unchanged.author == before_author
    assert unchanged.news == before_news


def test_user_cannot_delete_foreign_comment(reader_client,
                                            delete_url, comment):
    """Пользователь не может удалить чужой комментарий."""
    before_text = comment.text
    before_author = comment.author
    before_news = comment.news

    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    assert Comment.objects.filter(id=comment.id).exists()
    still = Comment.objects.get(id=comment.id)
    assert still.text == before_text
    assert still.author == before_author
    assert still.news == before_news
