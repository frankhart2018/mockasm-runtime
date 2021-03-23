$(document).ready(function() {

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
        $("#intermediate-area").css("display", "block");

        var registers = generate_table(json_object, "registers", "Register")
        $("#registers").html(registers);

        var flags = generate_table(json_object, "flags", "Flag");
        $("#flags").html(flags);

        var memory = generate_table(json_object, "memory", "Memory location");
        $("#memory").html(memory);
    }
    
    $("#run").click(function() {
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
                    $("#source_code").html("<strong>Source Code:</strong><br><pre>" + result.source_code + "</pre>");
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

});