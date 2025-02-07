import sys
import os
import subprocess
import re
import shlex


def main():
    def find_executable(executable):
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            executable_path = os.path.join(path, executable)
            if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                return executable_path
        return None

    def echo(messag):
        cleaned_msg = []
        for m in messag:
            if m.startswith('"') and m.endswith('"'):
                # Handle backslashes within double quotes
                arg = arg.replace('\\', '').replace('\\\\', '\\').replace('\\$', '$').replace('\\n', '\n')
            cleaned_msg.append(m)

        print(" ".join(cleaned_msg))

    def type(messag):
        builtins = ['echo', 'exit', 'type','pwd']
        if messag[0] in builtins:
            print(f"{messag[0]} is a shell builtin")
            return
        executable_path = find_executable(messag[0])
        if executable_path:
            print(f"{messag[0]} is {executable_path}")
        else:
            print(f"{messag[0]}: not found")
    def cd(messag):
        if messag [0] == "~":
            os.chdir(os.path.expanduser("~"))
            return
        try:
            os.chdir(messag[0])
        except FileNotFoundError:
            print(f"cd: {messag[0]}: No such file or directory")
        # except NotADirectoryError:
        #     print(f"cd: {messag[0]}: Not a directory")
        # except PermissionError:
        #     print(f"cd: {messag[0]}: Permission denied")
    def cat(messag):
            for file_p in messag:  # messag contains the arguments from shlex.split()
                try:
                    # Check if the argument is quoted.  If so, remove the quotes.
                    if file_p.startswith("'") and file_p.endswith("'"):
                        process_p = file_p[1:-1]
                    elif file_p.startswith('"') and file_p.endswith('"'):
                        process_p = file_p[1:-1]
                    else:
                        process_p = file_p #If not quoted, pass it as is.

                    with open(process_p, "r") as file:
                        print(file.read(), end="")  # Keep the end=" " to avoid extra newlines

                except FileNotFoundError:
                    print(f"cat: {process_p}: No such file or directory", file=sys.stderr)
                except Exception as e: #Catch any other exception during file reading.
                    print(f"cat: Error reading {process_p}: {e}", file=sys.stderr)
    def handle_redirection(command_parts):
        out_redirection_index = -1
        err_redirection_index = -1
        for i, part in enumerate(command_parts):
            if part == ">" or part == "1>":
                out_redirection_index = i
            elif part == "2>":
                err_redirection_index = i

        command = command_parts[:]  # Create a copy to modify

        outfile = None
        if out_redirection_index != -1:
            if out_redirection_index + 1 < len(command_parts):
                outfile = command_parts[out_redirection_index + 1]
                del command[out_redirection_index:out_redirection_index + 2] # Remove redirection from command
            else:
                print("Error: No output file specified after '>' or '1>'.")
                return True #Redirection handled, but with error

        errfile = None
        if err_redirection_index != -1:
            if err_redirection_index + 1 < len(command_parts):
                errfile = command_parts[err_redirection_index + 1]
                del command[err_redirection_index:err_redirection_index + 2] # Remove redirection from command
            else:
                print("Error: No error file specified after '2>'.")
                return True #Redirection handled, but with error

        user_input = command[0]
        messag = command[1:]
        executable_path = find_executable(user_input)

        try:
            with (open(outfile, "w") if outfile else sys.stdout) as stdout_target, \
                 (open(errfile, "w") if errfile else sys.stderr) as stderr_target: #Use context manager for both files.

                if user_input == "echo":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    echo(messag)
                    sys.stdout = original_stdout
                elif user_input == "cat":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    original_stderr = sys.stderr
                    sys.stderr = stderr_target
                    cat(messag)
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                elif user_input == "pwd":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    print(os.getcwd())
                    sys.stdout = original_stdout
                elif user_input == "type":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    type(messag)
                    sys.stdout = original_stdout
                if executable_path:
                    try:
                        subprocess.run([user_input] + messag, executable=executable_path, stdout=stdout_target, stderr=stderr_target, text=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error executing {user_input}: {e}", file=sys.stderr) 
                        return True  # Print subprocess errors to stderr
                    except BrokenPipeError as e: #Handle broken pipe error separately
                        print(f"Error executing {user_input}: {e}", file=sys.stderr)
                        return True
                else:
                    print(f"{user_input}: command not found", file=sys.stderr) # Print command not found to stderr

        except FileNotFoundError as e:
            print(f"Error: Could not open file: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An error occurred during redirection: {e}", file=sys.stderr)

        return True

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input().strip()
        command = shlex.split(command, posix=True)
        if not command:
            continue
        if handle_redirection(command):  # Check and handle redirection
            continue 
        user_input = command[0]
        messag = command[1:]
        if user_input == "echo":
            echo(messag)
        elif user_input == "exit":
            break
        elif user_input == "type":
            type(messag)
        elif user_input == "cd":
            cd(messag)
        elif user_input == "pwd":
            print(os.getcwd())
        elif user_input == "cat":
            cat(messag)
        else:
            executable_path = find_executable(user_input)
            if executable_path:
                try:
                    subprocess.run([user_input] + messag,executable=executable_path, capture_output=False, text=True)
                except subprocess.CalledProcessError:
                    print(f"Error executing {user_input}")
            else:
                print(f"{user_input}: command not found")

if __name__ == "__main__":
    main()