"""
Unit tests for model.py's retry/error-handling behaviour.

These mock the Hugging Face client entirely -- no network calls, no API key
needed -- so they run anywhere, including CI.
"""
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import model  # noqa: E402


def _fake_chat_response(content):
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    return response


def test_generate_metaphor_returns_text_on_success():
    # huggingface_hub's chat.completions.create is a bound method on an
    # immutable client object (patch.object can't setattr on it directly),
    # so swap the whole `model.client` for a MagicMock for the duration of
    # the test instead of patching one attribute of the real client.
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _fake_chat_response("A metaphor.")
    with patch("model.client", fake_client):
        result = model.generate_metaphor("Recursion")
    assert result == "A metaphor."


def test_generate_metaphor_retries_exactly_n_times_then_returns_none():
    fake_client = MagicMock()
    fake_client.chat.completions.create.side_effect = RuntimeError("simulated API failure")

    with patch("model.client", fake_client), \
         patch("model.time.sleep", return_value=None):  # skip real backoff delay in tests
        result = model.generate_metaphor("Recursion", retries=3, backoff_seconds=0)

    assert result is None
    assert fake_client.chat.completions.create.call_count == 3


def test_generate_metaphor_empty_response_is_treated_as_failure():
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = _fake_chat_response("")

    with patch("model.client", fake_client), \
         patch("model.time.sleep", return_value=None):
        result = model.generate_metaphor("Recursion", retries=1, backoff_seconds=0)
    assert result is None


def test_generate_image_returns_none_prompt_message_when_prompt_missing():
    image, error = model.generate_image(None)
    assert image is None
    assert error == "No metaphor text available to illustrate."


def test_generate_image_success_returns_image_and_no_error():
    fake_image = MagicMock(name="PIL.Image")
    with patch.object(model.client, "text_to_image", return_value=fake_image):
        image, error = model.generate_image("a metaphor about recursion")
    assert image is fake_image
    assert error is None


def test_generate_image_failure_message_does_not_leak_exception_details():
    # Regression test: the error message shown to the user must never
    # contain the raw exception text (which can include API/model internals)
    secret_detail = "super-secret-internal-detail-12345"
    with patch.object(model.client, "text_to_image", side_effect=RuntimeError(secret_detail)):
        image, error = model.generate_image("a metaphor about recursion")

    assert image is None
    assert error is not None
    assert secret_detail not in error
    assert error == "Could not generate an image right now. Your metaphor is still shown below."
