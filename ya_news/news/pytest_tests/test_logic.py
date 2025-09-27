from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cannot_add_comment(client, news):
    """Проверка запрета отправки комментария анонимным пользователем."""
    url = reverse('news:detail', args=(news.id,))
    comments_count = Comment.objects.count()
    response = client.post(
        url,
        data={'text': 'Анонимный комментарий'},
    )
    login_url = reverse('users:login')
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(login_url)
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_authorized_user_can_add_comment(author_client, news, author):
    """Проверка успешной отправки комментария авторизованным пользователем."""
    url = reverse('news:detail', args=(news.id,))
    comments_count = Comment.objects.count()
    response = author_client.post(
        url,
        data={'text': 'Комментарий автора'},
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.last()
    assert comment.text == 'Комментарий автора'
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_comment_with_forbidden_words_published(author_client, news, author):
    """Проверка публикации комментария с запрещенными словами.

    Так как фильтрация запрещённых слов не реализована,
    комментарий сохраняется даже с 'плохими' словами.
    """
    url = reverse('news:detail', args=(news.id,))
    comments_count = Comment.objects.count()
    response = author_client.post(
        url,
        data={'text': 'Ужасный спам!'},
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.last()
    assert comment.text == 'Ужасный спам!'
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_author_can_edit_and_delete_own_comment(author_client, comment):
    """Проверка редактирования и удаления комментария автором.

    Автор может изменять и удалять свои комментарии.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(edit_url, data={'text': 'Обновлённый текст'})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый текст'
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_user_cannot_edit_or_delete_foreign_comment(reader_client, comment):
    """Проверка запрета на редактирование чужих комментариев.

    Авторизованный пользователь не должен иметь возможности
    редактировать или удалять чужие комментарии.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))

    response = reader_client.post(edit_url, data={'text': 'Попытка взлома'})
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
