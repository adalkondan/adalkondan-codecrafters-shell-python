import sys
import os
import subprocess
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
        try:
        # Use shlex to correctly parse the command, handling quotes and spaces
            parsed_command = shlex.split(command)

            # Remove single quotes from each item
            cleaned_command = [item.replace("'", "") for item in parsed_command]

            # Join the cleaned items back into a string, preserving spaces
            print(*cleaned_command)  # * unpacks the list for print to add spaces

        except ValueError as e:
            print(f"Error: {e}")
     
        

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

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = input().split()
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
            try:
                with open(messag[0], "r") as file:
                    print(file.read())
            except FileNotFoundError:
                print(f"cat: {messag[0]}: No such file or directory")
            except IsADirectoryError:
                print(f"cat: {messag[0]}: Is a directory")
            except PermissionError:
                print(f"cat: {messag[0]}: Permission denied")
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