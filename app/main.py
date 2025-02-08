import sys
import os
import subprocess
import shlex
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
    BUILTINS = {"echo", "exit", "type", "pwd", "cd"}

    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def find_executable(self, executable: str) -> Optional[str]:
        """Find the full path of an executable in PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            executable_path = os.path.join(path, executable)
            if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                return executable_path
        return None

    def parse_command(self, command_line: str) -> ShellCommand:
        """Parse command line into command object with redirection handling."""
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
                stdout_redirect = ('w', parts[i + 1])  # write mode
                i += 2
            elif parts[i] in ['>>', '1>>'] and i + 1 < len(parts):
                stdout_redirect = ('a', parts[i + 1])  # append mode
                i += 2
            elif parts[i] == '2>' and i + 1 < len(parts):
                stderr_redirect = ('w', parts[i + 1])  # write mode
                i += 2
            elif parts[i] == '2>>' and i + 1 < len(parts):
                stderr_redirect = ('a', parts[i + 1])  # append mode
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
        """Set up file redirection for stdout and stderr."""
        stdout = self.original_stdout
        stderr = self.original_stderr

        if command.stdout_redirect:
            mode, filename = command.stdout_redirect
        try:
            stdout = open(filename, mode)
        except IOError as e:
            print(f"Error opening file for stdout redirection: {e}", file=sys.stderr)

        if command.stderr_redirect:
            mode, filename = command.stderr_redirect
        try:
            stderr = open(filename, mode)
        except IOError as e:
            print(f"Error opening file for stderr redirection: {e}", file=sys.stderr)

        return stdout, stderr

    def cleanup_redirection(self, stdout: TextIO, stderr: TextIO):
        """Clean up redirected file handles."""
        if stdout != self.original_stdout:
            stdout.close()
        if stderr != self.original_stderr:
            stderr.close()

    def execute_builtin(self, command: ShellCommand, stdout: TextIO, stderr: TextIO):
        """Execute built-in shell commands."""
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
                self.builtins = {"echo", "exit", "type", "pwd", "cd"} 
                
                if command.args[0] in self.builtins:

                    print(f"{command.args[0]} is a shell builtin", file=stdout)
                else:
                    executable_path = self.find_executable(command.args[0])
                    if executable_path:
                        print(f"{command.args[0]} is {executable_path}", file=stdout)
                    else:
                        print(f"{command.args[0]}: not found", file=stderr)
            elif command.command == "cat":
                if not command.args:
                    print("cat: missing file operand", file=stderr)
                    return
                for file_path in command.args:
                    try:
                        with open(file_path, 'r') as f:
                            print(f.read(), end='', file=stdout)
                    except FileNotFoundError:
                        print(f"cat: {file_path}: No such file or directory", file=stderr)
                    except PermissionError:
                        print(f"cat: {file_path}: Permission denied", file=stderr)
                    except Exception as e:
                        print(f"cat: {file_path}: Error: {e}", file=stderr)
        except Exception as e:
            print(f"Error executing builtin command: {e}", file=stderr)

    def execute_external(self, command: ShellCommand, stdout: TextIO, stderr: TextIO):
        """Execute external commands."""
        executable_path = self.find_executable(command.command)
        if not executable_path:
            print(f"{command.command}: command not found", file=stderr)
            return

        try:
            process = subprocess.run(
                [command.command] + command.args,
                stdout=stdout if stdout != self.original_stdout else subprocess.PIPE,
                stderr=stderr if stderr != self.original_stderr else subprocess.PIPE,
                text=True
            )
            
            if process.stdout and stdout == self.original_stdout:
                print(process.stdout, end='', file=stdout)
            if process.stderr and stderr == self.original_stderr:
                print(process.stderr, end='', file=stderr)
                
        except subprocess.CalledProcessError as e:
            print(f"Error executing {command.command}: {e}", file=stderr)
        except Exception as e:
            print(f"Error: {e}", file=stderr)

    def run(self):
        """Main shell loop."""
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
                    if command.command in self.BUILTINS:
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