from streamlit.testing.v1 import AppTest


def test_05_Manage_domains():
    at = AppTest.from_file("src/pages/05_Manage_domains.py").run()
    assert not at.exception
