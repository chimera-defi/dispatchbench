import re
import sys

sys.setrecursionlimit(100000)

ERROR_DIV = "#DIV/0!"
ERROR_CYCLE = "#CYCLE!"
ERRORS = {ERROR_DIV, ERROR_CYCLE}


def _tokenize(source):
    pattern = re.compile(
        r"\s+|<=|>=|<>|[+\-*/(),:=<>]|\d+|[A-Z][1-9]\d*|[A-Z]+"
    )
    tokens = []
    pos = 0
    while pos < len(source):
        match = pattern.match(source, pos)
        if not match:
            raise ValueError("Invalid formula")
        token = match.group()
        pos = match.end()
        if not token.isspace():
            tokens.append(token)
    return tokens


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self):
        token = self.peek()
        self.pos += 1
        return token

    def expression(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.peek() in ("*", "/"):
            op = self.take()
            node = ("bin", op, node, self.unary())
        return node

    def unary(self):
        if self.peek() == "-":
            self.take()
            return ("neg", self.unary())
        return self.atom()

    def atom(self):
        token = self.take()
        if token is None:
            raise ValueError("Unexpected end of formula")

        if token.isdigit():
            return ("num", int(token))

        if token == "(":
            node = self.expression()
            self.take()  # )
            return node

        if re.fullmatch(r"[A-Z][1-9]\d*", token):
            return ("cell", token)

        if token in ("SUM", "MIN", "MAX", "IF"):
            self.take()  # (
            if token == "IF":
                left = self.expression()
                op = self.take()
                right = self.expression()
                self.take()  # ,
                then = self.expression()
                self.take()  # ,
                otherwise = self.expression()
                self.take()  # )
                return ("if", left, op, right, then, otherwise)

            args = []
            while True:
                first = self.peek()
                second = (
                    self.tokens[self.pos + 1]
                    if self.pos + 1 < len(self.tokens)
                    else None
                )
                if (
                    first
                    and re.fullmatch(r"[A-Z][1-9]\d*", first)
                    and second == ":"
                ):
                    start = self.take()
                    self.take()  # :
                    end = self.take()
                    args.append(("range", start, end))
                else:
                    args.append(("arg", self.expression()))

                if self.peek() != ",":
                    break
                self.take()

            self.take()  # )
            return ("func", token, args)

        raise ValueError("Unexpected token")


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    parsed = {}
    values = {}
    active = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return ERROR_CYCLE

        active.add(name)
        content = cells[name]
        if isinstance(content, int):
            result = content
        elif not content.startswith("="):
            result = int(content.strip())
        else:
            if name not in parsed:
                parsed[name] = _Parser(_tokenize(content[1:])).expression()
            result = evaluate(parsed[name])

        active.remove(name)
        values[name] = result
        return result

    def evaluate(node):
        kind = node[0]

        if kind == "num":
            return node[1]
        if kind == "cell":
            return cell_value(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if value in ERRORS else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if left in ERRORS:
                return left
            right = evaluate(right_node)
            if right in ERRORS:
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return ERROR_DIV
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            _, left_node, op, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if left in ERRORS:
                return left
            right = evaluate(right_node)
            if right in ERRORS:
                return right

            conditions = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(then_node if conditions[op] else else_node)

        _, function, args = node
        collected = []
        for arg in args:
            if arg[0] == "range":
                _, start, end = arg
                c1, r1 = ord(start[0]) - 65, int(start[1:])
                c2, r2 = ord(end[0]) - 65, int(end[1:])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        name = chr(col + 65) + str(row)
                        if name in cells:
                            value = cell_value(name)
                            if value in ERRORS:
                                return value
                            collected.append(value)
            else:
                value = evaluate(arg[1])
                if value in ERRORS:
                    return value
                collected.append(value)

        if not collected:
            return 0
        if function == "SUM":
            return sum(collected)
        if function == "MIN":
            return min(collected)
        return max(collected)

    return {name: cell_value(name) for name in cells}
