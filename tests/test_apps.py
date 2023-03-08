from drf_test_generator.apps import DrfTestGeneratorConfig


def test_apps():
    assert DrfTestGeneratorConfig.name == "drf_test_generator"
