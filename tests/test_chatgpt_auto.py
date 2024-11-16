import unittest
from unittest.mock import Mock, patch
from selenium.webdriver.remote.webelement import WebElement
from chatgpt_auto.chatgpt_auto import ChatGPTAuto
from chatgpt_auto.custom_exceptions import ChatGPTAutoException, ChatGPTAutoTimeoutException

class TestChatGPTAuto(unittest.TestCase):
    @patch('chatgpt_auto.chatgpt_auto.WebDriverWait')
    @patch('chatgpt_auto.chatgpt_auto.Chrome')
    def setUp(self, mock_chrome, mock_wait):
        # Mock Chrome driver and its initialization
        self.mock_driver = Mock()
        mock_chrome.return_value = self.mock_driver
        
        # Mock WebDriverWait
        self.mock_wait = Mock()
        mock_wait.return_value = self.mock_wait
        
        # Initialize with mocked components
        with patch('builtins.open', unittest.mock.mock_open(read_data='{"chat_1": {"url": "test_url"}}')):
            with patch('json.load') as mock_json:
                mock_json.return_value = {"chat_1": {"url": "test_url"}}
                self.chat = ChatGPTAuto(cleanup=False)

    def test_send_empty_prompt(self):
        """Test that send() raises exception for empty prompts"""
        with self.assertRaises(ChatGPTAutoException):
            self.chat.send("")
        with self.assertRaises(ChatGPTAutoException):
            self.chat.send("   ")
        with self.assertRaises(ChatGPTAutoException):
            self.chat.send(None)

    @patch('chatgpt_auto.chatgpt_auto.EC')
    def test_send_valid_prompt(self, mock_ec):
        """Test sending a valid prompt"""
        # Mock the expected elements that would be found by WebDriverWait
        mock_textarea = Mock()
        mock_button = Mock()
        self.mock_wait.until.side_effect = [mock_textarea, mock_button]
        
        # Mock the response retrieval
        with patch.object(self.chat, '_get_chatgpt_response', return_value="Test response"):
            response = self.chat.send("Test prompt")
            
            # Verify interactions
            mock_textarea.send_keys.assert_called_once_with("Test prompt")
            mock_button.click.assert_called_once()
            self.assertEqual(response, "Test response")

    @patch('chatgpt_auto.chatgpt_auto.Paths.PY_SCRIPTS', '/mock/path/py_scripts')
    def test_handle_code_python(self):
        """Test handling Python code"""
        code_list = [("language-python", "# test.py\nprint('hello')")]
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            output, is_stderr = self.chat.handle_code(code_list)
            
            # Verify file was written to correct path
            mock_file.assert_called_once_with('/mock/path/py_scripts/test.py', 'w')
            mock_file().write.assert_called_once_with("# test.py\nprint('hello')")
            self.assertIn("'test.py' saved", output)
            self.assertFalse(is_stderr)

    def test_get_chatgpt_response_timeout(self):
        """Test timeout in get_chatgpt_response"""
        self.chat.instance_name = "chat_1"
        
        # Mock file operations
        mock_json = {"chat_1": {"last_response_data_testid": "conversation-turn-1"}}
        
        # Mock time to simulate timeout
        time_values = [0] + [31] * 10  # Return 31 multiple times to ensure we don't run out of values
        
        with patch('builtins.open', unittest.mock.mock_open(read_data=str(mock_json))):
            with patch('json.load', return_value=mock_json):
                with patch('time.time', side_effect=time_values):
                    with patch.object(self.chat.driver, 'execute_script', return_value=False):
                        with self.assertRaises(ChatGPTAutoException):
                            self.chat._get_chatgpt_response()

    def test_get_stable_output_success(self):
        """Test successful stable output retrieval"""
        # Mock time to avoid actual sleep
        with patch('time.sleep'):
            with patch('time.time', side_effect=[0] * 10):  # Avoid timeout
                # Set up the mock to return stable values
                self.mock_driver.execute_script.side_effect = [1] * 10  # More than enough stable outputs
                
                result = self.chat._get_stable_output_from_script(
                    "test_script",
                    interval=0.1,
                    timeout=1,
                    coincidences=5
                )
                
                self.assertEqual(result, 1)
                # We expect 6 calls because we need one extra call to check if we need to continue the loop
                self.assertEqual(self.mock_driver.execute_script.call_count, 6)

    def test_get_stable_output_timeout(self):
        """Test timeout in stable output retrieval"""
        # Mock time to simulate timeout
        with patch('time.sleep'):
            with patch('time.time', side_effect=[0, 0.3]):  # Simulate timeout after first check
                self.mock_driver.execute_script.side_effect = [1, 2, 3]  # Unstable outputs
                
                with self.assertRaises(ChatGPTAutoTimeoutException):
                    self.chat._get_stable_output_from_script(
                        "test_script",
                        interval=0.1,
                        timeout=0.2,
                        coincidences=5
                    )

if __name__ == '__main__':
    unittest.main()
