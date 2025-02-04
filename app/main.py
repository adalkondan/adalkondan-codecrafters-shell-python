import sys
import os


def main():
    # Uncomment this block to pass the first stage
    #sys.stdout.write("$ ")
    def find_executable(executable):
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            executable_path = os.path.join(path, executable)
            if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
                return executable_path
        return None
    def echo(messag):
        return print(" ".join(messag))
    # Wait for user input\
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
        
    while(True):
        
        sys.stdout.write("$ ")
        command=input().split()
        user_input = command[0]
        messag = command[1:]
        if command[0]=="echo":
            echo(messag)
        elif user_input== "exit":
            break
        elif command[0]=="type":
            type(messag)
        else:
          print(f"{user_input}: command not found")
        


if __name__ == "__main__":
    main()
