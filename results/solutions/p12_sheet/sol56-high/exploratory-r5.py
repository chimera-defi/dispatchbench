def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    DIV_ZERO = "#DIV/0!"
    CYCLE = "#CYCLE!"

    class Parser:
        def __init__(self, source):
            self.tokens = self.tokenize(source)
            self.pos = 0

        @staticmethod
        def tokenize(source):
            tokens = []
            i = 0
            n = len(source)

            while i < n:
                c = source[i]

                if c.isspace():
                    i += 1
                elif c.isdigit():
                    j = i + 1
                    while j < n and source[j].isdigit():
                        j += 1
                    tokens.append(("NUM", int(source[i:j])))
                    i = j
                elif c.isalpha():
                    j = i + 1
                    while j < n and source[j].isalpha():
                        j += 1
                    word = source[i:j]

                    if len(word) == 1 and j < n and source[j].isdigit():
                        k = j + 1
                        while k < n and source[k].isdigit():
                            k += 1
                        tokens.append(("CELL", source[i:k]))
                        i = k
                    else:
                        tokens.append(("NAME", word))
                        i = j
                elif source.startswith("<>", i):
                    tokens.append(("CMP", "<>"))
                    i += 2
                elif source.startswith("<=", i):
                    tokens.append(("CMP", "<="))
                    i += 2
                elif source.startswith(">=", i):
                    tokens.append(("CMP", ">="))
                    i += 2
                elif c in "<>=":
                    tokens.append(("CMP", c))
                    i += 1
                else:
                    tokens.append((c, c))
                    i += 1

            tokens.append(("EOF", None))
            return tokens

        def peek(self, offset=0):
            return self.tokens[self.pos + offset]

        def take(self, kind=None):
            token = self.tokens[self.pos]
            if kind is not None and token[0] != kind:
                raise ValueError("Unexpected token")
            self.pos += 1
            return token

        def parse(self):
            result = self.parse_add()
            self.take("EOF")
            return result

        def parse_add(self):
            first = self.parse_mul()
            rest = []

            while self.peek()[0] in ("+", "-"):
                op = self.take()[0]
                rest.append((op, self.parse_mul()))

            return ("seq", first, tuple(rest)) if rest else first

        def parse_mul(self):
            first = self.parse_unary()
            rest = []

            while self.peek()[0] in ("*", "/"):
                op = self.take()[0]
                rest.append((op, self.parse_unary()))

            return ("seq", first, tuple(rest)) if rest else first

        def parse_unary(self):
            negate = False
            while self.peek()[0] == "-":
                self.take("-")
                negate = not negate

            node = self.parse_atom()
            return ("neg", node) if negate else node

        def parse_atom(self):
            kind, value = self.take()

            if kind == "NUM":
                return ("const", value)

            if kind == "CELL":
                return ("ref", value)

            if kind == "(":
                node = self.parse_add()
                self.take(")")
                return node

            if kind == "NAME":
                self.take("(")

                if value == "IF":
                    left = self.parse_add()
                    op = self.take("CMP")[1]
                    right = self.parse_add()
                    self.take(",")
                    then_branch = self.parse_add()
                    self.take(",")
                    else_branch = self.parse_add()
                    self.take(")")
                    return ("if", left, op, right, then_branch, else_branch)

                arguments = []
                while True:
                    if self.peek()[0] == "CELL" and self.peek(1)[0] == ":":
                        start = self.take("CELL")[1]
                        self.take(":")
                        end = self.take("CELL")[1]
                        arguments.append(("range", start, end))
                    else:
                        arguments.append(("expr", self.parse_add()))

                    if self.peek()[0] != ",":
                        break
                    self.take(",")

                self.take(")")
                return ("func", value, tuple(arguments))

            raise ValueError("Unexpected token")

    maximum_length = max(
        (len(content) for content in cells.values() if content.startswith("=")),
        default=0,
    )
    old_limit = sys.getrecursionlimit()
    new_limit = max(old_limit, maximum_length * 5 + 1000)
    changed_limit = new_limit != old_limit

    if changed_limit:
        sys.setrecursionlimit(new_limit)

    try:
        definitions = {}
        for name, content in cells.items():
            if content.startswith("="):
                definitions[name] = Parser(content[1:]).parse()
            else:
                definitions[name] = ("const", int(content))
    finally:
        if changed_limit:
            sys.setrecursionlimit(old_limit)

    state = {}
    values = {}

    def is_error(value):
        return isinstance(value, str)

    def range_sources(arguments):
        for argument in arguments:
            if argument[0] == "expr":
                yield argument[1]
                continue

            start, end = argument[1], argument[2]
            c1, r1 = ord(start[0]), int(start[1:])
            c2, r2 = ord(end[0]), int(end[1:])

            left, right = sorted((c1, c2))
            top, bottom = sorted((r1, r2))

            for row in range(top, bottom + 1):
                for column in range(left, right + 1):
                    name = chr(column) + str(row)
                    if name in cells:
                        yield ("ref", name)

    def truncated_division(left, right):
        quotient = abs(left) // abs(right)
        return -quotient if (left < 0) != (right < 0) else quotient

    def evaluate(start_name):
        tasks = [("cell", start_name)]
        stack = []

        while tasks:
            task = tasks.pop()
            tag = task[0]

            if tag == "cell":
                name = task[1]

                if name not in cells:
                    stack.append(0)
                elif state.get(name) == 2:
                    stack.append(values[name])
                elif state.get(name) == 1:
                    stack.append(CYCLE)
                else:
                    state[name] = 1
                    tasks.append(("cell_done", name))
                    tasks.append(("node", definitions[name]))

            elif tag == "cell_done":
                name = task[1]
                value = stack.pop()
                state[name] = 2
                values[name] = value
                stack.append(value)

            elif tag == "node":
                node = task[1]
                node_tag = node[0]

                if node_tag == "const":
                    stack.append(node[1])

                elif node_tag == "ref":
                    tasks.append(("cell", node[1]))

                elif node_tag == "neg":
                    tasks.append(("neg_done",))
                    tasks.append(("node", node[1]))

                elif node_tag == "seq":
                    tasks.append(("seq_next", node[2], 0))
                    tasks.append(("node", node[1]))

                elif node_tag == "func":
                    initial = 0 if node[1] == "SUM" else None
                    iterator = range_sources(node[2])
                    tasks.append(("agg_next", node[1], iterator, initial))

                elif node_tag == "if":
                    tasks.append(
                        ("if_left", node[2], node[3], node[4], node[5])
                    )
                    tasks.append(("node", node[1]))

            elif tag == "neg_done":
                value = stack.pop()
                stack.append(value if is_error(value) else -value)

            elif tag == "seq_next":
                operations, index = task[1], task[2]
                left = stack.pop()

                if is_error(left) or index == len(operations):
                    stack.append(left)
                else:
                    op, right_node = operations[index]
                    tasks.append(("seq_apply", operations, index, left, op))
                    tasks.append(("node", right_node))

            elif tag == "seq_apply":
                operations, index, left, op = task[1:]
                right = stack.pop()

                if is_error(right):
                    stack.append(right)
                    continue

                if op == "+":
                    result = left + right
                elif op == "-":
                    result = left - right
                elif op == "*":
                    result = left * right
                elif right == 0:
                    stack.append(DIV_ZERO)
                    continue
                else:
                    result = truncated_division(left, right)

                stack.append(result)
                tasks.append(("seq_next", operations, index + 1))

            elif tag == "agg_next":
                function, iterator, accumulated = task[1:]
                try:
                    node = next(iterator)
                except StopIteration:
                    stack.append(0 if accumulated is None else accumulated)
                else:
                    tasks.append(
                        ("agg_apply", function, iterator, accumulated)
                    )
                    tasks.append(("node", node))

            elif tag == "agg_apply":
                function, iterator, accumulated = task[1:]
                value = stack.pop()

                if is_error(value):
                    stack.append(value)
                    continue

                if function == "SUM":
                    accumulated += value
                elif accumulated is None:
                    accumulated = value
                elif function == "MIN":
                    accumulated = min(accumulated, value)
                else:
                    accumulated = max(accumulated, value)

                tasks.append(("agg_next", function, iterator, accumulated))

            elif tag == "if_left":
                op, right_node, then_node, else_node = task[1:]
                left = stack.pop()

                if is_error(left):
                    stack.append(left)
                else:
                    tasks.append(
                        ("if_right", left, op, then_node, else_node)
                    )
                    tasks.append(("node", right_node))

            elif tag == "if_right":
                left, op, then_node, else_node = task[1:]
                right = stack.pop()

                if is_error(right):
                    stack.append(right)
                    continue

                if op == "=":
                    condition = left == right
                elif op == "<>":
                    condition = left != right
                elif op == "<":
                    condition = left < right
                elif op == "<=":
                    condition = left <= right
                elif op == ">":
                    condition = left > right
                else:
                    condition = left >= right

                tasks.append(("node", then_node if condition else else_node))

        return stack.pop()

    return {name: evaluate(name) for name in cells}
