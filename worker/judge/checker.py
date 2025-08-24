from typing import Tuple
from enum import Enum


class CheckerResult(Enum):
    AC = "AC"  # Accepted
    WA = "WA"  # Wrong Answer
    PE = "PE"  # Presentation Error


class Checker:
    """Output checking utilities."""
    
    @staticmethod
    def check_diff(expected: str, actual: str) -> Tuple[CheckerResult, str]:
        """Exact string comparison (ignoring trailing whitespace)."""
        expected_clean = expected.rstrip()
        actual_clean = actual.rstrip()
        
        if expected_clean == actual_clean:
            return CheckerResult.AC, "Accepted"
        else:
            return CheckerResult.WA, "Output doesn't match expected"
    
    @staticmethod
    def check_token(expected: str, actual: str) -> Tuple[CheckerResult, str]:
        """Token-based comparison (whitespace-insensitive)."""
        expected_tokens = expected.split()
        actual_tokens = actual.split()
        
        if expected_tokens == actual_tokens:
            return CheckerResult.AC, "Accepted"
        else:
            return CheckerResult.WA, "Tokens don't match expected"
    
    @staticmethod
    def check_float_eps(expected: str, actual: str, epsilon: float = 1e-6) -> Tuple[CheckerResult, str]:
        """Floating-point comparison with epsilon tolerance."""
        try:
            expected_lines = expected.strip().split('\n')
            actual_lines = actual.strip().split('\n')
            
            if len(expected_lines) != len(actual_lines):
                return CheckerResult.WA, "Different number of lines"
            
            for i, (exp_line, act_line) in enumerate(zip(expected_lines, actual_lines)):
                exp_tokens = exp_line.split()
                act_tokens = act_line.split()
                
                if len(exp_tokens) != len(act_tokens):
                    return CheckerResult.WA, f"Different number of tokens on line {i+1}"
                
                for j, (exp_token, act_token) in enumerate(zip(exp_tokens, act_tokens)):
                    try:
                        exp_val = float(exp_token)
                        act_val = float(act_token)
                        
                        if abs(exp_val - act_val) > epsilon:
                            return CheckerResult.WA, f"Value mismatch at line {i+1}, token {j+1}"
                    except ValueError:
                        # Non-numeric tokens must match exactly
                        if exp_token != act_token:
                            return CheckerResult.WA, f"Token mismatch at line {i+1}, token {j+1}"
            
            return CheckerResult.AC, "Accepted"
            
        except Exception as e:
            return CheckerResult.WA, f"Error checking floats: {str(e)}"
    
    @staticmethod
    def check_custom(expected: str, actual: str, checker_code: str) -> Tuple[CheckerResult, str]:
        """Custom checker (placeholder - requires sandboxed execution)."""
        # TODO: Implement custom checker execution in sandbox
        return CheckerResult.WA, "Custom checkers not yet implemented"
    
    @classmethod
    def check_output(
        self,
        checker_type: str,
        expected: str,
        actual: str,
        **kwargs
    ) -> Tuple[CheckerResult, str]:
        """Main checking function."""
        
        if checker_type == "diff":
            return self.check_diff(expected, actual)
        elif checker_type == "token":
            return self.check_token(expected, actual)
        elif checker_type == "float_eps":
            epsilon = kwargs.get("epsilon", 1e-6)
            return self.check_float_eps(expected, actual, epsilon)
        elif checker_type == "custom":
            checker_code = kwargs.get("checker_code", "")
            return self.check_custom(expected, actual, checker_code)
        else:
            # Default to diff
            return self.check_diff(expected, actual)