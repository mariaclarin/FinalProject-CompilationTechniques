import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.font import Font

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
        self.multi_line = False
        self.multi_line_comment = []

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
                elif char.isalpha() and self.multi_line == False or char == '_':
                    token, index = self.extract_identifier_or_function(line, index, line_number)
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
                elif char in self.operators or self.multi_line:
                    token, index = self.extract_operator(line, index, line_number)
                    if token:
                        tokens.append(token)
                    for i in range(len(tokens)):
                        if tokens[i].token_type == "First_Comment":
                            self.multi_line_comment.append(tokens[i].lexeme)
                            tokens.pop(i)
                        elif tokens[i].token_type == "Next_Comment":
                            self.multi_line_comment.append(tokens[i].lexeme)
                            tokens.pop(i)
                        elif tokens[i].token_type == "Last_Comment":
                            self.multi_line_comment.append(tokens[i].lexeme)
                            tokens.pop(i)
                            comments = ""
                            for j in range(len(self.multi_line_comment)):
                                comments += self.multi_line_comment[j]
                                comments += "\n"
                            tokens.append(Token('Comment', comments, line_number, index))
                elif char in self.delimiters: 
                    token, index = self.extract_delimiter(line, index, line_number)
                    if token:
                        tokens.append(token)
                elif char == '.' and self.is_valid_function_call(line, index):
                    token, index = self.extract_function_call(line, index, line_number)
                    if token:
                        tokens.append(token)
                else:
                    error_message = f"Unrecognized Token '{char}'."
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

    def extract_identifier_or_function(self, line, index, line_number):
        # DFA for identifiers
        keyword = ""
        function = ""
        identifier = ""
        if any(keyw in line for keyw in self.keywords):
            while index < len(line) and (line[index].isalnum() or line[index] == '_'):
                keyword += line[index]
                index += 1
            if keyword in self.keywords:
                return Token('Keyword', keyword, line_number, index), index
            else:
                return Token('Identifier', keyword, line_number, index), index
        else:
            for char in line:
                if char.isspace():
                    pass
                else:
                    function += char
                if any(func == function for func in self.functions):
                    index += len(function)
                    return Token('FunctionCall', function, line_number, index), index
                
            while index < len(line) and (line[index].isalnum() or line[index] == '_'):
                identifier += line[index]
                index += 1
            
            return Token('Identifier', identifier, line_number, index), index
    
    def extract_number(self, line, index, line_number):
        # DFA for numbers
        number = ""
        decimal_point_encountered = False

        while index < len(line) and (line[index].isdigit() or line[index] == '.'):
            char = line[index]
            
            if char == '.':
                if decimal_point_encountered:
                    break
                else:
                    decimal_point_encountered = True
            
            number += char
            index += 1

        if '.' in number:
            return Token('Float', float(number), line_number, index), index
        else:
            return Token('Number', int(number), line_number, index), index

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
        comment = "//"
        index += 2  
        while index < len(line) and line[index] != '\n':
            comment += line[index]
            index += 1

        return Token('Comment', comment, line_number, index), index

    def extract_multi_line_comment(self, line, index, line_number):
        comment = "/*"
        index += 2  
        while index < len(line) and not (line[index] == '*' and line[index+1]== '/') :
            comment += line[index]
            if line[index] =='\n':
                line_number +=1
            index+=1
        self.multi_line = True
        return Token('First_Comment', comment, line_number, index), index, 
    
    def extract_operator(self, line, index, line_number):
        if line[index] == '/':
            next_index = index + 1
            if next_index < len(line):
                next_char = line[next_index]
                if next_char == '/':
                    return self.extract_single_line_comment(line, index, line_number)
                elif next_char == '*':
                    return self.extract_multi_line_comment(line, index, line_number)

        # Check if it's a multi line comments or an operator
        if line[-2] == "*":
            if line[-1] == "/":
                comment = ""
                for i in line:
                    comment += i
                    index += 1
                self.multi_line = False
                return Token('Last_Comment', comment, line_number, index), index
            else:
                operator = line[index]
                return Token('Operator', operator, line_number, index + 1), index + 1
        elif line[index] in self.operators:
            operator = line[index]
            return Token('Operator', operator, line_number, index + 1), index + 1
        else:
            comment = ""
            for i in line:
                comment += i
                index += 1
            return Token('Next_Comment', comment, line_number, index + 1), index + 1


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
        
    def check_brackets(self, code):
        stack = []
        errorssyn = []
        line_number = 1
        for line in code.split('\n'):
            index = 0
            for char in line:
                index += 1
                if char in {'(', '{', '['}:
                    stack.append((char, line_number, index))
                elif char in {')', '}', ']'}:
                    if not stack:
                        errorssyn.append((f"Unmatched closing bracket '{char}'", line_number, index))
                    else:
                        last_open, open_line, open_index = stack.pop()
                        if (char == ')' and last_open != '(') or (char == '}' and last_open != '{') or (
                                char == ']' and last_open != '['):
                            errorssyn.append((f"Unmatched closing bracket '{char}'", line_number, index))

            line_number += 1

        for last_open, open_line, open_index in stack:
            errorssyn.append((f"Unmatched opening bracket '{last_open}'", open_line, open_index))

        # Check for while loops without brackets
        for line_number, line in enumerate(code.split('\n'), start=1):
            if "while" in line and "{" not in line and "}" not in line:
                errorssyn.append(("While loop without brackets", line_number, len(line) + 1))
                
        for line_number, line in enumerate(code.split('\n'), start=1):
            if "while" in line and "(" not in line and ")" not in line:
                errorssyn.append(("While loop without parentheses", line_number, len(line) + 1))

        return errorssyn

class JavaScriptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JavaScript Validator")
        self.root.geometry("1230x1000")
        self.root.resizable(True, True)
        self.text = tk.Text(self.root, wrap='word', width=50, height=10)
        
        #left frame containing text input field        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky='nsew')

        self.text = tk.Text(self.main_frame, wrap='word', width=50, height=10)
        self.text.insert(tk.END, """
        var x = 10.5;
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
        while (x === 10.5){
            console.log("Hello");
            break;
        }
        alert("This is an alert!");
        //comment here
        /*multiline
        here
        */
        """)
        self.text.grid(row=0, column=0, padx=10, pady=10, sticky='news')
        self.text.columnconfigure(0, weight=1)

        #divider
        self.scrollbar = tk.Scrollbar(self.main_frame, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.text['yscrollcommand'] = self.scrollbar.set

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        #frame of tables (right side)
        self.tables_frame = tk.Frame(self.main_frame)
        self.tables_frame.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')

        #token table
        self.token_table = ttk.Treeview(self.tables_frame, columns=('Token Type', 'Lexeme', 'Line', 'Index'), show='headings')
        self.token_table.heading('Token Type', text='Token Type')
        self.token_table.heading('Lexeme', text='Lexeme')
        self.token_table.heading('Line', text='Line')
        self.token_table.heading('Index', text='Index')
        self.token_table.column('Token Type', anchor='center')
        self.token_table.column('Lexeme', anchor='center')
        self.token_table.column('Line', anchor='center')
        self.token_table.column('Index', anchor='center')
        self.token_table.grid(row=0, column=0, padx=10, pady=10, sticky='news')

        #syntax table
        self.syntax_table = ttk.Treeview(self.tables_frame, columns=('Syntax Errors', 'Line', 'Index'), show='headings')
        self.syntax_table.heading('Syntax Errors', text='Syntax Errors')
        self.syntax_table.heading('Line', text='Line')
        self.syntax_table.heading('Index', text='Index')
        self.syntax_table.column('Syntax Errors', anchor='center')
        self.syntax_table.column('Line', anchor='center', width= 100)
        self.syntax_table.column('Index', anchor='center')
        self.syntax_table.grid(row=1, column=0, padx=10, pady=10, sticky='news')
        self.syntax_table.column('Syntax Errors', width=400)  # Set a specific width for the "Syntax Errors" column
        self.syntax_table.column('Line', width=200)  
        self.syntax_table.column('Index', width=200)  

        #frame of tables sizing config
        self.tables_frame.rowconfigure(0, weight=2)
        self.tables_frame.rowconfigure(1, weight=1)  
        self.tables_frame.columnconfigure(0, weight=1)
        self.tables_frame.columnconfigure(1, weight=1)

        #parse and load file button config
        self.parse_button = tk.Button(self.root, text="Parse", command=self.parse_code)
        self.parse_button.grid(row=3, column=0, pady=(5, 5),padx=(0,200), sticky='s')

        self.load_file_button = tk.Button(self.root, text="Load File", command=self.load_file)
        self.load_file_button.grid(row=3, column=0, pady=(5, 5), padx=(200,0), sticky='s')

        #rowsize for table rows
        font = Font(family='Arial', size=20) 
        style = ttk.Style()
        style.configure('Treeview', rowheight= font.metrics()['linespace']+25  ) 

        #double click event for row display popup
        self.double_click_cooldown = False
        self.token_table.bind("<Double-1>", self.on_double_click)
    
    def on_double_click(self, event):
        if not self.double_click_cooldown:
            item = self.token_table.selection()
            if item:
                #get the content in the row
                item_values = self.token_table.item(item, "values")
                messagebox.showinfo("Row Information", f"Token Type: {item_values[0]}\n"
                                                    f"Lexeme: {item_values[1]}\n"
                                                    f"Line: {item_values[2]}\n"
                                                    f"Index: {item_values[3]}")

            #prevent double popups with a cooldown
            self.double_click_cooldown = True
            self.root.after(500, self.reset_double_click_cooldown)

    def reset_double_click_cooldown(self):
        self.double_click_cooldown = False

    def parse_code(self):
        # Clear the syntax table before parsing the code
        self.syntax_table.delete(*self.syntax_table.get_children())

        code = self.text.get("1.0", tk.END)
        parser = JavaScriptParser()
        bracket_errors = parser.check_brackets(code)
        # loop_errors = parser.check_loops_syntax(code)
        for error in bracket_errors:
            self.syntax_table.insert('', 'end', values=(error[0], error[1], error[2]), tags=('error',))
        self.syntax_table.tag_configure('error', background='red')
        tokens, errors = parser.tokenize_with_errors(code)
        self.token_table.delete(*self.token_table.get_children())
        for token in tokens:
            self.token_table.insert('', 'end', values=(token.token_type, token.lexeme, token.line, token.index))

        for error in errors:
            self.token_table.insert('', 'end', values=(error.token_type, error.lexeme, error.line, error.index),
                                    tags=('error',))

        self.token_table.tag_configure('error', background='red')

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