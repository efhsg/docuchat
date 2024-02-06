from streamlit.testing.v1 import AppTest
import logging

logger = logging.getLogger(__name__)


def test_home_page():
    at = AppTest.from_file("./src/pages/10_Extract_text.py").run()
    assert not at.exception
