# Terminal Utils Contract

**Service**: TerminalUtils
**Purpose**: Provide platform-specific terminal clearing functionality
**Module**: `src/ticklisto/utils/terminal_utils.py`

## Interface

### clear_terminal

Clear the terminal screen and buffer using platform-specific mechanisms.

#### Signature

```python
def clear_terminal() -> None:
    """
    Clear terminal screen and buffer completely.

    Uses platform-specific mechanisms to ensure proper buffer clearing,
    not just scrolling down. Prevents scroll-back to previous commands.

    Raises:
        RuntimeError: If terminal clearing fails
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| None | - | - | Detects platform automatically |

#### Output

| Type | Description |
|------|-------------|
| None | No return value (raises exception on error) |

**Behavior**:
- Detects operating system automatically (Windows, Linux, macOS)
- Uses platform-specific clearing mechanism:
  - **Windows**: `cls` command via subprocess
  - **Linux/macOS**: ANSI escape codes + `clear` command
- Clears terminal buffer completely (not just visible screen)
- Prevents scroll-back to previous commands
- Resets cursor to top-left position

#### Platform-Specific Implementation

**Windows**:
```python
import subprocess
import sys

if sys.platform == "win32":
    subprocess.run("cls", shell=True, check=True)
```

**Linux/macOS**:
```python
import subprocess
import sys

if sys.platform in ["linux", "darwin"]:
    # ANSI escape codes to clear screen and buffer
    print("\033[2J\033[3J\033[H", end="")
    sys.stdout.flush()
    # Also run clear command for complete buffer reset
    subprocess.run("clear", shell=True, check=True)
```

#### Examples

```python
# Example 1: Clear terminal (auto-detects platform)
clear_terminal()
# Terminal screen and buffer completely cleared

# Example 2: Use in CLI command
def handle_clear_command():
    clear_terminal()
    print("Terminal cleared successfully")
```

---

### get_platform

Get the current platform identifier.

#### Signature

```python
def get_platform() -> str:
    """
    Get current platform identifier.

    Returns:
        Platform string: "windows", "linux", or "macos"
    """
```

#### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| None | - | - | Detects platform automatically |

#### Output

| Type | Description |
|------|-------------|
| str | Platform identifier: "windows", "linux", or "macos" |

**Behavior**:
- Uses `sys.platform` to detect OS
- Returns normalized platform name
- Useful for testing and debugging

#### Examples

```python
# Example: Check platform
platform = get_platform()
# Returns: "windows" on Windows, "linux" on Linux, "macos" on macOS
```

---

## Platform Detection Logic

```python
import sys

def get_platform() -> str:
    """Detect and return normalized platform name."""
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "linux":
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "unknown"
```

## ANSI Escape Codes Reference

| Code | Description |
|------|-------------|
| `\033[2J` | Clear entire screen |
| `\033[3J` | Clear scrollback buffer |
| `\033[H` | Move cursor to home position (0,0) |

## Error Handling

| Error | Condition | Response |
|-------|-----------|----------|
| RuntimeError | Subprocess command fails | Raise with error details |
| RuntimeError | Unknown platform | Raise with unsupported platform message |
| OSError | Terminal not available | Raise with terminal access error |

## Cross-Platform Compatibility

### Windows
- Uses `cls` command
- Clears console buffer
- Works in cmd.exe and PowerShell

### Linux
- Uses ANSI escape codes + `clear` command
- Clears screen and scrollback buffer
- Works in most terminal emulators (bash, zsh, etc.)

### macOS
- Uses ANSI escape codes + `clear` command
- Clears screen and scrollback buffer
- Works in Terminal.app and iTerm2

## Performance

- **Time Complexity**: O(1)
- **Target**: <50ms per clear operation

## Testing Requirements

**Unit Tests**:
1. Platform detection (Windows, Linux, macOS)
2. Clear terminal on Windows (mock subprocess)
3. Clear terminal on Linux (mock subprocess and ANSI codes)
4. Clear terminal on macOS (mock subprocess and ANSI codes)
5. Error handling for subprocess failures
6. Error handling for unknown platforms

**Integration Tests**:
1. Clear terminal in actual terminal environment
2. Verify buffer is cleared (no scroll-back)
3. Verify cursor position reset

**Manual Testing**:
1. Run clear command in Windows cmd.exe
2. Run clear command in Linux terminal
3. Run clear command in macOS Terminal.app
4. Verify no scroll-back to previous commands

---

## Usage in CLI

```python
# In commands.py
from ticklisto.utils.terminal_utils import clear_terminal

def handle_clear_command():
    """Handle the clear/clr command."""
    try:
        clear_terminal()
        console.print("[green]Terminal cleared successfully[/green]")
    except RuntimeError as e:
        console.print(f"[red]Error clearing terminal: {e}[/red]")
```

---

**Contract Version**: 1.0
**Date**: 2026-02-03
**Status**: Approved
