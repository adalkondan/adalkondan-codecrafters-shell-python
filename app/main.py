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
                    print(f"cat: {process_p}: No such file or directory")
                except Exception as e: #Catch any other exception during file reading.
                    print(f"cat: Error reading {process_p}: {e}")
    def handle_redirection(command_parts):
        redirection_index = -1
        for i, part in enumerate(command_parts):
            if part == ">" or part == "1>":
                redirection_index = i
                break

        if redirection_index != -1:
            if redirection_index + 1 < len(command_parts):
                output_file = command_parts[redirection_index + 1]
                try:
                    with open(output_file, "w") as outfile:
                        # Modify subprocess.run to use the file for stdout
                        command = command_parts[:redirection_index]  # Command before redirection
                        user_input = command[0]  # Extract command name
                        messag = command[1:]       # Extract arguments

                        # Redirect stdout for built-in and external commands
                        original_stdout = sys.stdout  # Save original stdout
                        sys.stdout = outfile           # Redirect stdout to file

                        if user_input == "echo":
                            echo(messag)
                        elif user_input == "cat":
                            cat(messag)
                        elif user_input == "pwd":
                            print(os.getcwd())
                        elif user_input == "type":
                            type(messag)
                        else:  # External command
                            executable_path = find_executable(user_input)
                            if executable_path:
                                try:
                                    subprocess.run([user_input] + messag, executable=executable_path, stdout=outfile, text=True, check=True)
                                except subprocess.CalledProcessError as e:
                                    print(f"Error executing {user_input}: {e}")
                            else:
                                print(f"{user_input}: command not found")

                        sys.stdout = original_stdout  # Restore stdout

                except FileNotFoundError:
                    print(f"Error: Could not open file '{output_file}' for writing.")
                except Exception as e:
                    print(f"An error occurred during redirection: {e}")
            else:
                print("Error: No output file specified after '>' or '1>'.")
            return True  # Redirection was handled
        return False  # No redirection found

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