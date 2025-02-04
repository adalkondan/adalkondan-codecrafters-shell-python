import sys


def main():
    # Uncomment this block to pass the first stage
    #sys.stdout.write("$ ")
    def echo(messag):
        return print(" ".join(messag))
    # Wait for user input\
    def type(messag):
        builtins = ['echo', 'exit', 'type']
        if messag[1:] in builtins:
            print(f"{messag[1:]} is a shell built-in")
        else:
            print(f"{messag[1:]}: command not found")
    while(True):
        
        sys.stdout.write("$ ")
        command=input().split()
        user_input = command[0]
        messag = command[1:]
        if command[0]=="echo":
            echo(messag)
        elif command[0]=="exit" and len(command)>1 and command[1:] == "0":
            break
        elif command[0]=="type":
            type(messag)
        else:
          print(f"{user_input}: command not found")
        


if __name__ == "__main__":
    main()
