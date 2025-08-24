import os
import time
import tempfile
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import docker
import structlog
from config import settings

logger = structlog.get_logger()


@dataclass
class ExecutionResult:
    verdict: str
    time_ms: int
    memory_kb: int
    output: str
    error: str
    exit_code: int


class DockerExecutor:
    """Secure Docker-based code execution."""
    
    def __init__(self):
        self.client = docker.from_env()
        
    def execute(
        self,
        language: str,
        source_code: str,
        input_data: str,
        time_limit_ms: int,
        memory_limit_mb: int,
        output_limit_kb: int
    ) -> ExecutionResult:
        """Execute code in a secure Docker container."""
        
        # Create temporary directory for this execution
        with tempfile.TemporaryDirectory(dir=settings.JUDGE_WORK_DIR) as work_dir:
            try:
                # Write source code and input  
                self._prepare_source(work_dir, language, source_code)
                input_file = os.path.join(work_dir, "input.txt")
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(input_data)
                
                # Get language configuration
                lang_config = self._get_language_config(language)
                
                # Compile if needed
                if lang_config.get("compile_cmd"):
                    compile_result = self._run_container(
                        work_dir, 
                        lang_config["image"],
                        lang_config["compile_cmd"],
                        time_limit_ms=10000,  # 10s compile timeout
                        memory_limit_mb=memory_limit_mb * 2,  # More memory for compilation
                    )
                    
                    if compile_result.exit_code != 0:
                        return ExecutionResult(
                            verdict="CE",
                            time_ms=0,
                            memory_kb=0,
                            output="",
                            error=compile_result.error,
                            exit_code=compile_result.exit_code
                        )
                
                # Execute
                result = self._run_container(
                    work_dir,
                    lang_config["image"], 
                    lang_config["run_cmd"],
                    input_file="input.txt",
                    time_limit_ms=time_limit_ms,
                    memory_limit_mb=memory_limit_mb,
                    output_limit_kb=output_limit_kb
                )
                
                # Determine verdict
                if result.exit_code != 0:
                    verdict = "RE"
                elif result.time_ms > time_limit_ms:
                    verdict = "TLE" 
                elif result.memory_kb > memory_limit_mb * 1024:
                    verdict = "MLE"
                elif len(result.output.encode('utf-8')) > output_limit_kb * 1024:
                    verdict = "OLE"
                else:
                    verdict = "OK"  # Will be checked against expected output
                
                return ExecutionResult(
                    verdict=verdict,
                    time_ms=result.time_ms,
                    memory_kb=result.memory_kb,
                    output=result.output,
                    error=result.error,
                    exit_code=result.exit_code
                )
                
            except Exception as e:
                logger.error("Execution failed", error=str(e))
                return ExecutionResult(
                    verdict="RE",
                    time_ms=0,
                    memory_kb=0,
                    output="",
                    error=f"System error: {str(e)}",
                    exit_code=1
                )
    
    def _prepare_source(self, work_dir: str, language: str, source_code: str) -> str:
        """Prepare source code file."""
        extensions = {
            "python": "py",
            "cpp": "cpp", 
            "java": "java",
            "javascript": "js",
            "go": "go",
            "rust": "rs"
        }
        
        ext = extensions.get(language, "txt")
        source_file = os.path.join(work_dir, f"solution.{ext}")
        
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(source_code)
            
        return source_file
    
    def _get_language_config(self, language: str) -> Dict[str, Any]:
        """Get configuration for a programming language."""
        configs = {
            "python": {
                "image": settings.PYTHON_IMAGE,
                "compile_cmd": None,
                "run_cmd": ["python3", "solution.py"]
            },
            "cpp": {
                "image": settings.CPP_IMAGE,
                "compile_cmd": ["g++", "-std=c++17", "-O2", "-o", "solution", "solution.cpp"],
                "run_cmd": ["./solution"]
            },
            # TODO: Add more languages
        }
        
        return configs.get(language, configs["python"])
    
    def _run_container(
        self,
        work_dir: str,
        image: str,
        command: List[str],
        input_file: Optional[str] = None,
        time_limit_ms: int = 2000,
        memory_limit_mb: int = 256,
        output_limit_kb: int = 64
    ) -> ExecutionResult:
        """Run a command in a secure Docker container."""
        
        container_name = f"judge_{int(time.time() * 1000000)}"
        
        # Security configuration
        security_opt = []
        if settings.ENABLE_SECCOMP:
            security_opt.append("seccomp:unconfined")  # TODO: Use custom seccomp profile
        if settings.ENABLE_APPARMOR:
            security_opt.append("apparmor:unconfined")  # TODO: Use custom AppArmor profile
            
        container_config = {
            "image": image,
            "command": command,
            "working_dir": "/workspace",
            "volumes": {work_dir: {"bind": "/workspace", "mode": "rw"}},
            "mem_limit": f"{memory_limit_mb}m",
            "memswap_limit": f"{memory_limit_mb}m",  # Disable swap
            "cpu_quota": 100000,  # 100% of one CPU
            "cpu_period": 100000,
            "network_mode": "none" if not settings.ENABLE_NETWORK else "bridge",
            "cap_drop": ["ALL"],
            "security_opt": security_opt,
            "read_only": True,
            "tmpfs": {"/tmp": "size=100m,noexec"},
            "pids_limit": 100,
            "remove": True,
            "name": container_name,
            "user": "nobody:nogroup",
        }
        
        try:
            start_time = time.time()
            
            # Start container
            container = self.client.containers.run(
                detach=True,
                stdin_open=bool(input_file),
                **container_config
            )
            
            # Send input if provided
            if input_file:
                input_path = os.path.join(work_dir, input_file)
                if os.path.exists(input_path):
                    with open(input_path, 'rb') as f:
                        input_data = f.read()
                        container.stdin.write(input_data)
                        container.stdin.close()
            
            # Wait for completion with timeout
            timeout_sec = (time_limit_ms + 1000) / 1000  # Add 1s buffer
            try:
                result = container.wait(timeout=timeout_sec)
                exit_code = result["StatusCode"]
            except Exception:
                # Timeout or other error - kill container
                container.kill()
                exit_code = 124  # Timeout exit code
            
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)
            
            # Get output and stats
            try:
                output = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
                error = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
                
                # Truncate output if too long
                max_output_bytes = output_limit_kb * 1024
                if len(output.encode('utf-8')) > max_output_bytes:
                    output = output.encode('utf-8')[:max_output_bytes].decode('utf-8', errors='replace')
                    output += "\n[Output truncated]"
                    
            except Exception as e:
                output = ""
                error = f"Failed to get container output: {str(e)}"
            
            # Get memory usage (approximate)
            memory_kb = 0
            try:
                stats = container.stats(stream=False)
                memory_usage = stats["memory_stats"].get("usage", 0)
                memory_kb = int(memory_usage / 1024)
            except Exception:
                pass
            
            return ExecutionResult(
                verdict="OK" if exit_code == 0 else "RE",
                time_ms=execution_time_ms,
                memory_kb=memory_kb,
                output=output,
                error=error,
                exit_code=exit_code
            )
            
        except Exception as e:
            logger.error("Container execution failed", error=str(e))
            return ExecutionResult(
                verdict="RE",
                time_ms=0,
                memory_kb=0,
                output="",
                error=f"Container error: {str(e)}",
                exit_code=1
            )
            
        finally:
            # Cleanup container if it still exists
            try:
                container = self.client.containers.get(container_name)
                container.remove(force=True)
            except Exception:
                pass