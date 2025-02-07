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
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input().strip()
        command = shlex.split(command, posix=True)
        if not command:
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