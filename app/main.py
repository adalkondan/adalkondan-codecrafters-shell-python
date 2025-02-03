import sys


def main():
    # Uncomment this block to pass the first stage
    #sys.stdout.write("$ ")
    def echo(message):
        return print(" ".join(message))
    # Wait for user input
    while(True):
        
        sys.stdout.write("$ ")
        command=input().split()
        user_input = command[0]
        messag = command[1:]
        if command[0]=="echo":
            echo(messag)
        elif command[0]=="exit" and len(command)>1 and command[1:] == "0":
            break
        else:
          print(f"{user_input}: command not found")
        


if __name__ == "__main__":
    main()
