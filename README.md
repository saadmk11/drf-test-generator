# drf-test-generator

This is a Django Package that generates basic tests for Django REST Framework.

# Features

- Generates tests for all `ViewSets` in a Django REST Framework `router`
- Generates tests for all custom `actions` in a `ViewSet`
- Generates tests for all `HTTP` methods in a `ViewSet`
- Supports test generation for both `pytest` and `unittest`

# Installation

```console
pip install drf-test-generator
```

# Setup

Add `drf_test_generator` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "drf_test_generator",
]
```

**Note:** This is required for the Django Management Command. You can remove it from `INSTALLED_APPS` once you have generated the tests.

# Generate Tests

## Django Management Command

You can generate tests using the Django Management Command:

```console
python manage.py generate_viewset_tests -r api.urls.router
```

**Note:** Currently this package only supports test generation for ViewSets that are registered in a router.

## Django Management Command Options

### `-r` or `--router` (REQUIRED)

The dotted path to the REST framework url router. This is the router that contains the ViewSets you want to generate tests for.

**Example:** `--router api.urls.router`

### `--test-base-class`

The dotted path to the test base class. This is the class that your tests will inherit from. If not provided, the tests will inherit from `rest_framework.test.APITestCase`.

**Example:** `--test-base-class tests.base.MyCustomTest`

### `--namespace`

The namespace to use for the URLs (e.g: `api_v1:posts-list` ). If not provided, no namespace will be used.

**Example:** `--namespace api_v1`

### `--output-file`

The path to the output file. If not provided, the tests will be printed to the console.

**Example:** `--output-file tests.py`

### `--select-viewsets`

A list of ViewSets to generate tests for. If not provided, tests will be generated for all ViewSets in the router.

**Example:** `--select-viewsets PostViewSet CommentViewSet`

### `--variant`

The test variant to generate. Options: `pytest`, `unittest`. If not provided, `unittest` will be used.

**Example:** `--variant pytest`

### `--pytest-markers`

A list of pytest markers to add to the generated tests. If not provided, only the `@pytest.mark.django_db` marker will be added.

**Example:** `--pytest-markers pytest.mark.ignore_template_errors pytest.mark.urls('myapp.test_urls')`

### `--pytest-fixtures`

A list of pytest fixtures to add to the generated tests. If not provided, only the `client` fixture will be added.

**Example:** `--pytest-fixtures django_user_model`

# Examples Usage

## For the following code

```python
# api/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PostViewSet(viewsets.ModelViewSet):
    # ...
    @action(detail=False, methods=["get", "post"], url_path="custom-action")
    def custom_action(self, request):
        return Response()

    @action(detail=True, methods=["get", "options", "put"], url_path="new-action")
    def custom_action2(self, request):
        return Response()


# api/urls.py
from rest_framework import routers

router = routers.DefaultRouter()

router.register("posts", PostViewSet, basename="post")
```

## For Unittest

**Run Command**

```console
python manage.py generate_viewset_tests -r api.urls.router
```

**Output**

```python
from django.urls import reverse

from rest_framework import status

from rest_framework.test import APITestCase


class PostViewSetTests(APITestCase):
    def test_post_list_get(self):
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_create_post(self):
        url = reverse("post-list")
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_custom_action_get(self):
        url = reverse("post-custom-action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_custom_action_post(self):
        url = reverse("post-custom-action")
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_retrieve_get(self):
        url = reverse("post-detail", kwargs={"pk": None})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_update_put(self):
        url = reverse("post-detail", kwargs={"pk": None})
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_partial_update_patch(self):
        url = reverse("post-detail", kwargs={"pk": None})
        response = self.client.patch(url, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_destroy_delete(self):
        url = reverse("post-detail", kwargs={"pk": None})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_custom_action2_get(self):
        url = reverse("post-custom-action2", kwargs={"pk": None})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_custom_action2_options(self):
        url = reverse("post-custom-action2", kwargs={"pk": None})
        response = self.client.options(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_custom_action2_put(self):
        url = reverse("post-custom-action2", kwargs={"pk": None})
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## For Pytest

**Run Command**

```console
python manage.py generate_viewset_tests -r api.urls.router --variant pytest
```

**Output**

```python
from django.urls import reverse

from rest_framework import status

import pytest

# PostViewSet Tests


@pytest.mark.django_db
def test_post_list_get(client):
    url = reverse("post-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_create_post(client):
    url = reverse("post-list")
    response = client.post(url, data={})
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_post_custom_action_get(client):
    url = reverse("post-custom-action")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_custom_action_post(client):
    url = reverse("post-custom-action")
    response = client.post(url, data={})
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_post_retrieve_get(client):
    url = reverse("post-detail", kwargs={"pk": None})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_update_put(client):
    url = reverse("post-detail", kwargs={"pk": None})
    response = client.put(url, data={})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_partial_update_patch(client):
    url = reverse("post-detail", kwargs={"pk": None})
    response = client.patch(url, data={})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_destroy_delete(client):
    url = reverse("post-detail", kwargs={"pk": None})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_post_custom_action2_get(client):
    url = reverse("post-custom-action2", kwargs={"pk": None})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_custom_action2_options(client):
    url = reverse("post-custom-action2", kwargs={"pk": None})
    response = client.options(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_post_custom_action2_put(client):
    url = reverse("post-custom-action2", kwargs={"pk": None})
    response = client.put(url, data={})
    assert response.status_code == status.HTTP_200_OK
```

# License

The code in this project is released under the [MIT License](LICENSE).
