import os
import subprocess
import pytest
from chatgpt_auto import ChatGPTAuto
import shutil


@pytest.fixture
def chatgpt_auto() -> ChatGPTAuto:
    return ChatGPTAuto(initialize=False)


def test_run_command_should_fail(chatgpt_auto: ChatGPTAuto) -> None:
    _, is_stderror = chatgpt_auto._run_command("not a command")
    assert is_stderror


def test_run_command_should_not_fail(chatgpt_auto: ChatGPTAuto) -> None:
    _, is_stderror = chatgpt_auto._run_command("ls")
    assert not is_stderror


URLS_TEST = "urls_test.json"
shutil.copy("urls.json", URLS_TEST)


def test_should_retrieve_urls(chatgpt_auto: ChatGPTAuto) -> None:
    urls = chatgpt_auto._get_instance_urls(json_path=URLS_TEST)
    assert urls is not None
    assert urls != {}


def test_should_retrieve_url(chatgpt_auto: ChatGPTAuto) -> None:
    url = chatgpt_auto._get_instance_url(instance_name="chat_1", json_path=URLS_TEST)
    assert url is not None
    assert url != ""


def test_should_update_url(chatgpt_auto: ChatGPTAuto) -> None:
    expected_new_url = "new url"
    chatgpt_auto._update_instance_url(
        instance_name="chat_1", new_url=expected_new_url, json_path=URLS_TEST
    )
    actual_new_url = chatgpt_auto._get_instance_url("chat_1", URLS_TEST)
    assert expected_new_url == actual_new_url


def test_should_execute_command_without_errors(chatgpt_auto: ChatGPTAuto) -> None:
    code = [("language-bash", "ls")]
    _, is_stderror = chatgpt_auto.handle_code(code)
    assert not is_stderror


def test_should_retrieve_valid_command_output(chatgpt_auto: ChatGPTAuto) -> None:
    command = [("language-bash", "whoami")]
    output, _ = chatgpt_auto.handle_code(command)

    process = subprocess.Popen(
        command[0][1],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        universal_newlines=True,
    )

    actual_output, _ = process.communicate()
    assert actual_output.strip() in output


def test_should_save_python_script(chatgpt_auto: ChatGPTAuto) -> None:
    script_name = "test.py"
    script = f"# {script_name}\nprint('JooJ')"
    code = [("language-python", script)]
    chatgpt_auto.handle_code(code)

    assert script_name in os.listdir("py_scripts")


def test_py_script_should_be_the_same_after_saving(chatgpt_auto: ChatGPTAuto) -> None:
    script_name = "test.py"
    script = f"# {script_name}\nprint('JooJ')"
    code = [("language-python", script)]
    chatgpt_auto.handle_code(code)

    with open(f"py_scripts/{script_name}", "r") as saved_script:
        saved_script_content = saved_script.read()

    assert saved_script_content == script
