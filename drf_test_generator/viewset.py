import abc
import dataclasses
import re
import textwrap
from functools import lru_cache
from typing import Dict, List, Optional

from rest_framework.routers import SimpleRouter
from rest_framework.viewsets import ViewSetMixin

from .constants import HTTP_METHOD_STATUS_CODE_MAP


@dataclasses.dataclass(frozen=True)
class ViewSetURLData:
    """Dataclass to hold information about a viewset URL."""

    name: str
    lookup_dict: Dict[str, None] = dataclasses.field(default_factory=dict)
    method_map: Dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ViewSetData:
    """Dataclass to hold information about a viewset."""

    name: str
    basename: str
    urls: List[ViewSetURLData] = dataclasses.field(default_factory=list)

    def __init__(
        self, router: SimpleRouter, prefix: str, viewset: ViewSetMixin, basename: str
    ) -> None:
        self.name = viewset.__name__
        self.basename = basename
        self.urls = []

        for route in router.get_routes(viewset):
            mapping = router.get_method_map(viewset, route.mapping)

            if not mapping:
                continue

            regex = route.url.format(
                prefix=prefix,
                lookup=router.get_lookup_regex(viewset),
                trailing_slash=router.trailing_slash,
            )

            self.urls.append(
                ViewSetURLData(
                    name=route.name.format(basename=basename),
                    lookup_dict=dict.fromkeys(re.compile(regex).groupindex.keys()),
                    method_map=mapping,
                )
            )


@dataclasses.dataclass
class TestBaseClass:
    """Dataclass to hold information about the test base class."""

    class_name: str
    from_import: Optional[str] = None

    def __init__(self, test_base_class: Optional[str] = None) -> None:
        if test_base_class:
            parts = test_base_class.rsplit(".", 1)

            if len(parts) == 2:
                self.from_import, self.class_name = parts
            else:
                self.from_import = None
                self.class_name = test_base_class
        else:
            self.from_import = "rest_framework.test"
            self.class_name = "APITestCase"

    def get_import_statement(self) -> str:
        if self.from_import:
            return f"from {self.from_import} import {self.class_name}"
        return f"import {self.class_name}"


