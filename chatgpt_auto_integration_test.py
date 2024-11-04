import pytest
from chatgpt_auto import ChatGPTAuto


@pytest.fixture
def chatgpt_auto() -> ChatGPTAuto:
    return ChatGPTAuto(cleanup=False, cookies=None, initialize=True)

def test_response_should_not_be_none_or_empty(chatgpt_auto: ChatGPTAuto) -> None:
    response = chatgpt_auto.send("Hello, world!")
    assert response is not None
    assert response != ""

def test_response_should_be_string(chatgpt_auto: ChatGPTAuto) -> None:
    response = chatgpt_auto.send("Hello, world!")
    assert isinstance(response, str)

def test_responsewith_code_should_be_list_of_tuple(chatgpt_auto: ChatGPTAuto) -> None:
    response = chatgpt_auto.send("Write a bash command that shows the last pacman package I installed")
    assert isinstance(response, list)


    