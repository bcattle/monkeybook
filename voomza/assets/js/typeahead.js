var filterActive = false;
var filterElement = null;
var lastXhr;
var lastSearchStr = '';

// Typeahead filter, pulls from AJAX
$(document).ready(function(){
    filterElement = $('#filter_input');
    filterElement.val('');

//    $('#filter_form').submit(function(e){
//        e.preventDefault();
//        return false;
//    });

    filterElement.keyup(function(e) {
        var searchStr = filterElement.val();
        if (searchStr.length) {
            if (searchStr != lastSearchStr) {
                // If there's an existing request, abort it
                if (lastXhr) {
                    lastXhr.abort();
                }
                // Initiate ajax request for filter
                lastXhr = $.ajax({
                    url: friendsUrl + '?name__icontains=' + encodeURI(searchStr),
                    success: onGetFilteredResults,
                    error: onGetFilteredResultsError
                });
                lastSearchStr = searchStr;
            }
        } else {
            clearFilter();
        }
    });
});

function getExistingElementById(facebook_id) {
    // Returns a person's existing DOM element, if any
    // Look for .friend_unloaded in case one of the pics hasn't loaded yet
    return $('.friend_unloaded[data-id="' + facebook_id + '"]');
}

function onGetFilteredResults(data, textStatus, jqXHR) {
    filterActive = true;
    // Hide all .friend entries
    friendsList.find('.friend').hide();
    // Remove any existing search results
    friendsList.find('.friend_result').remove();
    // Inject the new results
    var friends = data.objects;
    var result_element, curr_element;
    _.each(friends, function(friend) {
        // If this user is already in the DOM,
        // this checkbox should assume the value they already have
        curr_element = getExistingElementById(friend.facebook_id);
        if (curr_element && curr_element.find('input').is(':checked')) {
            // Show template with checkbox checked
            friend.checked = checkedAttr;
        }

        result_element = $(Mustache.to_html(friendTemplate, friend))
            .addClass('friend_result').hide().appendTo(friendsList);
        // Add a callback to show after the image has loaded
        result_element.imagesLoaded(function(){
            this.fadeIn(500);
        });
        // Add a callback if the checkbox value is changed
        result_element.find(':checkbox').change(resultChanged);
        // Add a callback, clicking element changes checkbox
        addCheckboxClickCallback(result_element);
    });
}

// Called when a result checkbox
// is checked or unchecked
function resultChanged(e) {
    var el = $(e.target);
    var curr_element = getExistingElementById(el.attr('value'));        // el is the <input>
    if (curr_element.length) {
        // If there's an existing element in the DOM, update it
        curr_element.find('input').attr('checked', el.is(':checked'));
    } else {
        if (el.is(':checked')) {
            // unchecked -> checked
            // Get the parent, switch the class
            var friend_element=el.parents('.friend_result').clone();
            // Switch the class and insert
            friend_element.removeClass('friend_result').addClass('friend_unloaded')
                .addClass('friend').hide().prependTo(friendsList);
            // Add the click handler
            addCheckboxClickCallback(friend_element);
        }
    }
    // If we just went unchecked->checked, reset the list
    if (el.is(':checked')) {
        clearFilter();
    }
}

function clearFilter() {
    filterElement.val('');
    // Remove any search results
    friendsList.find('.friend_result').remove();
    // Show the originally-loaded friends
    friendsList.find('.friend').show();
    filterActive = false;
}

function onGetFilteredResultsError(jqXHR, textStatus, errorThrown) {
    // TODO: handle the error
}
