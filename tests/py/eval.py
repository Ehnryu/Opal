from opal.interpreter import evaluate
x = evaluate("func hi():\n    print('hi')\nhi")
print(x)