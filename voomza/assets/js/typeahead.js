var filter_input;
var selected_element = 0;
var filtered_elements;
var filter_on = false;

// User type to filter
$(document).ready(function(){
    filter_input = $('#filter_input');
    filter_input.val('');

    $('#filter_form').submit(function(e){
        e.preventDefault();
        return false;
    });

    filter_input.keydown(function(e) {
        // Was it the up arrow key?
        if (e.keyCode==38) {
            // Keep the cursor where it is
            e.preventDefault();
            return false;
        }
    });

    filter_input.keyup(function(e) {
        var searchStr = $('#filter_input').val();
        if (searchStr.length) {
            // Was it an arrow key?
            if (e.keyCode==38) {    // up arrow
                // Move selection up
                if (!selected_element) {
                    return;
                } else {
                    selected_element--;
                    updateSelection($(filtered_elements[selected_element]));
                }
            } else if (e.keyCode==40) {     // down arrow
                // Move selection down
                if (selected_element == filtered_elements.length - 1) {
                    return;
                } else {
                    selected_element++;
                    updateSelection($(filtered_elements[selected_element]));
                }
            } else if (e.keyCode==13) {     // enter
                setSelection($(filtered_elements[selected_element]));
            } else {
                // Some other key was pressed
                // Selector version
                friends_elements.hide();
                filtered_elements = friends_elements.filter(':contains('+searchStr+'):not(.selection)')
                    .show();
                filter_on = true;
                selected_element = 0;
                updateSelection($(filtered_elements[selected_element]));
            }
        } else {
            clearFilter();
        }
    });
});

function clearFilter() {
    filter_input.val('');
    // Remove selection
    friends_elements.show();
    friends_elements.filter('.selection').hide();
    filtered_elements = null;
    filter_on = false;
}

function updateSelection(element) {
    // This will get overridden in a different script
    // if we actually want to use the selection capability

}
