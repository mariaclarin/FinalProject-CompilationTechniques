import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from treelib import Tree, Node

class Token:
    def __init__(self, token_type, lexeme, line, index):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line
        self.index = index


class JavaScriptParser:
    def __init__(self):
        self.keywords = {'if', 'else', 'while', 'function', 'var', 'return', 'for', 'break', 'continue',
                         'true', 'false', 'null', 'undefined', 'new', 'this'}
        self.operators = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='}
        self.delimiters = {'(', ')', '{', '}', ';'}
        self.functions = {'console.log', 'alert', 'prompt'}

    def tokenize_with_errors(self, code):
        tokens = []
        errors = []
        lines = code.split('\n')
        for line_number, line in enumerate(lines, start=1):
            index = 0
            while index < len(line):
                char = line[index]
                if char.isspace():
                    index += 1
                elif char.isalpha() or char == '_':
                    token, index = self.extract_identifier(line, index, line_number)
                    if token:
                        tokens.append(token)
                elif char.isdigit():
                    token, index = self.extract_number(line, index, line_number)
                    if token:
                        tokens.append(token)
                elif char == '"':
                    token, index = self.extract_string(line, index, line_number)
                    if token:
                        tokens.append(token)
                elif char in self.operators:
                    token, index = self.extract_operator(line, index, line_number)
                    if token:
                        tokens.append(token)
                elif char in self.delimiters:
                    token, index = self.extract_delimiter(line, index, line_number)
                    if token:
                        tokens.append(token)
                elif char == '.' and self.is_valid_function_call(line, index):
                    token, index = self.extract_function_call(line, index, line_number)
                    if token:
                        tokens.append(token)
                else:
                    error_message = f"Invalid character '{char}' at line {line_number}, index {index}."
                    errors.append(Token('Error', error_message, line_number, index))
                    index += 1  # Skip the invalid character and continue parsing

        return tokens, errors

    def is_valid_function_call(self, line, index):
        # Check if the current position is the start of a function call
        return line[index:].startswith(tuple(self.functions))

    def extract_identifier(self, line, index, line_number):
        # DFA for identifiers
        identifier = ""
        while index < len(line) and (line[index].isalnum() or line[index] == '_'):
            identifier += line[index]
            index += 1

        return Token('Identifier', identifier, line_number, index), index

    def extract_number(self, line, index, line_number):
        # DFA for numbers
        number = ""
        while index < len(line) and line[index].isdigit():
            number += line[index]
            index += 1

        return Token('Number', number, line_number, index), index

    def extract_string(self, line, index, line_number):
        # DFA for strings
        string = ""
        index += 1  # Skip the opening double quote
        while index < len(line) and line[index] != '"':
            string += line[index]
            index += 1

        if index == len(line):
            print(f"Error: Unclosed string starting at line {line_number}, index {index}.")
            return None, index

        return Token('String', string, line_number, index + 1), index + 1

    def extract_operator(self, line, index, line_number):
        # Simple check for operators
        operator = line[index]
        return Token('Operator', operator, line_number, index + 1), index + 1

    def extract_delimiter(self, line, index, line_number):
        # Simple check for delimiters
        delimiter = line[index]
        return Token('Delimiter', delimiter, line_number, index + 1), index + 1

    def extract_function_call(self, line, index, line_number):
        # Extract the entire function call as a single token
        function_call = ""
        while index < len(line) and (line[index].isalnum() or line[index] in {'_', '.'}):
            function_call += line[index]
            index += 1

        if function_call in self.functions:
            return Token('FunctionCall', function_call, line_number, index), index
        else:
            print(f"Error: Invalid function call '{function_call}' at line {line_number}, index {index}.")
            return None, index


class JavaScriptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JavaScript Parser GUI")

        self.text = tk.Text(self.root, wrap='word', width=50, height=10)
        self.text.insert(tk.END, """
        var x = 10;
        if (x > 5) {
            console.log("Hello, world!");
        }
        for (var i = 0; i < 5; i++) {
            if (i % 2 === 0) {
                continue;
            } else {
                break;
            }
        }
        alert("This is an alert!");
        """)

        self.text.grid(row=0, column=0, padx=10, pady=10, sticky='news')

        self.scrollbar = tk.Scrollbar(self.root, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.text['yscrollcommand'] = self.scrollbar.set

        self.result_tree = ttk.Treeview(self.root, columns=('Token Type', 'Lexeme', 'Line', 'Index'))
        self.result_tree.heading('#0', text='Output')
        self.result_tree.heading('Token Type', text='Token Type')
        self.result_tree.heading('Lexeme', text='Lexeme')
        self.result_tree.heading('Line', text='Line')
        self.result_tree.heading('Index', text='Index')
        self.result_tree.column('#0', width=200, stretch=tk.NO)
        self.result_tree.column('Token Type', anchor='center')
        self.result_tree.column('Lexeme', anchor='center')
        self.result_tree.column('Line', anchor='center')
        self.result_tree.column('Index', anchor='center')

        self.result_tree.grid(row=0, column=2, padx=10, pady=10, sticky='news')

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(2, weight=1)

        self.parse_button = tk.Button(self.root, text="Parse", command=self.parse_code)
        self.parse_button.grid(row=1, column=0, columnspan=3, pady=10)

        self.parse_tree_label = tk.Label(self.root, text="Parse Tree")
        self.parse_tree_label.grid(row=2, column=0, pady=(10, 0))

        self.parse_tree_canvas = tk.Canvas(self.root, width=800, height=400)
        self.parse_tree_canvas.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def parse_code(self):
        code = self.text.get("1.0", tk.END)
        parser = JavaScriptParser()
        tokens, errors = parser.tokenize_with_errors(code)

        self.result_tree.delete(*self.result_tree.get_children())

        for token in tokens:
            self.result_tree.insert('', 'end', values=(token.token_type, token.lexeme, token.line, token.index))

        for error in errors:
            self.result_tree.insert('', 'end', values=(error.token_type, error.lexeme, error.line, error.index),
                                    tags=('error',))

        if errors:
            messagebox.showerror("Parse Error", "Some errors were encountered in the code. See the output for details.")

        self.result_tree.tag_configure('error', background='red', foreground='white')

        # Build parse tree
        parse_tree = self.build_parse_tree(tokens)
        self.visualize_parse_tree(parse_tree)

    def build_parse_tree(self, tokens):
        parse_tree = Tree()
        current_node = parse_tree.create_node("Program", "program")

        for i, token in enumerate(tokens, start=1):
            node_id = f"{token.token_type}_{token.lexeme}_{i}"
            parse_tree.create_node(f"{token.token_type}: {token.lexeme}", node_id, parent=current_node.identifier, data=token)

        return parse_tree

    def visualize_parse_tree(self, parse_tree):
        self.parse_tree_canvas.delete("all")
        self.draw_tree(parse_tree, self.parse_tree_canvas, x=400, y=20)
    def draw_tree(self, tree, canvas, node=None, x=0, y=0, dx=60, dy=240):  # Increased dx and dy values
        if node is None:
            node = tree.get_node(tree.root)

        canvas.create_text(x, y, text=node.data.lexeme, anchor=tk.S, tags="tree_node")
        children = tree.children(node.identifier)
        if children:
            x_offset = len(children) * dx / 2
            for child in children:
                x_child = x + x_offset
                y_child = y + dy  # Increased vertical separation
                canvas.create_line(x, y, x_child, y_child - 15, width=2, tags="tree_edge")
                self.draw_tree(tree, canvas, child, x_child, y_child, dx, dy)
                x_offset -= dx
def main():
    root = tk.Tk()
    app = JavaScriptGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
