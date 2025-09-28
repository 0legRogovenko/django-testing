import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.mark.parametrize(
    'url_name,method',
    [
        ('news:home', 'get'),
        ('users:signup', 'get'),
        ('users:login', 'get'),
        ('users:logout', 'post'),
    ]
)
def test_public_pages_available_for_anonymous(client, url_name, method):
    """Проверка доступности публичных страниц.

    Главная страница, регистрация, вход и выход
    должны быть доступны анонимному пользователю.
    """
    url = reverse(url_name)
    response = getattr(client, method)(url)
    assert response.status_code == 200


def test_news_detail_available_for_anonymous(client, detail_url):
    """Проверка доступности страницы новости.

    Страница отдельной новости должна быть доступна анонимному пользователю.
    """
    response = client.get(detail_url)
    assert response.status_code == 200


@pytest.mark.parametrize('url_fixture', ['edit_url', 'delete_url'])
def test_comment_pages_available_for_author(
        author_client, request, url_fixture):
    """Проверка доступности страниц комментария для автора.

    Страницы редактирования и удаления должны быть доступны автору.
    """
    url = request.getfixturevalue(url_fixture)
    response = author_client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize('url_fixture', ['edit_url', 'delete_url'])
def test_anonymous_redirected_from_edit_delete(
        client, request, url_fixture, login_url):
    """Проверка редиректа анонимного пользователя.

    При попытке редактирования или удаления комментария должно происходить
    перенаправление на страницу авторизации.
    """
    url = request.getfixturevalue(url_fixture)
    response = client.get(url)
    assert response.status_code == 302
    expected_url = f"{login_url}?next={url}"
    assert response.url == expected_url


@pytest.mark.parametrize('url_fixture', ['edit_url', 'delete_url'])
def test_user_cannot_edit_or_delete_foreign_comment(
        reader_client, request, url_fixture):
    """Проверка запрета на работу с чужими комментариями.

    Авторизованный пользователь не должен иметь возможности
    редактировать или удалять чужие комментарии.
    """
    url = request.getfixturevalue(url_fixture)
    response = reader_client.get(url)
    assert response.status_code == 404
