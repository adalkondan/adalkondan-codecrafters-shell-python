import sys


def main():
    # Uncomment this block to pass the first stage
    #sys.stdout.write("$ ")

    # Wait for user input
    while(True):
        
        sys.stdout.write("$ ")
        command=input()
        if command=="exit 0":
            break
        print(f"{command}: command not found")
        


if __name__ == "__main__":
    main()
