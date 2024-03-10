import os
import pytest
from streamlit.testing.v1 import AppTest


def find_streamlit_pages(root_dir):
    for root, dirs, files in os.walk(root_dir):
        if "utils" in root.split(os.sep):
            continue
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                yield os.path.join(root, file)


def test_home_page(app_test):
    at = app_test("src/Main.py")
    assert not at.exception
    assert at.title[0].value == "Welcome to DocuChat!"


@pytest.mark.parametrize("page_path", list(find_streamlit_pages("src/pages")))
def test_streamlit_page(app_test, page_path):
    at = app_test(page_path, timeout=10)
    assert not at.exception


@pytest.fixture
def app_test():
    """A pytest fixture to create and run an AppTest instance with a configurable timeout."""

    def _app_test(page_path, timeout=10):
        """Create and run an AppTest instance for a given page_path with specified timeout."""
        at = AppTest.from_file(page_path).run(timeout=timeout)
        return at

    return _app_test
