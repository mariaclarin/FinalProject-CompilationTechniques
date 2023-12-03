import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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
        self.operators = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', '%'}
        self.delimiters = {'(', ')', '{', '}', ';', ',', '.'}
        self.functions = {'console.log', 'alert', 'prompt'}
        self.single_line_comment = {'//'}
        self.multi_line_comment_start = {'/*'}
        self.multi_line_comment_end = {'*/'}

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
        # Check if the current position is the start of a potential function call
        if not line[index].isalpha() and line[index] != '_':
            return False

        # Check if the substring up to the current position is a valid identifier
        while index < len(line) and (line[index].isalnum() or line[index] == '_'):
            index += 1

        # Check if the next character is a dot (indicating a potential function call)
        if index < len(line) and line[index] == '.':
            index += 1
            # Check if the substring after the dot is a valid identifier
            while index < len(line) and (line[index].isalnum() or line[index] == '_'):
                index += 1
            return True

        return False

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

    def extract_delimiter(self, line, index, line_number):
        # Simple check for delimiters
        delimiter = line[index]
        token_type = 'Delimiter'
        if delimiter == '(':
            token_type = 'Lparen'
        elif delimiter == ')':
            token_type = 'Rparen'

        return Token(token_type, delimiter, line_number, index + 1), index + 1

    def extract_single_line_comment(self, line, index, line_number):
        # DFA for single-line comments
        comment = "//"
        index += 2  # Skip the second '/'
        while index < len(line) and line[index] != '\n':
            comment += line[index]
            index += 1


        return Token('Comment', comment, line_number, index), index
# elif char == '/' and i + 1 < code_length and input[i + 1] == '*':
                # comment = char
                # i += 1
                # while i + 1 < code_length and not (input[i] == '*' and input[i + 1] == '/'):
                #     comment += input[i]
                #     if input[i] == '\n':
                #         line += 1
                #     i += 1
                # tokens.append((TOKEN_COMMENT, comment + "*/"))
                # #Multiline comment error handling
                # if i + 1 >= code_length:
                #     print(f"Unterminated comment at line {line}, position {i - 1}")
                # i += 2

    def extract_multi_line_comment(self, line, index, line_number):
        # DFA for multi-line comments
        comment = "/*"
        index += 2  # Skip the '*' after '/'
        while index < len(line) and not (line[index] == '*' and line[index+1]== '/') :
            comment += line[index]
            if line[index] =='\n':
                line_number +=1
            index+=1
        return Token('Comment', comment, line_number, index), index
    
    def extract_operator(self, line, index, line_number):
        # Check for the '/' operator that might indicate the start of a comment
        if line[index] == '/':
            next_index = index + 1
            if next_index < len(line):
                next_char = line[next_index]
                if next_char == '/':
                    return self.extract_single_line_comment(line, index, line_number)
                elif next_char == '*':
                    return self.extract_multi_line_comment(line, index, line_number)

        # Simple check for other operators
        operator = line[index]
        return Token('Operator', operator, line_number, index + 1), index + 1


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
        //comment here
        /*multiline
        here
        */
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

        self.load_file_button = tk.Button(self.root, text="Load File", command=self.load_file)
        self.load_file_button.grid(row=1, column=0, pady=10)

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

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                code = file.read()
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, code)


def main():
    root = tk.Tk()
    app = JavaScriptGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
