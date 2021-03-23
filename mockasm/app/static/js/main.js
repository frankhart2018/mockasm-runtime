$(document).ready(function() {
    
    $("#run").click(function() {
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
                    console.log(result.output);
                    $("#output").html(result.output);
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