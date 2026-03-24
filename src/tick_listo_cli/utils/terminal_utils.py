"""Terminal utilities for platform-specific terminal clearing."""

import sys
import subprocess


def get_platform() -> str:
    """
    Get current platform identifier.

    Returns:
        Platform string: "windows", "linux", "macos", or "unknown"
    """
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "linux":
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "unknown"


class TerminalUtils:
    """
    Utility class for platform-specific terminal operations.

    Provides proper terminal clearing that resets the buffer,
    not just scrolling down.
    """

    def __init__(self):
        """Initialize terminal utils."""
        self.platform = get_platform()

    def clear_terminal(self) -> None:
        """
        Clear terminal screen and buffer completely.

        Uses platform-specific mechanisms to ensure proper buffer clearing,
        not just scrolling down. Prevents scroll-back to previous commands.

        Raises:
            RuntimeError: If terminal clearing fails or platform is unsupported
        """
        try:
            if self.platform == "windows":
                # Windows: Use cls command
                subprocess.run("cls", shell=True, check=True)

            elif self.platform in ["linux", "macos"]:
                # Linux/macOS: Use ANSI escape codes + clear command
                # \033[2J - Clear entire screen
                # \033[3J - Clear scrollback buffer
                # \033[H - Move cursor to home position
                print("\033[2J\033[3J\033[H", end="")
                sys.stdout.flush()

                # Also run clear command for complete buffer reset
                subprocess.run("clear", shell=True, check=True)

            else:
                raise RuntimeError(f"Unsupported platform: {self.platform}")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clear terminal: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to clear terminal: {str(e)}")
