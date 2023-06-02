const clear_form = () => {
    var input_elements = document.getElementsByTagName("input");
    var new_textarea_element = document.getElementsByID("new_review_content");
    for (var ii=0; ii < input_elements.length; ii++) {
        if (input_elements[ii].type == "text" || input_elements[ii].type == "email" || input_elements[ii].type == "password") {
            input_elements[ii].value = "";
            }
    }
}