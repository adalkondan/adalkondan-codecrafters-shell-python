import sys


def main():
    # Uncomment this block to pass the first stage
    #sys.stdout.write("$ ")
    def echo(message):
        print(" ".join(message))
    # Wait for user input
    while(True):
        
        sys.stdout.write("$ ")
        command=input().split()
        user_input = command[0]
        messag = command[1:]
        if command=="echo":
            echo(messag)
        if command=="exit 0":
            break
        print(f"{command}: command not found")
        


if __name__ == "__main__":
    main()
