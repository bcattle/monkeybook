var filterActive = false;
var filterElement = null;
var lastXhr;
var resultTemplate;
var lastSearchStr = '';

// Typeahead filter, pulls from AJAX
$(document).ready(function(){
    resultTemplate = $('#friend_template_search_result');
    filterElement = $('#filter_input');
    filterElement.val('');

    $('#filter_form').submit(function(e){
        e.preventDefault();
        return false;
    });

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

function onGetFilteredResults(data, textStatus, jqXHR) {
    filterActive = true;
    // Hide all .friend entries
    friendsList.find('.friend').hide();
    // Remove any existing search results
    friendsList.find('.friend_result').remove();
    // Inject the new results
    var friends = data.objects;
    var result_element;
    _.each(friends, function(friend) {
//        result_element = $(Mustache.to_html(resultTemplate, friend))
        result_element = $(Mustache.to_html(friendTemplateUnchecked, friend))
            .addClass('friend_result').hide().appendTo(friendsList);
        // Add a callback to show after the image has loaded
        result_element.imagesLoaded(function(){
            this.fadeIn(500);
        });
        // Add a callback if the checkbox value is changed
        result_element.change(function(){
            // TODO
        });
        // Add a callback, clicking element changes checkbox
        result_element.click(function(){
            // TODO
//            this.filter('input')
        });
    });
}

function resultChecked() {
    // TODO
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
