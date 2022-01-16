import main as basic
import sys
l = ""
try:
    l = sys.argv[1]
except IndexError:
    l = ""
if l.endswith("opl"):
  with open(sys.argv[1],"r") as x:
      content = x.read()

      text = content
      if text.strip() == "":
          exit()
      result, error = basic.run('<stdin>', text)
  
      if error:
        print(error.as_string())
      elif result:
        if len(result.elements) == 1:
          print(repr(result.elements[0]))
      else:
        print(repr(result))
else:
    while True:
      text = input('basic > ')
      if text.strip() == "": continue
      result, error = basic.run('<stdin>', text)
    
      if error:
        print(error.as_string())
      elif result:
        if len(result.elements) == 1:
          print(repr(result.elements[0]))
        else:
          print(repr(result))