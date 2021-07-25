from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

GROUP_LINK = "group"
NEW_POST_LINK = "new"
EDIT_LINK = "edit"
REDIRECT_ON_LOGIN_PAGE_LINK = "auth/login/?next="
COMMENT_LINK = "comment"
TITLE = "Название"
SLUG = "test-slug"
DESCRIPTION = "Описание"
TEXT = "Текст"


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.user_watcher = User.objects.create_user(username="watcher")
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_watcher_client = Client()
        self.authorized_watcher_client.force_login(self.user_watcher)

    def test_all_urls_exist_at_desired_location(self):
        """Проверка доступности страниц в соответствии с правами
        пользователей."""
        type_client_urls_tuples = (
            (reverse("index"), self.guest_client),
            (f"/{GROUP_LINK}/{self.group.slug}/", self.guest_client),
            (f"/{NEW_POST_LINK}/", self.authorized_client),
            (f"/{self.user.username}/", self.guest_client),
            (f"/{self.user.username}/{self.post.pk}/", self.guest_client),
            (f"/{self.user.username}/{self.post.pk}/{EDIT_LINK}/",
                self.authorized_client),
            (reverse("about:author"), self.guest_client),
            (reverse("about:tech"), self.guest_client),
        )
        for tuple_item in type_client_urls_tuples:
            adress = tuple_item[0]
            client_type = tuple_item[1]
            with self.subTest(adress=adress):
                response = client_type.get(adress)
                self.assertEqual(response.status_code, 200)

    def test_all_urls_redirect_code(self):
        """
        Проверка ожидаемых кодов
        редиректов в соответствии с правами пользователей.
        """
        type_client_urls_tuples = (
            (f"/{NEW_POST_LINK}/", self.guest_client),
            (f"/{self.user.username}/{self.post.pk}/{EDIT_LINK}/",
             self.guest_client),
            (f"/{self.user.username}/{self.post.pk}/{EDIT_LINK}/",
             self.authorized_watcher_client)
        )
        for tuple_item in type_client_urls_tuples:
            adress = tuple_item[0]
            client_type = tuple_item[1]
            with self.subTest(adress=adress):
                response = client_type.get(adress)
                self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """Вызываются ли ожидаемые шаблоны."""
        cache.clear()
        templates_url_names = {
            "posts/index.html": "/",
            "posts/group.html": f"/{GROUP_LINK}/{self.group.slug}/",
            "users/new_post.html": f"/{NEW_POST_LINK}/"
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_edit_url_correct_template(self):
        """Вызывается ошидаемый шаблон для страницы редактирования."""
        cache.clear()
        response = self.authorized_client.get(
            f"/{self.user.username}/{self.post.pk}/{EDIT_LINK}/"
        )
        self.assertTemplateUsed(response, "users/new_post.html")

    def test_redirects_assert(self):
        """
        Вызываются ли ожидаемые редиректы в соответствии с правами
        пользователей.
        """
        type_client_urls_tuples = (
            (f"/{self.user.username}/{self.post.pk}/{EDIT_LINK}/",
             self.guest_client,
             f"/{REDIRECT_ON_LOGIN_PAGE_LINK}/{self.user.username}/"
             f"{self.post.pk}/{EDIT_LINK}/"),
            (f"/{self.user.username}/{self.post.pk}/{EDIT_LINK}/",
             self.authorized_watcher_client,
             f"/{self.user.username}/{self.post.pk}/"),
            (f"/{self.user.username}/{self.post.pk}/{COMMENT_LINK}/",
             self.guest_client,
             f"/{REDIRECT_ON_LOGIN_PAGE_LINK}/{self.user.username}/"
             f"{self.post.pk}/{COMMENT_LINK}/"),
        )
        for tuple_item in type_client_urls_tuples:
            adress = tuple_item[0]
            client_type = tuple_item[1]
            adress_redirect = tuple_item[2]
            with self.subTest(adress=adress):
                response = client_type.get(adress)
                self.assertRedirects(response, adress_redirect)

    def test_page_not_found_error(self):
        """Вызов ошибки 404 - не найдена страница."""
        response = self.authorized_client.get(f"/{100*100}/")
        self.assertEqual(response.status_code, 404)
