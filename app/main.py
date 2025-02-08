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
    # def cd(messag):
    #     if messag [0] == "~":
    #         os.chdir(os.path.expanduser("~"))
    #         return
    #     try:
    #         os.chdir(messag[0])
    #     except FileNotFoundError:
    #         print(f"cd: {messag[0]}: No such file or directory")
    #     # except NotADirectoryError:
    #     #     print(f"cd: {messag[0]}: Not a directory")
    #     # except PermissionError:
    #     #     print(f"cd: {messag[0]}: Permission denied")
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
                    print(f"cat: {process_p}: No such file or directory", file=sys.stderr)
                except Exception as e: #Catch any other exception during file reading.
                    print(f"cat: Error reading {process_p}: {e}", file=sys.stderr)

    def normalise_args(user_input) -> list[str]:  #Enhanced argument parser
        res = []
        arg = ""
        i = 0
        while i < len(user_input):
            if user_input[i] == "'":
                i += 1
                start = i
                while i < len(user_input) and user_input[i] != "'":
                    i += 1
                arg += user_input[start:i]
                i += 1
            elif user_input[i] == '"':
                i += 1
                while i < len(user_input):
                    if user_input[i] == "\\":
                        if user_input[i + 1] in ["\\", "$", '"', "\n"]:
                            arg += user_input[i + 1]
                            i += 2
                        else:
                            arg += user_input[i]
                            i += 1
                    elif user_input[i] == '"':
                        break
                    else:
                        arg += user_input[i]
                        i += 1
                i += 1
            elif user_input[i] == " ":
                if arg:
                    res.append(arg)
                arg = ""
                i += 1
            elif user_input[i] == "\\":
                i += 1
            else:
                while i < len(user_input) and user_input[i] != " ":
                    if user_input[i] == "\\":
                        arg += user_input[i + 1]
                        i += 2
                    else:
                        arg += user_input[i]
                        i += 1
            
        if arg:
            res.append(arg)
        return res

    def cd_cmd(args, cur_dir) -> tuple[str, str]: #Snippet 1's enhanced cd
        path = args[0]
        new_dir = cur_dir
        if path.startswith("/"):
            new_dir = path
        else:
            for p in filter(None, path.split("/")):
                if p == "..":
                    new_dir = new_dir.rsplit("/", 1)[0]
                elif p == "~":
                    new_dir = os.environ["HOME"]
                elif p != ".":
                    new_dir += f"/{p}"
        if not os.path.exists(new_dir):
            return (cur_dir, f"cd: {path}: No such file or directory")
        else:
            return (new_dir, "")

    # def handle_redirection(command_parts):
    #     out_redirection_index = -1
    #     err_redirection_index = -1
    #     for i, part in enumerate(command_parts):
    #         if part == ">" or part == "1>":
    #             out_redirection_index = i
    #         elif part == "2>":
    #             err_redirection_index = i

    #     command = command_parts[:]  # Create a copy to modify

    #     outfile = None
    #     if out_redirection_index != -1:
    #         if out_redirection_index + 1 < len(command_parts):
    #             outfile = command_parts[out_redirection_index + 1]
    #             del command[out_redirection_index:out_redirection_index + 2] # Remove redirection from command
    #         else:
    #             print("Error: No output file specified after '>' or '1>'.")
    #             return True #Redirection handled, but with error

    #     errfile = None
    #     if err_redirection_index != -1:
    #         if err_redirection_index + 1 < len(command_parts):
    #             errfile = command_parts[err_redirection_index + 1]
    #             del command[err_redirection_index:err_redirection_index + 2] # Remove redirection from command
    #         else:
    #             print("Error: No error file specified after '2>'.")
    #             return True #Redirection handled, but with error

    #     user_input = command[0]
    #     messag = command[1:]
    #     executable_path = find_executable(user_input)

        try:
            with (open(outfile, "w") if outfile else sys.stdout) as stdout_target, \
                 (open(errfile, "w") if errfile else sys.stderr) as stderr_target: #Use context manager for both files.

                if user_input == "echo":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    echo(messag)
                    sys.stdout = original_stdout
                elif user_input == "cat":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    original_stderr = sys.stderr
                    sys.stderr = stderr_target
                    cat(messag)
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                elif user_input == "pwd":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    print(os.getcwd())
                    sys.stdout = original_stdout
                elif user_input == "type":
                    original_stdout = sys.stdout
                    sys.stdout = stdout_target
                    type(messag)
                    sys.stdout = original_stdout
                if executable_path:
                    try:
                        subprocess.run([user_input] + messag, executable=executable_path, stdout=stdout_target, stderr=stderr_target, text=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error executing {user_input}: {e}", file=sys.stderr) 
                        return True  # Print subprocess errors to stderr
                    except BrokenPipeError as e: #Handle broken pipe error separately
                        print(f"Error executing {user_input}: {e}", file=sys.stderr)
                        return True
                else:
                    print(f"{user_input}: command not found", file=sys.stderr) # Print command not found to stderr

        except FileNotFoundError as e:
            print(f"Error: Could not open file: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An error occurred during redirection: {e}", file=sys.stderr)

        return True

    cur_dir = os.getcwd() #Keep track of current directory
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        user_input = input()
        args = normalise_args(user_input) #Use the enhanced argument parser
        if not args: #Handle empty input
            continue
        cmd, args = args[0], args[1:]
        out, err = "", ""

        if cmd == "exit":
            if args and args[0] == "0": #Handle exit code
                break
            elif not args:
                break
        elif cmd == "echo":
            out = " ".join(args)
        elif cmd == "type":
            if args:
              out, err = type(args) #type function is already defined
        elif cmd == "pwd":
            out = cur_dir
        elif cmd == "cd":
            cur_dir, err = cd_cmd(args, cur_dir) #Use the enhanced cd
        elif cmd == "cat":
            out, err = cat(args)
        else:
            executable_path = find_executable(cmd)
            if executable_path:
                try:
                    res = subprocess.run(
                        args=([cmd] + args),
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    out = res.stdout.rstrip()
                    err = res.stderr.rstrip()
                except subprocess.CalledProcessError as e:
                    err = f"Error executing {cmd}: {e}"
            else:
                err = f"{user_input}: command not found"

        if err:
            print(err, file=sys.stderr)
        if out:
            print(out, file=sys.stdout)


if __name__ == "__main__":
    main()