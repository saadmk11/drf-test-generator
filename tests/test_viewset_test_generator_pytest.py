import textwrap
from contextlib import redirect_stdout
from io import StringIO

from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_test_generator.viewset import PyTestViewSetTestGenerator


def test_viewset_test_generator_with_model_viewset():
    class PostViewSet(viewsets.ModelViewSet):
        ...

    router = routers.DefaultRouter()
    router.register("posts", PostViewSet, basename="post")

    expected_tests = textwrap.dedent(
        """\
        from django.urls import reverse

        from rest_framework import status

        import pytest

        # PostViewSet Tests


        @pytest.mark.django_db
        def test_post_list_get(client):
            url = reverse('post-list')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_create_post(client):
            url = reverse('post-list')
            response = client.post(url, data={})
            assert response.status_code == status.HTTP_201_CREATED


        @pytest.mark.django_db
        def test_post_retrieve_get(client):
            url = reverse('post-detail', kwargs={'pk': None})
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_update_put(client):
            url = reverse('post-detail', kwargs={'pk': None})
            response = client.put(url, data={})
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_partial_update_patch(client):
            url = reverse('post-detail', kwargs={'pk': None})
            response = client.patch(url, data={})
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_destroy_delete(client):
            url = reverse('post-detail', kwargs={'pk': None})
            response = client.delete(url)
            assert response.status_code == status.HTTP_204_NO_CONTENT
    """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(router).run()
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

        import pytest

        # PostViewSet Tests


        @pytest.mark.django_db
        def test_post_all_get(client):
            url = reverse('post-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_comment_get(client):
            url = reverse('post-comment', kwargs={'pk': None})
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_comment_options(client):
            url = reverse('post-comment', kwargs={'pk': None})
            response = client.options(url)
            assert response.status_code == status.HTTP_200_OK


        @pytest.mark.django_db
        def test_post_comment_put(client):
            url = reverse('post-comment', kwargs={'pk': None})
            response = client.put(url, data={})
            assert response.status_code == status.HTTP_200_OK
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(router).run()
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

        import pytest

        # FirstViewSet Tests


        @pytest.mark.django_db
        def test_first_all_get(client):
            url = reverse('first-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

        # SecondViewSet Tests


        @pytest.mark.django_db
        def test_second_all_get(client):
            url = reverse('second-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(router).run()
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

        import pytest

        # FirstViewSet Tests


        @pytest.mark.django_db
        def test_first_all_get(client):
            url = reverse('api_v1:first-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(router, namespace="api_v1").run()
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

        import pytest

        # FirstViewSet Tests


        @pytest.mark.django_db
        def test_first_all_get(client):
            url = reverse('first-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(router, selected_viewsets=["FirstViewSet"]).run()
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

        import pytest

        # FirstViewSet Tests


        @pytest.mark.django_db
        def test_first_all_get(client):
            url = reverse('first-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
        """
    )

    PyTestViewSetTestGenerator(router, output_file=file.strpath).run()
    assert file.read() == expected_tests


def test_viewset_test_generator_with_fixtures():
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

        import pytest

        # FirstViewSet Tests


        @pytest.mark.django_db
        def test_first_all_get(client, db, user):
            url = reverse('first-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(router, pytest_fixtures=["db", "user"]).run()
        assert str(generated_tests.getvalue()) == expected_tests


def test_viewset_test_generator_with_markers():
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

        import pytest

        # FirstViewSet Tests


        @pytest.mark.django_db
        @pytest.mark.urls('myapp.test_urls')
        @pytest.mark.ignore_template_errors
        def test_first_all_get(client):
            url = reverse('first-all')
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
        """
    )

    with redirect_stdout(StringIO()) as generated_tests:
        PyTestViewSetTestGenerator(
            router,
            pytest_markers=[
                "pytest.mark.urls('myapp.test_urls')",
                "pytest.mark.ignore_template_errors",
            ],
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
        PyTestViewSetTestGenerator(router).run()
        assert str(generated_tests.getvalue()) == expected_tests
