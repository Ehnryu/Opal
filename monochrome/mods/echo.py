def echo(content):


    import subprocess
    te = content
    process = subprocess.run(f"""echo {te}""",text=True,capture_output=True)
    print(process.stdout)

export = {"name":"echo","run":echo,"args":["content"],"description":"Echo text from the shell"}
