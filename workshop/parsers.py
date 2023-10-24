from phply.phpparse import make_parser
from phply.phplex import lexer
from phply import phpast as ast

from langchain.document_loaders.parsers.language.code_segmenter import CodeSegmenter


class PHPSegmenter(CodeSegmenter):
    """Code segmenter for `Python`."""

    def __init__(self, code: str):
        super().__init__(code)
        self.source_lines = self.code.splitlines()


    def is_valid(self):
        try:
            parser = make_parser()
            result = parser.parse(self.code, lexer.clone())
            parser.restart()
            return True
        except AssertionError:
            return False
        except SyntaxError:
            return False

    def _get_line_indexes(self, node):
        start = node.lineno - 1
        inner = [n for n in node.nodes if isinstance(n, (ast.Node))]
        if len(inner) > 0:
            last_node = inner[-1]
            if isinstance(last_node, (ast.Method, ast.Class)):
                [_, end] = self._get_line_indexes(last_node)
            else:
                end = last_node.lineno
            end = end + 1
        else:
            end = node.lineno - 1
        return [start,end]
    
    def _extract_code(self, node):
        [start, end] = self._get_line_indexes(node)
        return "\n".join(self.source_lines[start:end])

    def extract_functions_classes(self):
        functions_classes = []
        parser = make_parser()
        result = parser.parse(self.code, lexer.clone())
        parser.restart()

        for node in result:
            if isinstance(node, (ast.Class, ast.Function)):
                code = self._extract_code(node)
                functions_classes.append(code)

        return functions_classes

    def simplify_code(self):
        all_lines = self.source_lines[:]
        parser = make_parser()
        result = parser.parse(self.code, lexer.clone())
        parser.restart()

        for node in result:
            if isinstance(node, (ast.Class, ast.Function)):
                [start, end] = self._get_line_indexes(node)

                all_lines[start] = f'// Simplified Code for {all_lines[start]}'

                for i in range(start + 1, end):
                    all_lines[i] = None

        return "\n".join(line for line in all_lines if line is not None)
