"""
End-to-end UI tests for app.py using Streamlit's headless AppTest harness.

model.generate_metaphor / model.generate_image are patched before each run so
these tests never hit the network or need a real HF_API_KEY.
"""
import os
import sys
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def _ss_get(at, key, default=None):
    # Streamlit's AppTest SafeSessionState wrapper doesn't expose .get(), only
    # dict-style access that raises KeyError when the key isn't set yet.
    try:
        return at.session_state[key]
    except KeyError:
        return default


def test_empty_topic_shows_error_and_does_not_call_backend():
    at = AppTest.from_file(APP_PATH)
    at.run()

    with patch("model.generate_metaphor") as mock_metaphor:
        at.button[0].click().run()

    mock_metaphor.assert_not_called()
    assert any("Please enter a topic" in e.value for e in at.error)


def test_happy_path_shows_explanation_and_image_and_download_button():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.text_input[0].set_value("Recursion")

    fake_image = Image.new("RGB", (8, 8), color="red")
    with patch("model.generate_metaphor", return_value="Recursion is like Russian nesting dolls."), \
         patch("model.generate_image", return_value=(fake_image, None)):
        at.button[0].click().run()

    assert _ss_get(at, "explanation") == "Recursion is like Russian nesting dolls."
    assert _ss_get(at, "image") is fake_image
    assert _ss_get(at, "image_error") is None
    assert len(at.image) == 1
    assert len(at.download_button) == 1


def test_metaphor_failure_shows_error_and_never_calls_image_generation():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.text_input[0].set_value("Recursion")

    with patch("model.generate_metaphor", return_value=None) as mock_metaphor, \
         patch("model.generate_image") as mock_image:
        at.button[0].click().run()

    mock_metaphor.assert_called_once()
    mock_image.assert_not_called()  # regression guard: no image call on a failed metaphor
    assert any("Couldn't generate a metaphor" in e.value for e in at.error)
    assert _ss_get(at, "image") is None


def test_image_failure_still_shows_explanation_with_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.text_input[0].set_value("Recursion")

    with patch("model.generate_metaphor", return_value="A valid metaphor."), \
         patch("model.generate_image", return_value=(None, "Could not generate an image right now. Your metaphor is still shown below.")):
        at.button[0].click().run()

    assert _ss_get(at, "explanation") == "A valid metaphor."
    assert _ss_get(at, "image") is None
    assert len(at.warning) == 1
    assert len(at.download_button) == 0  # no image => no download button


def test_rate_limit_blocks_rapid_second_click():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.text_input[0].set_value("Recursion")

    fake_image = Image.new("RGB", (8, 8), color="blue")
    with patch("model.generate_metaphor", return_value="First metaphor.") as mock_metaphor, \
         patch("model.generate_image", return_value=(fake_image, None)):
        at.button[0].click().run()  # first click: allowed
        at.button[0].click().run()  # immediate second click: should be rate-limited

    assert mock_metaphor.call_count == 1
    assert any("wait" in w.value.lower() for w in at.warning)
