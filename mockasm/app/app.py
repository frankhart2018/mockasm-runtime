from flask import Flask, request, render_template, jsonify

from ..lexer import lexer
from ..parser import parser
from ..runtime import vm
from ..utils import file_utils

# Instantiate flask app
app = Flask(__name__)

# Basic config for flask app
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.secret_key = "my-secret-key"
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/", methods=['GET'])
def index():

    if request.method == "GET":
        return render_template("index.html")

@app.route("/get-output", methods=['POST'])
def get_output():

    if request.method == "POST":
        path = request.form['path']
        
        source_code = file_utils.read_file(path=path)

        lexer_obj = lexer.Lexer(source_code=source_code)
        tokens = lexer_obj.lexical_analyze()

        parser_obj = parser.Parser(tokens=tokens)
        opcodes = parser_obj.parse()

        vm_obj = vm.VM(opcodes=opcodes)
        sequence_of_execution = vm_obj.execute(yield_execution=True)
        output = list(sequence_of_execution)[-1]

        return jsonify({
            "icon": "success",
            "title": "Success",
            "text": "Code executed successfully!",
            "output": output
        })