class ViewSetTestGeneratoBaser(abc.ABC):
    """Builds basic tests for Django Rest Framework ViewSets."""

    def __init__(
        self,
        router: SimpleRouter,
        namespace: Optional[str] = None,
        output_file: Optional[str] = None,
        selected_viewsets: Optional[List[str]] = None,
    ) -> None:
        self.router = router
        self.output_file = output_file
        self.namespace = namespace
        self.selected_viewsets = selected_viewsets

    @abc.abstractmethod
    def build_assert_statement(self, http_method: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def build_test_method_args(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def build_request(self, http_method: str) -> str:
        raise NotImplementedError

    def build_test_method_name(
        self, basename: str, action_name: str, http_method: str
    ) -> str:
        return f"test_{basename}_{action_name}_{http_method}"

    def build_reverse(
        self, url_name: str, lookup_dict: Optional[Dict[str, None]]
    ) -> str:
        nemspace = f"{self.namespace}:" if self.namespace else ""
        return (
            f"reverse('{nemspace}{url_name}', kwargs={lookup_dict})"
            if lookup_dict
            else f"reverse('{nemspace}{url_name}')"
        )

    def get_import_string(self) -> str:
        return textwrap.dedent(
            """\
            from django.urls import reverse

            from rest_framework import status
            """
        )

    def generate_viewset_data_from_router(self) -> List[ViewSetData]:
        data = []

        for prefix, viewset, basename in self.router.registry:
            if (
                self.selected_viewsets
                and viewset.__name__ not in self.selected_viewsets
            ):
                continue

            viewset_data = ViewSetData(self.router, prefix, viewset, basename)

            if viewset_data.urls:
                data.append(viewset_data)

        return data

    def build_test_method(
        self, url: ViewSetURLData, basename: str, http_method: str, action_name: str
    ) -> str:
        method_name = self.build_test_method_name(basename, action_name, http_method)
        return textwrap.dedent(
            f"""\
            def {method_name}({self.build_test_method_args()}):
                url = {self.build_reverse(url.name, url.lookup_dict)}
                response = {self.build_request(http_method)}
                {self.build_assert_statement(http_method)}
            """
        )

    def generate_tests_for_viewset(self, viewset_data: ViewSetData) -> str:
        tests = ""

        for url in viewset_data.urls:
            for http_method, action_name in url.method_map.items():
                test_method = self.build_test_method(
                    url, viewset_data.basename, http_method, action_name
                )
                tests += f"\n{test_method}"

        return tests

    def generate_tests(self) -> List[str]:
        tests = []
        for viewset_data in self.generate_viewset_data_from_router():
            tests.append(self.generate_tests_for_viewset(viewset_data))
        return tests

    def write_generated_tests_to_file(self, tests: List[str]) -> None:
        assert self.output_file

        with open(self.output_file, "a") as f:
            f.write(self.get_import_string())

            for test in tests:
                f.write(test)

    def print_generated_tests(self, tests: List[str]) -> None:
        print(self.get_import_string(), end="")

        for test in tests:
            print(test, end="")

    def run(self) -> None:
        tests = self.generate_tests()

        if not tests:
            print("No tests generated.")
            return

        if self.output_file:
            self.write_generated_tests_to_file(tests)
        else:
            self.print_generated_tests(tests)


class UnitTestViewSetTestGenerator(ViewSetTestGeneratoBaser):
    """Builds basic tests for Django Rest Framework ViewSets."""

    def __init__(
        self,
        router: SimpleRouter,
        test_base_class: Optional[str] = None,
        namespace: Optional[str] = None,
        output_file: Optional[str] = None,
        selected_viewsets: Optional[List[str]] = None,
    ) -> None:
        super().__init__(router, namespace, output_file, selected_viewsets)
        self.test_base_class = TestBaseClass(test_base_class)

    @lru_cache(maxsize=7)  # noqa: B019
    def build_assert_statement(self, http_method: str) -> str:
        return (
            "self.assertEqual(response.status_code, "
            f"{HTTP_METHOD_STATUS_CODE_MAP[http_method]})"
        )

    @lru_cache(maxsize=7)  # noqa: B019
    def build_request(self, http_method: str) -> str:
        if http_method in ["post", "put", "patch"]:
            return f"self.client.{http_method}(url, data={{}})"
        return f"self.client.{http_method}(url)"

    def build_test_method_args(self) -> str:
        return "self"

    def build_test_class(self, viewset_name: str) -> str:
        return f"\n\nclass {viewset_name}Tests({self.test_base_class.class_name}):\n"

    def get_import_string(self) -> str:
        return (
            f"{super().get_import_string()}\n"
            f"{self.test_base_class.get_import_statement()}\n"
        )

    def generate_tests_for_viewset(self, viewset_data: ViewSetData) -> str:
        tests = self.build_test_class(viewset_data.name)

        tests += textwrap.indent(
            text=super().generate_tests_for_viewset(viewset_data),
            prefix="    ",
        )
        return tests


class PyTestViewSetTestGenerator(ViewSetTestGeneratoBaser):
    """Builds basic tests for Django Rest Framework ViewSets."""

    def __init__(
        self,
        router: SimpleRouter,
        namespace: Optional[str] = None,
        output_file: Optional[str] = None,
        selected_viewsets: Optional[List[str]] = None,
        pytest_markers: Optional[List[str]] = None,
        pytest_fixtures: Optional[List[str]] = None,
    ) -> None:
        super().__init__(router, namespace, output_file, selected_viewsets)
        self.pytest_markers = pytest_markers or []
        self.pytest_fixtures = pytest_fixtures or []

    @lru_cache(maxsize=7)  # noqa: B019
    def build_assert_statement(self, http_method: str) -> str:
        return (
            "assert response.status_code == "
            f"{HTTP_METHOD_STATUS_CODE_MAP[http_method]}"
        )

    @lru_cache(maxsize=7)  # noqa: B019
    def build_request(self, http_method: str) -> str:
        if http_method in ["post", "put", "patch"]:
            return f"client.{http_method}(url, data={{}})"
        return f"client.{http_method}(url)"

    def build_test_method_args(self) -> str:
        args = ["client"]

        for arg in self.pytest_fixtures:
            args.append(arg)

        return ", ".join(args)

    def build_test_markers(self) -> str:
        markers = ["@pytest.mark.django_db"]

        for marker in self.pytest_markers:
            markers.append(f"@{marker}")

        return "\n".join(markers)

    def get_import_string(self) -> str:
        return f"{super().get_import_string()}\n" f"import pytest\n"

    def build_test_method(
        self, url: ViewSetURLData, basename: str, http_method: str, action_name: str
    ) -> str:
        return (
            f"\n{self.build_test_markers()}\n"
            f"{super().build_test_method(url, basename, http_method, action_name)}"
        )

    def generate_tests_for_viewset(self, viewset_data: ViewSetData) -> str:
        tests = f"\n# {viewset_data.name} Tests\n"
        tests += super().generate_tests_for_viewset(viewset_data)
        return tests
