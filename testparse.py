
class parse(Subparser):
    def parse(self,parser,tokens):
        from qi import ast
        tokens.consume_expected("X")
        v = tokens.consume_expected("STRING")
        print(v.value)
        tokens.consume_expected("NEWLINE")
        return ast.String(value=v.value)
