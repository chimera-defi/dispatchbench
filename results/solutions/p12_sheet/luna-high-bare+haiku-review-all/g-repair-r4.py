import re
import sys
import threading


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    token_re = re.compile(r"\s*(<=|>=|<>|[A-Z]+[0-9]*|\d+|[()+\-*/,:=<>])")

    def tokenize(text):
        text = text.strip()
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    def is_cell(token):
        return bool(re.fullmatch(r"[A-Z][1-9][0-9]?", token))

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.pos += 1
            return token

        def parse(self):
            return self.expression()

        def expression(self):
            node = self.term()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("binary", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("binary", op, node, self.unary())
            return node

        def unary(self):
            if self.peek() == "-":
                self.take()
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            token = self.take()
            if token == "(":
                node = self.expression()
                self.take()  # )
                return node
            if token is not None and token.isdigit():
                return ("literal", int(token))
            if token in ("SUM", "MIN", "MAX"):
                self.take()  # (
                args = []
                while True:
                    if is_cell(self.peek() or "") and self.pos + 1 < len(self.tokens) \
                            and self.tokens[self.pos + 1] == ":":
                        start = self.take()
                        self.take()  # :
                        end = self.take()
                        args.append(("range", start, end))
                    else:
                        args.append(("formula", self.expression()))
                    if self.peek() != ",":
                        break
                    self.take()
                self.take()  # )
                return ("aggregate", token, args)
            if token == "IF":
                self.take()  # (
                left = self.expression()
                op = self.take()
                right = self.expression()
                self.take()  # ,
                then_node = self.expression()
                self.take()  # ,
                else_node = self.expression()
                self.take()  # )
                return ("if", op, left, right, then_node, else_node)
            if is_cell(token or ""):
                return ("reference", token)
            raise ValueError("Invalid formula")

    state = {}
    values = {}

    def evaluate_cell(name):
        if name not in cells:
            return 0
        current = state.get(name, 0)
        if current == 1:
            return "#CYCLE!"
        if current == 2:
            return values[name]

        state[name] = 1
        content = cells[name]
        if not content.startswith("="):
            result = int(content)
        else:
            tree = Parser(tokenize(content[1:])).parse()
            result = evaluate(tree)
        values[name] = result
        state[name] = 2
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "literal":
            return node[1]
        if kind == "reference":
            return evaluate_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind == "binary":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return "#DIV/0!"
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(then_node if comparisons[op] else else_node)
        if kind == "aggregate":
            _, function, args = node
            collected = []
            for arg in args:
                if arg[0] == "formula":
                    value = evaluate(arg[1])
                    if isinstance(value, str):
                        return value
                    collected.append(value)
                else:
                    _, start, end = arg
                    c1, r1 = ord(start[0]) - ord("A"), int(start[1:])
                    c2, r2 = ord(end[0]) - ord("A"), int(end[1:])
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(ord("A") + col) + str(row)
                            if name in cells:
                                value = evaluate_cell(name)
                                if isinstance(value, str):
                                    return value
                                collected.append(value)
            if not collected:
                return 0
            if function == "SUM":
                return sum(collected)
            if function == "MIN":
                return min(collected)
            return max(collected)
        raise ValueError("Invalid expression")

    errors = []

    def worker():
        try:
            for cell_name in cells:
                evaluate_cell(cell_name)
        except BaseException as exc:
            errors.append(exc)

    # Long reference chains need deep recursion, so run on a thread with a large stack.
    old_limit = sys.getrecursionlimit()
    old_stack = threading.stack_size()
    sys.setrecursionlimit(max(old_limit, 100000))
    threading.stack_size(256 * 1024 * 1024)
    try:
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
    finally:
        threading.stack_size(old_stack)
        sys.setrecursionlimit(old_limit)

    if errors:
        raise errors[0]
    return values
