from django.test import TestCase

from ..models import Group, Post

TEXT = "Текст"
TITLE = "Название"
SLUG = "test-slug"


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text=TEXT
        )

        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG
        )

    """Поле title совпадает с ожидаемымы"""
    def test_object_name_is_title_field(self):
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    """Правильно отображается поле __str__"""
    def test_object_name_title_have_15_symbols(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
