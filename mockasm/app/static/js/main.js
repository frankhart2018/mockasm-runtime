$(document).ready(function() {

    $("#next").css("display", "none");
    $("#intermediate-area").css("display", "none");

    const capitalize = (s) => {
        if (typeof s !== 'string') 
            return ''
        return s.charAt(0).toUpperCase() + s.slice(1)
    }

    function generate_table(json_object, category, th) {
        var table = "<strong>" + capitalize(category) + ":</strong><br><br><table><thead>";
        table += "<tr><th>" + th + "</th><th>Value</th></thead><tbody>";
        category_object = json_object[category];  
        for(var key in category_object) {
            table += "<tr><td>" + key + "</td><td>" + category_object[key] + "</td></tr>";
        }
        table += "</pre>";

        return table;
    }

    function generate_sequence_tables(json_object) {
        $("#next").css("display", "block");
        $("#intermediate-area").css("display", "block");

        var registers = generate_table(json_object, "registers", "Register")
        $("#registers").html(registers);

        var flags = generate_table(json_object, "flags", "Flag");
        $("#flags").html(flags);

        var memory = generate_table(json_object, "memory", "Memory location");
        $("#memory").html(memory);

        var stack = generate_table(json_object, "stack", "Stack");
        $("#stack").html(stack);
    }

    function highlight_source_lines(source_code, line_num) {
        highlighted_source_code = "<strong>Source Code:</strong><br><pre>";

        source_lines = source_code.split("\n");
        var focus_idx = -1;
        source_lines.forEach(function (source_line, index) {
            if(index == line_num - 1) {
                focus_idx = index;
                highlighted_source_code += "<span style='background: yellow;' id='line_" + index + "'>" + 
                                           (parseInt(index) + 1).toString() + ". " + 
                                           source_line + "</span><br>";
            }
            else {
                highlighted_source_code += "<span id='line_" + index + "'>" + 
                                           (parseInt(index) + 1).toString() + ". " + 
                                           source_line + "</span><br>";
            }
        });

        highlighted_source_code += "</pre>";

        return [highlighted_source_code, focus_idx];
    }
    
    $("#run").click(function() {
        $("#next").css("display", "none");
        $("#intermediate-area").css("display", "none");

        var path = $("#path").val();

        if(path) {
            $.ajax({
                url: "/get-output",
                type: "post",
                dataType: "json",
                data: {"path": path},
                success: function(result) {
                    Swal.fire({
                        icon: result.icon,
                        title: result.title,
                        text: result.text,
                    });

                    $("#output").html("<strong>Output:</strong> " + result.output);
                    const source_ret_val = highlight_source_lines(result.source_code, result.sequence_of_execution.line_num);
                    var highlighted_source_code = source_ret_val[0];
                    $("#source_code").html(highlighted_source_code);

                    generate_sequence_tables(result.sequence_of_execution);
                }
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "ASM code file path is required!",
            });
        }
    });

    $("#next").click(function() {
        $.ajax({
            url: "/next-output",
            type: "post",
            dataType: "json",
            success: function(result) {
                if(result.icon == "error") {
                    Swal.fire({
                        icon: result.icon,
                        title: result.title,
                        text: result.text,
                    });
                } else {
                    const source_ret_val = highlight_source_lines(result.source_code, result.current_sequence.line_num);
                    var highlighted_source_code = source_ret_val[0];
                    var focus_idx = source_ret_val[1];
                    $("#source_code").html(highlighted_source_code);

                    document.getElementById("line_" + focus_idx).scrollIntoView({
                        behaviour: "smooth",
                        block: "end",
                        inline: "nearest",
                    });

                    generate_sequence_tables(result.current_sequence);
                }
            }
        });
    });

});