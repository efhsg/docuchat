from streamlit.testing.v1 import AppTest
import logging

logger = logging.getLogger(__name__)


def test_home_page():
    at = AppTest.from_file("./src/Main.py").run()
    assert not at.exception
    assert at.title[0].value == "Welcome to DocuChat!"
