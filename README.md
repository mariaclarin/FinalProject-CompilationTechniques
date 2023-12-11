# JavaScript Validator Program
This is a final project program for Compilation Techniques class. We built a JavaScript source code validator, that tokenize and parse an input JS code to return errors within the code. The tokenizer returns every character/instance token found within the code, providing the token, lexeme, line number, and index of the character/instance. The parser is able to trace unmatched/imbalanced opening brackets {} and parentheses (), along with while loop format syntax of 'while (conditionhere){effecthere}' by checking if there is the existing parentheses before the brackets and if there is the existing brackets after the parentheses. If it encounters a syntax error, it will return the error, line number, and index.</br>
</br>
This program helps users identify potential errors of their codes before they run them. Highlighting the lines and the index of the error so the users can debug them right away. 

## Contributor Details
Class: L5AC </br>
Members: </br>
* Ferdinand Jacques (2501982600)
* Hansel Faren (2501990350)
* Maria Clarin (2501990331)
* Nicholas Valerianus Budiman (2502055596)

## Specification and Limitation
#### Tokens recognized and Lexemes Within: </br>
1. **Keywords** : 'if', 'else', 'while', 'function', 'var', 'return', 'for', 'break', 'continue','true', 'false', 'null', 'undefined', 'new', 'this' </br>
2. **Operators** : '+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=', '%' </br>
3. **Delimiters** : '(', ')', '{', '}', ';', ',', '.'
4. **Functions** : 'console.log', 'alert', 'prompt'
5. **Comments** : [//single line comments], [/* multi line \n comments */]

#### Parsing Syntax Errors Recognized: </br>
1. **Unmatched Opening Parentheses ()**
2. **Unmatched Opening Brackets {}**
3. **While Loop Without Parentheses () Before Brackets {}**
4. **While Loop Without Brackets {} After Parentheses ()**

## How to Install
1. Clone the repository via GitHub or the following command
```
git clone https://github.com/mariaclarin/FinalProject-CompilationTechniques 
```
2. Install dependencies for the GUI
```
pip install tkinter
```
3. run JSValidator.py

## Program Manual 
The program has a default testing code already enterred upon running the file. If the user wants to use a different file to test the load file feature, they can use 'example.txt'.

### Default Main Page
* Display may vary slightly, the attached display is on Mac OS.
![landing page](https://cdn.discordapp.com/attachments/794551109523341353/1183800311362629652/Screen_Shot_2023-12-11_at_22.59.38.png?ex=6589a6f4&is=657731f4&hm=a9088505c8d34cce12934eafafa755bf4dcaa835453ff8f267c1cda770257dd8&)
</br>

**Elements and Functionality:**</br>

1. Code input text field : users can type their source code directly on the input field
2. Load file button : users can load .txt file types containing their source code instead of typing their code manually
3. Token table : displays all recognized tokens and lexemes along with errors (if any)
4. Syntax errors table : displays all recognized parsing errors (if any)
5. Parse button : starts the tokenization and parsing process of the input code 
6. Token table row content display event : users can double click on any row to view the full content of the row.

### Tokens, Token Errors, and Syntax Errors Display 
* Display may vary slightly, the attached display is on Mac OS.
![errors](https://cdn.discordapp.com/attachments/794551109523341353/1183802810408636447/Screen_Shot_2023-12-11_at_23.09.38.png?ex=6589a947&is=65773447&hm=b79a366557330e0a111ac2e907bfff6e19d9bca62a9442a989010ca4df4b1f58&)

### Token Table Expand Row Display
* Display may vary slightly, the attached display is on Mac OS.
![errors](https://cdn.discordapp.com/attachments/794551109523341353/1183803403822977155/Screen_Shot_2023-12-11_at_23.11.46.png?ex=6589a9d5&is=657734d5&hm=4b950c9c1a124ad8ecd2ca1c403637b4d04e9caaccb377e1450d78bb684f48f0&)
