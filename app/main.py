import sys
import os
import subprocess
import shlex
import readline
from typing import Optional, Tuple, List, TextIO

class ShellCommand:
    def __init__(self, command: str, args: List[str], 
                 stdout_redirect: Optional[Tuple[str, str]] = None,
                 stderr_redirect: Optional[Tuple[str, str]] = None):
        self.command = command
        self.args = args
        self.stdout_redirect = stdout_redirect
        self.stderr_redirect = stderr_redirect

class Shell:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.builtins = {"echo", "exit", "type", "pwd", "cd"}
        self.setup_completion()
        self._cache_executables()

    def _cache_executables(self):
        """Cache all executable files in PATH"""
        self.executables = set()
        for path in os.environ.get("PATH", "").split(os.pathsep):
            try:
                path = path.strip('"')
                if os.path.isdir(path):
                    for file in os.listdir(path):
                        full_path = os.path.join(path, file)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            self.executables.add(file)
            except Exception:
                continue

    def setup_completion(self):
        """Set up command completion using readline"""
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)
        readline.set_completer_delims(' \t\n;')

    def complete(self, text: str, state: int) -> Optional[str]:
        """Completion function for readline"""
        buffer = readline.get_line_buffer()
        cmd_start = buffer[:readline.get_begidx()]
        
        # If we're at the start of the line or completing the command
        if not cmd_start.strip():
            # First try builtins
            builtin_matches = [cmd + ' ' for cmd in self.builtins if cmd.startswith(text)]
            # Then try executables
            executable_matches = [cmd + ' ' for cmd in self.executables if cmd.startswith(text)]
            # Combine matches
            matches = builtin_matches + executable_matches
            
            try:
                return matches[state] + ' '
            except IndexError:
                return None
                
        return None

    def find_executable(self, executable: str) -> Optional[str]:
        """Find the full path of an executable in PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            executable_path = os.path.join(path, executable)
            if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                return executable_path
        return None

    def parse_command(self, command_line: str) -> ShellCommand:
        try:
            parts = shlex.split(command_line, posix=True)
        except ValueError as e:
            print(f"Error parsing command: {e}", file=sys.stderr)
            return ShellCommand("", [])

        if not parts:
            return ShellCommand("", [])

        stdout_redirect = None
        stderr_redirect = None
        command_parts = []

        i = 0
        while i < len(parts):
            if parts[i] in ['>', '1>'] and i + 1 < len(parts):
                stdout_redirect = ('w', parts[i + 1])
                i += 2
            elif parts[i] in ['>>', '1>>'] and i + 1 < len(parts):
                stdout_redirect = ('a', parts[i + 1])
                i += 2
            elif parts[i] == '2>' and i + 1 < len(parts):
                stderr_redirect = ('w', parts[i + 1])
                i += 2
            elif parts[i] == '2>>' and i + 1 < len(parts):
                stderr_redirect = ('a', parts[i + 1])
                i += 2
            else:
                command_parts.append(parts[i])
                i += 1

        if not command_parts:
            return ShellCommand("", [])

        return ShellCommand(
            command_parts[0],
            command_parts[1:],
            stdout_redirect,
            stderr_redirect
        )

    def setup_redirection(self, command: ShellCommand) -> Tuple[TextIO, TextIO]:
        stdout = self.original_stdout
        stderr = self.original_stderr

        try:
            if command.stdout_redirect:
                mode, filepath = command.stdout_redirect
                stdout = open(filepath, mode)

            if command.stderr_redirect:
                mode, filepath = command.stderr_redirect
                stderr = open(filepath, mode)
        except Exception as e:
            print(f"Redirection error: {e}", file=self.original_stderr)

        return stdout, stderr

    def cleanup_redirection(self, stdout: TextIO, stderr: TextIO):
        if stdout != self.original_stdout:
            stdout.close()
        if stderr != self.original_stderr:
            stderr.close()

    def execute_external(self, command: ShellCommand, stdout: TextIO, stderr: TextIO):
        try:
            executable_path = self.find_executable(command.command)
            if not executable_path:
                executable_path = command.command  # Try using the command as-is
            executable_name = os.path.basename(executable_path)    
            process = subprocess.run(
                [executable_path] + command.args,
                stdout=stdout if stdout != self.original_stdout else subprocess.PIPE,
                stderr=stderr if stderr != self.original_stderr else subprocess.PIPE,
                text=True
            )
            
            if process.stdout and stdout == self.original_stdout:
                print(process.stdout.replace(executable_path, executable_name), end='', file=stdout)
            if process.stderr and stderr == self.original_stderr:
                print(process.stderr.replace(executable_path, executable_name), end='', file=stderr)
                
        except FileNotFoundError:
            print(f"{command.command}: command not found", file=stderr)
        except Exception as e:
            print(f"Error: {e}", file=stderr)

    def execute_builtin(self, command: ShellCommand, stdout: TextIO, stderr: TextIO):
        try:
            if command.command == "echo":
                print(" ".join(command.args), file=stdout)
            elif command.command == "pwd":
                print(os.getcwd(), file=stdout)
            elif command.command == "cd":
                if not command.args:
                    print("cd: missing directory", file=stderr)
                    return
                try:
                    if command.args[0] == "~":
                        os.chdir(os.path.expanduser("~"))
                    else:
                        os.chdir(command.args[0])
                except FileNotFoundError:
                    print(f"cd: {command.args[0]}: No such file or directory", file=stderr)
                except NotADirectoryError:
                    print(f"cd: {command.args[0]}: Not a directory", file=stderr)
                except PermissionError:
                    print(f"cd: {command.args[0]}: Permission denied", file=stderr)
            elif command.command == "type":
                if not command.args:
                    print("type: missing argument", file=stderr)
                    return
                if command.args[0] in self.builtins:
                    print(f"{command.args[0]} is a shell builtin", file=stdout)
                else:
                    executable_path = self.find_executable(command.args[0])
                    if executable_path:
                        print(f"{command.args[0]} is {executable_path}", file=stdout)
                    else:
                        print(f"{command.args[0]}: not found", file=stderr)
        except Exception as e:
            print(f"Error executing builtin command: {e}", file=stderr)

    def run(self):
        while True:
            try:
                sys.stdout.write("$ ")
                sys.stdout.flush()
                command_line = input().strip()
                
                if not command_line:
                    continue

                command = self.parse_command(command_line)
                
                if command.command == "exit":
                    break

                stdout, stderr = self.setup_redirection(command)
                
                try:
                    if command.command in self.builtins:
                        self.execute_builtin(command, stdout, stderr)
                    else:
                        self.execute_external(command, stdout, stderr)
                finally:
                    self.cleanup_redirection(stdout, stderr)

            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n", end='')
                continue
            except Exception as e:
                print(f"Shell error: {e}", file=sys.stderr)

def main():
    shell = Shell()
    shell.run()

if __name__ == "__main__":
    main()