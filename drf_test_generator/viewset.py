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


class ViewSetTestGenerator:
    """Builds basic tests for Django Rest Framework ViewSets."""

    def __init__(
        self,
        router: SimpleRouter,
        test_base_class: Optional[str] = None,
        namespace: Optional[str] = None,
        output_file: Optional[str] = None,
        selected_viewsets: Optional[List[str]] = None,
    ) -> None:
        self.router = router
        self.output_file = output_file
        self.namespace = namespace
        self.test_base_class = TestBaseClass(test_base_class)
        self.selected_viewsets = selected_viewsets

    @lru_cache(maxsize=7)  # noqa: B019
    def _build_assert_statement(self, http_method: str) -> str:
        return (
            "self.assertEqual(response.status_code, "
            f"{HTTP_METHOD_STATUS_CODE_MAP[http_method]})"
        )

    @lru_cache(maxsize=7)  # noqa: B019
    def _build_request(self, http_method: str) -> str:
        if http_method in ["post", "put", "patch"]:
            return f"self.client.{http_method}(url, data={{}})"
        return f"self.client.{http_method}(url)"

    def _build_test_method_name(
        self, basename: str, action_name: str, http_method: str
    ) -> str:
        return f"test_{basename}_{action_name}_{http_method}"

    def _build_reverse(
        self, url_name: str, lookup_dict: Optional[Dict[str, None]]
    ) -> str:
        nemspace = f"{self.namespace}:" if self.namespace else ""
        return (
            f"reverse('{nemspace}{url_name}', kwargs={lookup_dict})"
            if lookup_dict
            else f"reverse('{nemspace}{url_name}')"
        )

    def _build_test_class(self, viewset_name: str) -> str:
        return f"\n\nclass {viewset_name}Tests({self.test_base_class.class_name}):\n"

    def _get_import_string(self) -> str:
        return textwrap.dedent(
            f"""\
            from django.urls import reverse

            from rest_framework import status

            {self.test_base_class.get_import_statement()}
            """
        )

    def _generate_viewset_data_from_router(self) -> List[ViewSetData]:
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

    def _generate_tests_for_viewset(self, viewset_data: ViewSetData) -> str:
        tests = self._build_test_class(viewset_data.name)

        for url in viewset_data.urls:
            for http_method, action_name in url.method_map.items():
                test_method_name = self._build_test_method_name(
                    viewset_data.basename, action_name, http_method
                )

                tests += textwrap.indent(
                    text=textwrap.dedent(
                        f"""
                        def {test_method_name}(self):
                            url = {self._build_reverse(url.name, url.lookup_dict)}
                            response = {self._build_request(http_method)}
                            {self._build_assert_statement(http_method)}
                        """
                    ),
                    prefix="    ",
                )

        return tests

    def _generate_tests(self) -> List[str]:
        tests = []
        for viewset_data in self._generate_viewset_data_from_router():
            tests.append(self._generate_tests_for_viewset(viewset_data))
        return tests

    def _write_generated_tests_to_file(self, tests: List[str]) -> None:
        assert self.output_file

        with open(self.output_file, "a") as f:
            f.write(self._get_import_string())

            for test in tests:
                f.write(test)

    def _print_generated_tests(self, tests: List[str]) -> None:
        print(self._get_import_string(), end="")

        for test in tests:
            print(test, end="")

    def run(self) -> None:
        tests = self._generate_tests()

        if not tests:
            print("No tests generated.")
            return

        if self.output_file:
            self._write_generated_tests_to_file(tests)
        else:
            self._print_generated_tests(tests)
