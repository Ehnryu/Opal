import os
for file in os.listdir("qi/"):
    try:
        x = open(f"qi/{file}")
        y = x.read()
        y = y.replace("qi","monochrome").replace("Qi","Monochrome")
        z = open(f"qi/{file}","w")
        z.write(y)
    except:
        pass
