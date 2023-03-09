from unittest import mock

import pytest
from django.core.management import CommandError, call_command


def test_generate_viewset_tests_command_with_no_options():
    with pytest.raises(CommandError) as e_info:
        call_command(
            "generate_viewset_tests",
        )

    assert "Error: the following arguments are required: -r/--router" in str(
        e_info.value
    )


@mock.patch(
    "drf_test_generator.management.commands."
    "generate_viewset_tests.UnitTestViewSetTestGenerator"
)
def test_generate_viewset_tests_command_invalid_router(viewset_test_generator):
    with pytest.raises(CommandError) as e_info:
        call_command(
            "generate_viewset_tests",
            "-r",
            "api.urls.router",
        )

    assert (
        "Could not import router from api.urls.router. "
        "Check that the dotted path is correct." in str(e_info.value)
    )


@mock.patch(
    "drf_test_generator.management.commands." "generate_viewset_tests.import_string"
)
@mock.patch(
    "drf_test_generator.management.commands."
    "generate_viewset_tests.UnitTestViewSetTestGenerator"
)
def test_generate_viewset_tests_command(viewset_test_generator, import_string):
    call_command(
        "generate_viewset_tests",
        "-r",
        "api.urls.router",
    )

    viewset_test_generator.assert_called_once_with(
        import_string.return_value,
        test_base_class="rest_framework.test.APITestCase",
        namespace=None,
        output_file=None,
        selected_viewsets=None,
    )


@mock.patch(
    "drf_test_generator.management.commands." "generate_viewset_tests.import_string"
)
@mock.patch(
    "drf_test_generator.management.commands."
    "generate_viewset_tests.UnitTestViewSetTestGenerator"
)
def test_generate_viewset_tests_command_with_all_options(
    viewset_test_generator, import_string
):
    call_command(
        "generate_viewset_tests",
        "-r",
        "api.urls.router",
        "--test-base-class",
        "tests.base.MyCustomTest",
        "--namespace",
        "api_v1",
        "--output-file",
        "tests.py",
        "--select-viewsets",
        "PostViewSet",
        "CommentViewSet",
    )

    viewset_test_generator.assert_called_once_with(
        import_string.return_value,
        test_base_class="tests.base.MyCustomTest",
        namespace="api_v1",
        output_file="tests.py",
        selected_viewsets=["PostViewSet", "CommentViewSet"],
    )


@mock.patch(
    "drf_test_generator.management.commands.generate_viewset_tests.import_string"
)
@mock.patch(
    "drf_test_generator.management.commands."
    "generate_viewset_tests.PyTestViewSetTestGenerator"
)
def test_generate_viewset_tests_command_pytest_with_all_options(
    pytest_viewset_test_generator, import_string
):
    call_command(
        "generate_viewset_tests",
        "-r",
        "api.urls.router",
        "--variant",
        "pytest",
        "--namespace",
        "api_v1",
        "--output-file",
        "tests.py",
        "--select-viewsets",
        "PostViewSet",
        "CommentViewSet",
        "--pytest-markers",
        "pytest.mark.urls",
        "--pytest-fixtures",
        "django_user_model",
    )

    pytest_viewset_test_generator.assert_called_once_with(
        import_string.return_value,
        namespace="api_v1",
        output_file="tests.py",
        selected_viewsets=["PostViewSet", "CommentViewSet"],
        pytest_markers=["pytest.mark.urls"],
        pytest_fixtures=["django_user_model"],
    )
