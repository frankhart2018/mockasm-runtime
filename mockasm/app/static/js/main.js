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
    }

    function highlight_source_lines(source_code, line_num) {
        highlighted_source_code = "<strong>Source Code:</strong><br><pre>";

        source_lines = source_code.split("\n");
        source_lines.forEach(function (source_line, index) {
            if(index == line_num - 1)
                highlighted_source_code += "<span style='background: yellow;'>" + source_line + "</span><br>";
            else
                highlighted_source_code += source_line + "<br>";
        });

        highlighted_source_code += "</pre>";

        return highlighted_source_code
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
                    highlighted_source_code = highlight_source_lines(result.source_code, result.sequence_of_execution.line_num);
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
                    console.log(result.current_sequence);
                    highlighted_source_code = highlight_source_lines(result.source_code, result.current_sequence.line_num);
                    $("#source_code").html(highlighted_source_code);
                    generate_sequence_tables(result.current_sequence);
                }
            }
        });
    });

});