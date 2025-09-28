import pytest
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_cannot_add_comment(
        client, detail_url, login_url, form_data):
    """Проверка запрета создания комментария анонимным пользователем."""
    response = client.post(detail_url, data=form_data)
    assert response.status_code == 302
    expected_url = f"{login_url}?next={detail_url}"
    assert response.url == expected_url
    assert Comment.objects.count() == 0


def test_authorized_user_can_add_comment(
        author_client, detail_url, form_data, author, news):
    """Проверка создания комментария авторизованным пользователем."""
    response = author_client.post(detail_url, data=form_data)
    assert response.status_code == 302
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize('text', ['спам', 'реклама', 'запрещено'])
def test_comment_with_forbidden_words_published(
        author_client, detail_url, author, news, text):
    """Проверка публикации комментария с запрещенными словами.

    Комментарий должен сохраняться, так как фильтрация не реализована.
    """
    response = author_client.post(detail_url, data={'text': text})
    assert response.status_code == 302
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == text
    assert comment.author == author
    assert comment.news == news


def test_author_can_edit_own_comment(
        author_client, edit_url, updated_form_data, author, news, comment):
    """Проверка возможности редактирования комментария автором."""
    response = author_client.post(edit_url, data=updated_form_data)
    assert response.status_code == 302
    updated = Comment.objects.get(id=comment.id)
    assert updated.text == updated_form_data['text']
    assert updated.author == author
    assert updated.news == news


def test_author_can_delete_own_comment(author_client, delete_url, comment):
    """Проверка возможности удаления комментария автором."""
    response = author_client.post(delete_url)
    assert response.status_code == 302
    assert Comment.objects.count() == 0


def test_user_cannot_edit_foreign_comment(reader_client, edit_url, comment):
    """Проверка запрета на редактирование чужого комментария."""
    response = reader_client.post(edit_url, data={'text': 'Попытка взлома'})
    assert response.status_code == 404
    unchanged = Comment.objects.get(id=comment.id)
    assert unchanged.text == comment.text


@pytest.mark.django_db
def test_user_cannot_delete_foreign_comment(
        reader_client, delete_url, comment):
    """Проверка запрета на удаление чужого комментария."""
    response = reader_client.post(delete_url)
    assert response.status_code == 404
    assert Comment.objects.filter(id=comment.id).exists()
