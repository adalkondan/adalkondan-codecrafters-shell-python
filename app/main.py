import os
import sys
class command:
    def __init__(this, name, func, sh_type):
        this.name = name
        this.func = func
        this.sh_type = sh_type
    def execute(this, argc, argv):
        argv = pars_args(argv)
        this.func(*argv)
def pars_args(argv):
    s_quote = False
    d_quote = False
    quote_buffer = ""
    quote_index = 0
    args_buffer = []
    for i, arg in enumerate(argv):
        backslash = find(arg, "\\")
        if arg.startswith('"'):
            if arg.endswith('"'):
                quote_buffer = ""
                args_buffer.append(arg[1:-1])
                continue
            d_quote = True
            quote_buffer += arg[1:]
            quote_index = i
        elif d_quote == True:
            if arg.endswith('"'):
                d_quote = False
                quote_buffer += " " + arg[:-1]
                args_buffer.append(quote_buffer)
                quote_buffer = ""
            else:
                quote_buffer += " " + arg
        elif arg.startswith("'") and d_quote == False:
            if arg.endswith("'"):
                quote_buffer = ""
                args_buffer.append(arg[1:-1])
                continue
            s_quote = True
            quote_buffer += arg[1:]
            quote_index = i
        elif s_quote == True:
            if arg.endswith("'"):
                s_quote = False
                quote_buffer += " " + arg[:-1]
                args_buffer.append(quote_buffer)
                quote_buffer = ""
            else:
                quote_buffer += " " + arg
        else:
            if d_quote == False and s_quote == False:
                if len(backslash) != 0:
                    start_idx = 0
                    buffer = ""
                    add_end = True
                    for idx in backslash:
                        if len(arg) == (idx + 1):
                            buffer += arg[:-1] + " "
                            add_end = False
                        else:
                            buffer += arg[start_idx:idx]
                            start_idx = idx + 1
                    if add_end:
                        buffer += arg[start_idx:]
                    args_buffer.append(buffer)
                else:
                    args_buffer.append(arg)
            else:
                args_buffer.append(arg)
    if s_quote == True or d_quote == True:
        sys.stdout.write(f"Error parsing quote string")
    argv = args_buffer
    return argv
class shell_type:
    def __init__(this, name):
        this.name = name
BuiltIn = shell_type("shell builtin")
Types = {"builtin": BuiltIn}
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]
def search_path(name):
    PATH_ENV = os.environ.get("PATH")
    path_dirs = PATH_ENV.split(":")
    commands = []
    for path_dir in path_dirs:
        try:
            files = os.listdir(path_dir)
        except FileNotFoundError:
            pass  # this means there is no directory for that path entry
        files = [file for file in files if os.path.isfile(f"{path_dir}/{file}")]
        for file in files:
            if file == name:
                return f"{path_dir}/{file}"
    return None