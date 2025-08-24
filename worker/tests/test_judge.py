import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from judge.executor import DockerExecutor
from judge.checker import Checker, CheckerResult


class TestDockerExecutor:
    
    @pytest.fixture
    def executor(self):
        return DockerExecutor()
    
    def test_prepare_source(self, executor):
        """Test source code preparation."""
        with tempfile.TemporaryDirectory() as work_dir:
            source_code = "print('Hello, World!')"
            source_file = executor._prepare_source(work_dir, "python", source_code)
            
            assert source_file.endswith("solution.py")
            assert os.path.exists(source_file)
            
            with open(source_file, 'r') as f:
                assert f.read() == source_code
    
    def test_get_language_config(self, executor):
        """Test language configuration retrieval."""
        python_config = executor._get_language_config("python")
        assert python_config["image"] == "python:3.12-slim"
        assert python_config["compile_cmd"] is None
        assert python_config["run_cmd"] == ["python3", "solution.py"]
        
        cpp_config = executor._get_language_config("cpp")
        assert cpp_config["image"] == "gcc:13"
        assert cpp_config["compile_cmd"] is not None
        assert "g++" in cpp_config["compile_cmd"]
    
    @patch('docker.from_env')
    def test_execute_python_success(self, mock_docker, executor):
        """Test successful Python code execution."""
        # Mock Docker client and container
        mock_client = Mock()
        mock_container = Mock()
        
        mock_docker.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        
        # Mock container behavior
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.side_effect = [b"Hello, World!", b""]
        mock_container.stats.return_value = {
            "memory_stats": {"usage": 1024000}  # 1MB
        }
        
        executor.client = mock_client
        
        result = executor.execute(
            language="python",
            source_code="print('Hello, World!')",
            input_data="",
            time_limit_ms=2000,
            memory_limit_mb=256,
            output_limit_kb=64
        )
        
        assert result.verdict == "OK"
        assert result.output == "Hello, World!"
        assert result.exit_code == 0
        assert result.memory_kb == 1000
    
    @patch('docker.from_env')
    def test_execute_timeout(self, mock_docker, executor):
        """Test execution timeout handling."""
        mock_client = Mock()
        mock_container = Mock()
        
        mock_docker.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        
        # Mock timeout scenario
        mock_container.wait.side_effect = Exception("Timeout")
        mock_container.logs.side_effect = [b"", b""]
        mock_container.kill = Mock()
        
        executor.client = mock_client
        
        result = executor.execute(
            language="python",
            source_code="import time; time.sleep(10)",
            input_data="",
            time_limit_ms=1000,
            memory_limit_mb=256,
            output_limit_kb=64
        )
        
        assert result.verdict == "RE"  # Runtime error due to timeout
        mock_container.kill.assert_called_once()


class TestChecker:
    
    def test_check_diff_exact_match(self):
        """Test exact diff checking with matching output."""
        expected = "42\n"
        actual = "42\n"
        
        result, message = Checker.check_diff(expected, actual)
        assert result == CheckerResult.AC
        assert message == "Accepted"
    
    def test_check_diff_trailing_whitespace(self):
        """Test diff checking ignores trailing whitespace."""
        expected = "42"
        actual = "42   \n  "
        
        result, message = Checker.check_diff(expected, actual)
        assert result == CheckerResult.AC
        assert message == "Accepted"
    
    def test_check_diff_mismatch(self):
        """Test diff checking with non-matching output."""
        expected = "42"
        actual = "43"
        
        result, message = Checker.check_diff(expected, actual)
        assert result == CheckerResult.WA
        assert "doesn't match" in message
    
    def test_check_token_whitespace_insensitive(self):
        """Test token checking is whitespace insensitive."""
        expected = "42  43\n44"
        actual = "42\n43 44"
        
        result, message = Checker.check_token(expected, actual)
        assert result == CheckerResult.AC
        assert message == "Accepted"
    
    def test_check_token_different_tokens(self):
        """Test token checking with different tokens."""
        expected = "42 43 44"
        actual = "42 43 45"
        
        result, message = Checker.check_token(expected, actual)
        assert result == CheckerResult.WA
        assert "don't match" in message
    
    def test_check_float_eps_within_tolerance(self):
        """Test float checking within epsilon tolerance."""
        expected = "3.14159"
        actual = "3.14160"
        
        result, message = Checker.check_float_eps(expected, actual, epsilon=1e-4)
        assert result == CheckerResult.AC
        assert message == "Accepted"
    
    def test_check_float_eps_outside_tolerance(self):
        """Test float checking outside epsilon tolerance."""
        expected = "3.14159"
        actual = "3.15000"
        
        result, message = Checker.check_float_eps(expected, actual, epsilon=1e-4)
        assert result == CheckerResult.WA
        assert "mismatch" in message
    
    def test_check_float_eps_mixed_content(self):
        """Test float checking with mixed numeric and text content."""
        expected = "Result: 3.14159 meters"
        actual = "Result: 3.14160 meters"
        
        result, message = Checker.check_float_eps(expected, actual, epsilon=1e-4)
        assert result == CheckerResult.AC
        assert message == "Accepted"
    
    def test_check_output_dispatch(self):
        """Test the main check_output function dispatches correctly."""
        expected = "42"
        actual = "42"
        
        # Test diff checker
        result, message = Checker.check_output("diff", expected, actual)
        assert result == CheckerResult.AC
        
        # Test token checker  
        result, message = Checker.check_output("token", expected, actual)
        assert result == CheckerResult.AC
        
        # Test float checker
        result, message = Checker.check_output("float_eps", expected, actual)
        assert result == CheckerResult.AC
        
        # Test unknown checker defaults to diff
        result, message = Checker.check_output("unknown", expected, actual)
        assert result == CheckerResult.AC