from streamlit.testing.v1 import AppTest


def test_10_Extract_text():
    at = AppTest.from_file("src/pages/10_Extract_text.py").run()
    assert not at.exception
