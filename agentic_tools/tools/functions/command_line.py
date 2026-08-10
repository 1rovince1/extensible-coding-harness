import logging
import subprocess

from config.env_config import env_settings

logger = logging.getLogger(__name__)


ALLOWED_CMDS = env_settings.SHELL_COMMANDS_ALLOWED
SHELL_COMMAND_TIMEOUT = 30


async def execute_shell_command(command: str) -> str:
    """
    Execute a shell command and return its output
    """
    try:
        logger.info(f"Command request: {command}")

        if command.split()[0] not in ALLOWED_CMDS:
            return "Error: Command not allowed"

        result = subprocess.run(
            command,
            cwd=env_settings.AGENT_WORK_DIR,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            timeout=SHELL_COMMAND_TIMEOUT
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        return "\n\n".join(output) or "Command executed successfully"
        # return result.stdout.strip() if result.stdout else "Command executed successfully"

    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e}"
