# drf-test-generator

# Usage

```console
usage: manage.py generate_viewset_tests [-h] -r [ROUTER] [--test-base-class [TEST_BASE_CLASS]] [--namespace [NAMESPACE]] [--output-file [OUTPUT_FILE]] [--select-viewsets [SELECT_VIEWSETS ...]] [--version]
                                        [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

Generate tests for Django Rest Framework ViewSets based on the provided router's registered ViewSets.
Example: `python manage.py generate_viewset_tests -r api.urls.router`

options:
  -h, --help            show this help message and exit
  -r [ROUTER], --router [ROUTER]
                        Dotted path to the rest framework router. Example: api.urls.router
  --test-base-class [TEST_BASE_CLASS]
                        Dotted path to the test base class. Example: tests.base.MyCustomTest
  --namespace [NAMESPACE]
                        Namespace to use for the URLs. Example: api_v1
  --output-file [OUTPUT_FILE]
                        Path to the output file. Example: tests.py
  --select-viewsets [SELECT_VIEWSETS ...]
                        List of ViewSets to generate tests for. Example: PostViewSet CommentViewSet
```
