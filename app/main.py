import sys
import os
import subprocess

def main():
    def find_executable(executable):
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            executable_path = os.path.join(path, executable)
            if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                return executable_path
        return None

    def echo(messag):
        return print(" ".join(messag))

    def type(messag):
        builtins = ['echo', 'exit', 'type']
        if messag[0] in builtins:
            print(f"{messag[0]} is a shell builtin")
            return
        executable_path = find_executable(messag[0])
        if executable_path:
            print(f"{messag[0]} is {executable_path}")
        else:
            print(f"{messag[0]}: not found")

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