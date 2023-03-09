import textwrap
from contextlib import redirect_stdout
from io import StringIO

from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_test_generator.viewset import UnitTestViewSetTestGenerator


def test_viewset_test_generator_with_model_viewset():
    class PostViewSet(viewsets.ModelViewSet):
        ...

    router = routers.DefaultRouter()
    router.register("posts", PostViewSet, basename="post")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from rest_framework.test import APITestCase


        class PostViewSetTests(APITestCase):

            def test_post_list_get(self):
                url = reverse('post-list')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_create_post(self):
                url = reverse('post-list')
                response = self.client.post(url, data={})
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            def test_post_retrieve_get(self):
                url = reverse('post-detail', kwargs={'pk': None})
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_update_put(self):
                url = reverse('post-detail', kwargs={'pk': None})
                response = self.client.put(url, data={})
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_partial_update_patch(self):
                url = reverse('post-detail', kwargs={'pk': None})
                response = self.client.patch(url, data={})
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_destroy_delete(self):
                url = reverse('post-detail', kwargs={'pk': None})
                response = self.client.delete(url)
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router).run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_generic_viewset():
    class PostViewSet(viewsets.GenericViewSet):
        @action(detail=True, methods=["get", "options", "put"], url_path="comment")
        def comment(self, request):
            return Response()

        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("posts", PostViewSet, basename="post")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from rest_framework.test import APITestCase


        class PostViewSetTests(APITestCase):

            def test_post_all_get(self):
                url = reverse('post-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_comment_get(self):
                url = reverse('post-comment', kwargs={'pk': None})
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_comment_options(self):
                url = reverse('post-comment', kwargs={'pk': None})
                response = self.client.options(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            def test_post_comment_put(self):
                url = reverse('post-comment', kwargs={'pk': None})
                response = self.client.put(url, data={})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
    """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router).run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_multiple_generic_viewset():
    class FirstViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    class SecondViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")
    router.register("second", SecondViewSet, basename="second")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from rest_framework.test import APITestCase


        class FirstViewSetTests(APITestCase):

            def test_first_all_get(self):
                url = reverse('first-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)


        class SecondViewSetTests(APITestCase):

            def test_second_all_get(self):
                url = reverse('second-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router).run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_app_namespace():
    class FirstViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from rest_framework.test import APITestCase


        class FirstViewSetTests(APITestCase):

            def test_first_all_get(self):
                url = reverse('api_v1:first-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router, namespace="api_v1").run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_selected_viewsets():
    class FirstViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    class SecondViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")
    router.register("second", SecondViewSet, basename="second")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from rest_framework.test import APITestCase


        class FirstViewSetTests(APITestCase):

            def test_first_all_get(self):
                url = reverse('first-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router, selected_viewsets=["FirstViewSet"]).run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_output_file(tmpdir):
    class FirstViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")

    output_file_name = "output.py"
    file = tmpdir.join(output_file_name)

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from rest_framework.test import APITestCase


        class FirstViewSetTests(APITestCase):

            def test_first_all_get(self):
                url = reverse('first-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
    )

    UnitTestViewSetTestGenerator(router, output_file=file.strpath).run()
    assert file.read() == expected_tests


def test_viewset_test_generator_with_test_base_class():
    class FirstViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        import CustomAPITestCase


        class FirstViewSetTests(CustomAPITestCase):

            def test_first_all_get(self):
                url = reverse('first-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router, test_base_class="CustomAPITestCase").run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_test_base_class_from_import():
    class FirstViewSet(viewsets.GenericViewSet):
        @action(detail=False, methods=["get"])
        def all(self, request):
            return Response()

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        from tests.base import CustomAPITestCase


        class FirstViewSetTests(CustomAPITestCase):

            def test_first_all_get(self):
                url = reverse('first-all')
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(
            router, test_base_class="tests.base.CustomAPITestCase"
        ).run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_empty_viewset():
    class FirstViewSet(viewsets.GenericViewSet):
        ...

    router = routers.DefaultRouter()
    router.register("first", FirstViewSet, basename="first")

    expected_tests = textwrap.dedent(
        """\
        No tests generated.
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        UnitTestViewSetTestGenerator(router).run()
        assert str(generated_tests.getvalue()) == expected_tests
