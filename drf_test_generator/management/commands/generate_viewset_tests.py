import argparse
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from drf_test_generator.viewset import ViewSetTestGenerator


class Command(BaseCommand):
    help = (
        "Generate tests for Django Rest Framework ViewSets"
        " based on the provided router's registered ViewSets. "
        "Example: `python manage.py generate_viewset_tests -r api.urls.router`"
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-r",
            "--router",
            nargs="?",
            type=str,
            help="Dotted path to the rest framework router. Example: api.urls.router",
            required=True,
        )
        parser.add_argument(
            "--test-base-class",
            nargs="?",
            type=str,
            help="Dotted path to the test base class. Example: tests.base.MyCustomTest",
            default="rest_framework.test.APITestCase",
        )
        parser.add_argument(
            "--namespace",
            nargs="?",
            type=str,
            help="Namespace to use for the URLs. Example: api_v1",
        )
        parser.add_argument(
            "--output-file",
            nargs="?",
            type=str,
            help="Path to the output file. Example: tests.py",
        )
        parser.add_argument(
            "--select-viewsets",
            nargs="*",
            type=str,
            help=(
                "List of ViewSets to generate tests for. "
                "Example: PostViewSet CommentViewSet"
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            router = import_string(options["router"])
        except ImportError:
            raise CommandError(
                f"Could not import router from {options['router']}. "
                "Check that the dotted path is correct."
            )

        ViewSetTestGenerator(
            router,
            test_base_class=options["test_base_class"],
            namespace=options["namespace"],
            output_file=options["output_file"],
            selected_viewsets=options["select_viewsets"],
        ).run()
