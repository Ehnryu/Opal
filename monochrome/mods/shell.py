def execute(content):
    import subprocess
    te = content
    process = subprocess.run(te,text=True,capture_output=True)
    return {"args":process.args,"code":process.returncode,"content":process.stdout,"error":process.stderr}
def sh(content):
    try:
        import subprocess
        te = content
        process = subprocess.run(te,text=True,capture_output=True)
        return process.stdout
    except:
        print("SHELL ERROR.")
export = [{"name":"shell","run":execute,"args":["content"],"description":"Execute a shell command"},{"name":"sh","run":sh,"args":["content"],"description":"Execute a shell command & get output directly"}]
