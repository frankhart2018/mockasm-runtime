from flask import Flask, request, render_template, jsonify, session
import copy

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
        
        session['sequence_of_execution'] = None
        session['sequence_ptr'] = None
        session['source_code'] = None

        source_code = file_utils.read_file(path=path)

        lexer_obj = lexer.Lexer(source_code=source_code)
        tokens = lexer_obj.lexical_analyze()

        parser_obj = parser.Parser(tokens=tokens)
        opcodes = parser_obj.parse()

        vm_obj = vm.VM(opcodes=opcodes)
        sequence_of_execution = []
        for sequence in vm_obj.execute(yield_execution=True):
            if type(sequence) == dict:
                sequence_of_execution.append(copy.deepcopy(sequence))
            else:
                sequence_of_execution.append(sequence)

        output = sequence_of_execution[-1]

        sequence_of_execution = sequence_of_execution[:-1]

        source_lines = source_code.split("\n")
        for sequence in sequence_of_execution:
            sequence['source_code'] = source_lines[sequence['line_num'] - 1]

        session['sequence_of_execution'] = sequence_of_execution
        session['sequence_ptr'] = 1
        session['source_code'] = source_code

        return jsonify({
            "icon": "success",
            "title": "Success",
            "text": "Code executed successfully!",
            "output": output,
            "sequence_of_execution": sequence_of_execution[0],
            "source_code": source_code,
        })

@app.route("/next-output", methods=['POST'])
def next_output():

    if request.method == 'POST':
        sequence_of_execution = session.get('sequence_of_execution', None)
        sequence_ptr = session.get('sequence_ptr', None)
        source_code = session.get('source_code', None)

        if sequence_of_execution != None and sequence_ptr != None and source_code != None:
            current_sequence = sequence_of_execution[sequence_ptr]

            session['sequence_ptr'] += 1

            if session['sequence_ptr'] >= len(session['sequence_of_execution']):
                session['sequence_ptr'] = 0

            return jsonify({
                "icon": "",
                "title": "",
                "text": "",
                "current_sequence": current_sequence,
                "source_code": source_code
            })
        else:
            return jsonify({
                "icon": "error",
                "title": "Error",
                "text": "No sequence found, make sure you have run the code!"
            })