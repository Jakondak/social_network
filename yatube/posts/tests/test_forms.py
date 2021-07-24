import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

User = get_user_model()
MEDIA_ROOT_TEMP = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT_TEMP)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title="Тестовое имя сообщества",
            slug="test-slug",
            description="Тестовое описание сообщества")
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        tasks_count = Post.objects.count()

        form_data = {
            "text": "Тестовый заголовок",
            "group": TaskCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse("post_new"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_edit_post(self):
        form_data = {
            "text": "Измененный тест",
            "group": TaskCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            f"/{self.user.username}/{self.post.pk}/edit/",
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            str(response.context["post"]), "Измененный тест")

    def test_form_pict(self):
        post_count = Post.objects.count()
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
            content_type="image/gif"
        )
        form_data = {
            "text": "Тестовый заголовок",
            "group": self.group.id,
            "image": uploaded,
        }
        self.authorized_client.post(
            reverse("post_new"),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_create_comment(self):
        comments_count = Comment.objects.count()

        form_data = {
            "text": "Тестовый комментарий",
        }
        self.authorized_client.post(
            reverse("add_comment", args=[f"{self.user.username}", f"{self.post.pk}"]),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
