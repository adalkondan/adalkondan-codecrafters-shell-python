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
        for word in messag:
          # cleaned_word = re.sub(r"'([^']*)'", r"\1", word)
          # cleaned_word = re.sub(r'"([^"]*)"', r"\1", cleaned_word)
          cleaned_word = re.sub(r"'([^']*)'", lambda m: m.group(1).replace("\\\\", "\\").replace("\\'", "'"), word)
          # cleaned_word = re.sub(r"'([^']*)'|\"([^']*)\"", lambda m: m.group(1) if m.group(1) is not None else m.group(2).replace("\\\\", "\\").replace('\\"', '"'), word)
          # Append the cleaned word  
          cleaned_msg.append(cleaned_word)
        
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
        for file_path in messag:
            for file_path in messag:
                processed_path = re.sub(r"'([^']*)'|\"([^\"]*)\"", lambda m: bytes((m.group(1)).replace("\\\\", "\\"), "utf-8").decode("unicode_escape", "ignore"), file_path)
                # Normalize the path for the operating system
                processed_path = os.path.normpath(processed_path)

                try:
                    with open(processed_path, "r") as file:
                        print(file.read())
                except FileNotFoundError:
                    print(f"cat: {processed_path}: No such file or directory")
                except IsADirectoryError:
                    print(f"cat: {processed_path}: Is a directory")
                except PermissionError:
                    print(f"cat: {processed_path}: Permission denied")

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        command = shlex.split(input())
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