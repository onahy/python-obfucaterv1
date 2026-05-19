

"""
   _____ ________     __
  / ___// ____/\ \   / /
  \__ \/ /      \ \_/ / 
 ___/ / /___     \   /  
/____/\____/      \_/   

 @@@@@@   @@@@@@@@  @@@ @@@  
@@@@@@@   @@@@@@@@  @@@ @@@  
!@@       @@!       @@! !@@  
!@!       !@!       !@! @!!  
!!@@!!    @!!!:!     !@!@!   
 !!@!!!   !!!!!:      @!!!   
     !:!  !!:         !!:    
    !:!   :!:         :!:    
:::: ::    :: ::::     ::    
:: : :    : :: ::      :   

"""


import os
import ast
import sys
import zlib
import base64
import string
import random
import builtins
import argparse

class SzyOBFv2:
    def __init__(self, code: str, include_imports: bool=False, recursion: int=1) -> None:
        self._code = code
        self._imports = []
        self._aliases = {}
        self._valid_identifiers = [chr(x) for x in range(sys.maxunicode) if chr(x).isidentifier()]

        self.__include_imports = include_imports
        if recursion < 1:
            raise ValueError("Recursion length cannot be less than 1")
        else:
            self.__recursion = recursion
    
    def obfuscate(self) -> str:
        szy_banner = '''# Szy_Szy - obfucater
'''
        self._remove_comments_and_docstrings()
        self._save_imports()

        layers = [
            self._layer_1,
            self._layer_2,
            self._layer_3
        ] * self.__recursion
        random.shuffle(layers)

        if layers[-1] == self._layer_3:
            for index, layer in enumerate(layers):
                if layer != self._layer_3:
                    layers[index] = self._layer_3
                    layers[-1] = layer
                    break

        for layer in layers:
            layer()

        if self.__include_imports:
            self._prepend_imports()
            
        return szy_banner + self._code
    
    def _save_imports(self) -> None:
        def visit_node(node):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self._imports.append((None, name.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for name in node.names:
                    self._imports.append((module, name.name))

            for child_node in ast.iter_child_nodes(node):
                visit_node(child_node)

        tree = ast.parse(self._code)
        visit_node(tree)
        
        self._imports = list(set(self._imports))
        self._imports.sort(reverse=True, key=lambda x: len(x[1]) + len(x[0]) if x[0] is not None else 0)
    
    def _prepend_imports(self) -> None:
        for module, submodule in self._imports:
            if module is not None:
                statement = "from %s import %s\n" % (module, submodule)
            else:
                statement = "import %s\n" % submodule
            self._code = statement + self._code
    
    def _generate_random_name(self, value: str) -> str:
        if value in self._aliases.keys():
            return self._aliases.get(value)
        else:
            while(True):
                name = "".join(random.choices(self._valid_identifiers, k=random.randint(10, 25)))
                if not name in self._aliases.values():
                    self._aliases[value] = name
                    return name
                
    def _remove_comments_and_docstrings(self) -> None:
        tree = ast.parse(self._code)
        tree.body.insert(0, ast.Expr(
                    value=ast.Constant(":: You managed to break through SzyOBF v2; Give yourself a pat on your back! ::")
                ))
        for index, node in enumerate(tree.body[1:]):
            
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                tree.body[index] = ast.Pass()

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                for index, expr in enumerate(node.body):
                    if (isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Constant)):
                        node.body[index] = ast.Pass()
            
            elif isinstance(node, ast.ClassDef):
                for index, expr in enumerate(node.body):

                    if isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Constant):
                        node.body[index] = ast.Pass()


                    elif isinstance(expr, ast.FunctionDef) or isinstance(expr, ast.AsyncFunctionDef):
                        for index, node in enumerate(expr.body):
                            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                                expr.body[index] = ast.Pass()
        self._code = ast.unparse(tree)
                
    def _insert_dummy_comments(self) -> None:
        code = self._code.splitlines()
        for index in range(len(code) - 1, 0, -1):
            if random.randint(1, 10) > 3:
                spaces = 0
                comment = "#"
                for i in range(random.randint(7, 55)):
                    comment += " " + "".join(random.choices(self._valid_identifiers, k=random.randint(2, 10)))
                for i in code[index]:
                    if i != " ":
                        break
                    else:
                        spaces += 1
                code.insert(index, (" " * spaces) + comment)
        self._code = "\n".join(code)
    
    def _obfuscate_vars(self) -> None:
        class Transformer(ast.NodeTransformer):
            def __init__(self, outer: SzyOBFv2) -> None:
                self._outer = outer

            def rename(self, name: str) -> None:
                if not name in dir(builtins) and not name in [x[1] for x in self._outer._imports]:
                    return self._outer._generate_random_name(name)
                else:
                    return name
            
            def visit_Name(self, node: ast.Name) -> ast.Name:
                if node.id in dir(builtins) or node.id in [x[1] for x in self._outer._imports]:
                    node = ast.Call(
                            func=ast.Call(
                                    func=ast.Name(id="getattr", ctx=ast.Load()),
                                    args=[
                                        ast.Call(
                                            func=ast.Name(id="__import__", ctx=ast.Load()),
                                            args=[self.visit_Constant(ast.Constant(value="builtins"))],
                                            keywords=[]
                                        ),
                                        self.visit_Constant(ast.Constant(value="eval"))
                                    ],
                                    keywords=[]
                                ),
                            args=[
                                ast.Call(
                                    func=ast.Name(id="bytes", ctx=ast.Load()),
                                    args=[
                                        ast.Subscript(
                                            value = ast.List(
                                                        elts=[ast.Constant(value=x) for x in list(node.id.encode())][::-1],
                                                        ctx=ast.Load()
                                                    ),
                                            slice=ast.Slice(
                                                upper=None,
                                                lower=None,
                                                step=ast.Constant(value=-1)
                                            )
                                        )
                                    ],
                                    keywords=[]
                                )
                            ],
                            keywords=[]
                    )
                    return node
                else:
                    node.id = self.rename(node.id)
                    return self.generic_visit(node)
            
            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                node.name = self.rename(node.name)
                return self.generic_visit(node)
            
            def visit_arg(self, node: ast.arg) -> ast.arg:
                node.arg = self.rename(node.arg)
                return node
            
            def visit_Constant(self, node: ast.Constant) -> ast.Constant:
                if isinstance(node.value, int):
                    choice = random.randint(1, 2)
                    match choice:
                        case 1: # fn(x) = x*n - x*(n-1) ; Where n > 2^16
                            num = random.randint(2 ** 16, sys.maxsize)
                            left = node.value * num
                            right = node.value * (num - 1)
                            node = ast.BinOp(left=ast.Constant(value=left), 
                                            op=ast.Sub(),
                                            right=ast.Constant(value=right))
                        
                        case 2: # fn(x) = ((n*2) + (x*2*m)) // 2 - n - x*(m-1) ; Where n > 2^16, m ∈ [50, 500]
                            num = random.randint(2 ** 16, sys.maxsize)
                            times = random.randint(50, 500)
                            node = ast.BinOp(
                                left=ast.BinOp(
                                    left=ast.BinOp(
                                        left=ast.BinOp(
                                            left=ast.Constant(value=num*2),
                                            op=ast.Add(),
                                            right=ast.Constant(value=node.value*2*times)
                                        ),
                                        op=ast.FloorDiv(),
                                        right=ast.Constant(value=2)
                                    ),
                                    op=ast.Sub(),
                                    right=ast.Constant(value=num)
                                ),
                                op=ast.Sub(),
                                right=ast.Constant(node.value*(times-1))
                            )

                elif isinstance(node.value, str):
                    encoded = list(node.value.encode())[::-1]
                    node = ast.Call(func=ast.Attribute(value=ast.Call(func=ast.Name(id="bytes", ctx=ast.Load()),
                                                                      args=[ast.Subscript(value=ast.List(elts=[ast.Constant(value=x) for x in encoded],
                                                                                                        ctx=ast.Load()),
                                                                                          slice= ast.Slice(lower=None,
                                                                                                           upper=None,
                                                                                                           step=ast.Constant(value=-1)), 
                                                                                          ctx=ast.Load())],
                                                                      keywords=[]), 
                                    attr="decode", 
                                    ctx=ast.Load()), 
                                    args=[], 
                                    keywords=[])
                elif isinstance(node.value, bytes):
                    encoded = list(node.value)[::-1]
                    node = ast.Call(func=ast.Name(id="bytes", ctx=ast.Load()),
                                    args=[ast.Subscript(value=ast.List(elts=[ast.Constant(value=x) for x in encoded],
                                                                       ctx=ast.Load()),
                                                        slice= ast.Slice(lower=None,
                                                                         upper=None,
                                                                         step=ast.Constant(value=-1)), 
                                                        ctx=ast.Load())],
                                    keywords=[])
                return node
            
            def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
                node = ast.Call(
                    func=ast.Name(id="getattr", ctx=ast.Load()),
                    args=[node.value, ast.Constant(node.attr)],
                    keywords=[]
                )

                return self.generic_visit(node)
        
        tree = ast.parse(self._code)
        Transformer(self).visit(tree)
        self._code = ast.unparse(tree)
    
    def _layer_1(self) -> None:
        layer = """
fire = ""
water = ""
earth = ""
wind = ""

exec(__import__("zlib").decompress(__import__("base64").b64decode(fire + water + earth + wind)))
"""
        encoded = base64.b64encode(zlib.compress(self._code.encode())).decode()
        parts = []
        for index in range(0, len(encoded), int(len(encoded)/4)):
            parts.append(encoded[index : index + int(len(encoded)/4)])
        parts.reverse()

        tree = ast.parse(layer)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and parts:
                before = "".join(random.choices(string.ascii_letters, k= random.randint(5, 100)))
                after = "".join(random.choices(string.ascii_letters, k= random.randint(5, 100)))
                part = parts.pop()
                node.value = ast.Subscript(
                    value = ast.Constant(value=before + part + after),
                    slice=ast.Slice(
                        upper=ast.Constant(value=len(before) + len(part)),
                        lower=ast.Constant(value=len(before)),
                        step=None
                    ),
                    ctx=ast.Store()
                )
        self._code = ast.unparse(tree)
        self._obfuscate_vars()
        self._insert_dummy_comments()
    
    def _layer_2(self) -> None:
        layer = """
encrypted = []
for i in range(1, 100):
    if encrypted[in_loc] ^ i == encrypted[re_loc]:
        exec(__import__("zlib").decompress(bytes(map(lambda x: x^i, encrypted[0:in_loc] + encrypted[in_loc + 1: re_loc] + encrypted[re_loc + 1:]))))
        break
"""
        key = random.randint(1, 100)
        in_byte = random.randbytes(1)[0]
        re_byte = in_byte ^ key

        encrypted = list(map(lambda x: key ^ x, zlib.compress(self._code.encode())))

        in_loc = random.randint(0, int(len(encrypted)/2))
        re_loc = random.randint(in_loc, len(encrypted) - 1)
        encrypted.insert(in_loc, in_byte)
        encrypted.insert(re_loc, re_byte)
        layer = layer.replace("in_loc", str(in_loc)).replace("re_loc", str(re_loc)) 

        tree = ast.parse(layer)
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                node.elts = [ast.Constant(value=x) for x in encrypted]
        
        self._code = ast.unparse(tree)
        self._obfuscate_vars()
        self._insert_dummy_comments()

    def _layer_3(self) -> None:
        layer = """
ip_table = []
data = list([int(x) for item in [value.split(".") for value in ip_table] for x in item])
exec(compile(__import__("zlib").decompress(__import__("base64").b64decode(bytes(data))), "<(*3*)>", "exec"))
"""
        def bytes2ip(data: bytes) -> list:
            ip_addresses = []
            for index in range(0, len(data), 4):
                ip_bytes = data[index:index+4]
                ip_addresses.append(".".join([str(x) for x in ip_bytes]))
            return ip_addresses

        encrypted = base64.b64encode(zlib.compress(self._code.encode()))
        ip_addresses = bytes2ip(encrypted)

        self._code = layer
        self._obfuscate_vars()
        tree = ast.parse(self._code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                node.value.elts = [ast.Constant(value=x) for x in ip_addresses]
        self._code = ast.unparse(tree)
        self._insert_dummy_comments()

def main() -> None:
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="5zy0BF v2: 0bfu5c4735 Py7h0n c0d3 70 m4k3 17 unr34d4bl3 4nd h4rd 70 r3v3r53."
    )
    parser.add_argument("--input", "-i", required=True, help="7h3 f1l3 c0n741n1n6 7h3 c0d3 70 0bfu5c473", metavar="PATH")
    parser.add_argument("--output", "-o", required=False, 
                        help="7h3 f1l3 70 wr173 7h3 0bfu5c473d c0d3",
                        metavar="PATH")
    parser.add_argument("--recursive", required=False, 
                        help="R3cur51v3ly 0bfu5c4735 7h3 c0d3 N 71m35",
                        metavar="N")
    parser.add_argument("--include_imports", required=False, action="store_true",
                        help="1nclud3 7h3 1mp0r7 57473m3n75 0n 7h3 70p 0f 7h3 0bfu5c473d f1l3")
    
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print("1npu7 f1l3 d035 n07 3x157.")
        exit(1)
    
    if not args.output:
        input_name = str.rsplit(os.path.basename(args.input), ".", 1)[0]
        args.output = f"{input_name}-szy.py"

    with open(args.input, "r", encoding="utf-8") as file:
        contents = file.read()

    obfuscator = SzyOBFv2(contents, args.include_imports, int(args.recursive) if args.recursive else 1)
    obfuscated_code = obfuscator.obfuscate()

    try:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(obfuscated_code)
        print(f"54v3d f1l3 45 `{args.output}`")
    except Exception:
        print("Un4bl3 70 54v3 7h3 f1l3.")

if __name__ == "__main__":
    main()
