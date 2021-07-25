import shutil
import tempfile

from bs4 import BeautifulSoup
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TITLE = "Название"
SLUG = "test-slug"
DESCRIPTION = "Описание"
TEXT = "Текст"


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif",
        )
        cls.image = uploaded
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.image,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    """Соответствует ли ожиданиям словарь context главной страницы"""
    def test_main_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        first_object = response.context["page"][0]
        post_text = first_object.text
        self.assertEqual(post_text, TEXT)

    """Соответствует ли ожиданиям словарь context страницы группы"""
    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse("group", args=f"{self.group.slug}"))
        first_object = response.context["page"][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, TEXT)

    """Соответствует ли ожиданиям словарь context страницы создания поста"""
    def test_new_post_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse("post_new"))
        form_fields = {
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    """Соответствует ли ожиданиям словарь context страницы редактирования
    отдельного поста"""
    def test_edit_post_page_shows_correct_context(self):
        response = self.authorized_client.get(f"/{self.user.username}/"
                                              f"{self.post.pk}/edit/")
        form_fields = {
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    """При создании поста в группе1, он не появляется на старинице группы2"""
    def test_new_post_group_page_dont_show_on_another_group_page(self):
        response = self.authorized_client.get(
            reverse("group", args=[f"{self.group.slug}"]))
        first_object = response.context["page"][0]
        group = first_object.group
        self.assertEqual(str(group), TITLE)

    """Соответствует ли ожиданиям словарь context стриницы профиля юзера"""
    def test_user_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse("profile", args=[f"{self.user.username}"]))
        first_object = response.context["page"][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, TEXT)

    """Соответствует ли ожиданиям словарь context страницы отдельного поста"""
    def test_one_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "post",
                args=[f"{self.user.username}", f"{self.post.pk}"]
            )
        )
        first_object = response.context["post"]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, TEXT)

    """Соответствует ли ожиданиям словарь context дополнительные страницы о
    технология и авторе"""
    def test_pages_uses_correct_template(self):
        templates_page_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    """Соответствует ли ожиданиям словарь context страницы главной страницы"""
    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        first_object = response.context["page"][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, str(self.post))

    """Картинка отображается на главной странице"""
    def test_main_page_shows_pict(self):
        response = self.authorized_client.get(reverse("index"))
        first_object = response.context["page"][0]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    """Картинка отображается на странице пользователя"""
    def test_profile_page_shows_pict(self):
        response = self.authorized_client.get(
            reverse("profile", args=[f"{self.user.username}"]))
        first_object = response.context["page"][0]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    """Картинка отображается на странице группы"""
    def test_group_page_shows_pict(self):
        response = self.authorized_client.get(
            reverse("group", args=[f"{self.group.slug}"]))
        first_object = response.context["page"][0]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    """Картинка отображается на странице отдельного поста"""
    def test_one_post_page_shows_pict(self):
        response = self.authorized_client.get(
            reverse(
                "post",
                args=[f"{self.user.username}", f"{self.post.pk}"]
            )
        )
        first_object = response.context["post"]
        image = first_object.image
        self.assertEqual(image.name.split("/")[-1], self.image.name)

    """Тестирование работы кэширования на главной странице"""
    def test_main_page_cache(self):
        response = self.authorized_client.get(reverse("index"))
        Post.objects.create(
            text="Тестовый текст в cache",
            author=self.user,
        )
        response_cache = self.authorized_client.get(reverse("index"))
        html_string = response_cache.content.decode("UTF-8")
        html_string = BeautifulSoup(html_string, "html.parser")
        count_posts_cache = len(html_string.findAll("small"))
        self.assertEqual(
            count_posts_cache,
            len(response.context.get("page").object_list)
        )

    """
    Авторизованный пользователь может подписываться/отписываться на/от других
    """
    def test_authorized_user_can_follow_unfollow_another_users(self):
        self.user_1 = User.objects.create_user(username="test_user_1")
        followings_before = self.user_1.follower.count()
        self.follow = Follow.objects.create(author=self.user, user=self.user_1)
        followings_after_follow = self.user_1.follower.count()
        self.unfollow = Follow.objects.filter(
            author=self.user,
            user=self.user_1
        ).delete()
        followings_after_delete = self.user_1.following.count()
        self.assertNotEqual(followings_before, followings_after_follow)
        self.assertEqual(followings_before, followings_after_delete)

    """Новая запись пользователя появляется в ленте тех, кто на него подписан
     и не появляется в ленте тех, кто не подписан на него"""
    def test_new_post_shows_on_the_right_lenta_of_posts(self):

        self.user_1 = User.objects.create_user(username="test_user_1")
        self.user_2 = User.objects.create_user(username="test_user_2")

        self.authorized_client_user_1 = Client()
        self.authorized_client_user_1.force_login(self.user_1)
        self.authorized_client_user_2 = Client()
        self.authorized_client_user_2.force_login(self.user_2)

        Follow.objects.create(author=self.user, user=self.user_1)

        response_user_1 = self.authorized_client_user_1.get(
            reverse("follow_index")
        )
        response_user_2 = self.authorized_client_user_2.get(
            reverse("follow_index")
        )

        posts_count_user_1_before_new_post = len(
            response_user_1.context["page"]
        )
        posts_count_user_2_before_new_post = len(
            response_user_2.context["page"]
        )

        Post.objects.create(
            text="Тестовый текст",
            author=self.user
        )

        response_user_1_after_new_post = self.authorized_client_user_1.get(
            reverse("follow_index")
        )
        response_user_2_after_new_post = self.authorized_client_user_2.get(
            reverse("follow_index")
        )

        posts_count_user_1_after_new_post = len(
            response_user_1_after_new_post.context["page"]
        )
        posts_count_user_2_after_new_post = len(
            response_user_2_after_new_post.context["page"]
        )

        self.assertNotEqual(
            posts_count_user_1_before_new_post,
            posts_count_user_1_after_new_post
        )
        self.assertEqual(
            posts_count_user_2_before_new_post,
            posts_count_user_2_after_new_post
        )


class PaginatorViewsTest(TestCase):
    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        num = 13
        Post.objects.bulk_create([
            Post(text=f"Тестовый текст номер {item}",
                 author=cls.user) for item in range(num)
        ])

    """Тестрование работы Пагинатора"""
    def test_first_page_contains_certain_amount_records(self):
        response_first_page = self.authorized_client.get(reverse("index"))
        response_second_page = self.authorized_client.get(
            reverse("index") + "?page=2"
        )
        self.assertEqual(
            len(response_first_page.context.get("page").object_list),
            10
        )
        self.assertEqual(
            len(response_second_page.context.get("page").object_list),
            3
        )
