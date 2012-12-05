var filterActive = false;
var filterElement = null;
var lastXhr, lastSignedXhr;
var lastSearchStr = '';
var signedYearbookTemplate;

// Typeahead filter, pulls from AJAX
$(document).ready(function(){
    filterElement = $('#filter_input');
    filterElement.val('');
    signedYearbookTemplate = $('#signed_yearbook_template').html();

    filterElement.keyup(function(e) {
        var searchStr = filterElement.val();
        if (searchStr.length) {
            if (searchStr != lastSearchStr) {
                // If there's an existing request, abort it
                if (lastXhr) {
                    lastXhr.abort();
                }
                if (lastSignedXhr) {
                    lastSignedXhr.abort();
                }

                // We make two requests here,
                // one for yearbooks they *have* signed that match
                // and one for yearbooks they haven't signed

                // People I haven't signed
                // Unsigned yearbooks
                lastXhr = $.ajax({
                    url: unSignedYearbooksUrl + '?name__icontains=' + encodeURI(searchStr),
                    success: onGetFilteredResults,
                    error: onGetFilteredResultsError
                });
                // People I have signed
                lastSignedXhr = $.ajax({
                    url: signedYearbooksUrl + '?name__icontains=' + encodeURI(searchStr),
                    success: onGetSignedResults
                });
                lastSearchStr = searchStr;
            }
        } else {
            clearFilter();
        }
    });
});

function getExistingElementById(facebook_id) {
    return $('.yearbook[data-id="' + facebook_id + '"]');
}

function onGetFilteredResults(data, textStatus, jqXHR) {
    filterActive = true;
    // Hide all .yearbook entries
    yearbooksList.find('.yearbook').hide();
    // Remove any existing search results
    yearbooksList.find('.yearbook_result').remove();
    // Inject the new results
    var results = data.objects;
    var result_element, curr_text, result_input;
    _.each(results, function(result) {
        // If the user is already in the DOM,
        // assume the value their textarea already has
        curr_text = getExistingElementById(result.facebook_id).find('.yearbook_input').val();
        result_element = $(Mustache.to_html(yearbookTemplate, result))
            .addClass('yearbook_result').hide().appendTo(yearbooksList);
        // Add a callback to show after the image has loaded
        result_element.imagesLoaded(function(){
            this.fadeIn(500);
        });
        result_input = result_element.find('.yearbook_input');
        result_input.val(curr_text);
        // Add a callback if the textarea value is changed
        result_input.change(onTextChanged);
        // Register the focus/unfocus, etc. callbacks
        registerYearbookInputHandlers();
    });
}

function onGetSignedResults(data, textStatus, jqXHR) {
    // Remove any existing search results
    yearbooksList.find('.signed_yearbook_result').remove();
    // Prepend these results to the top of the list
    var results = data.objects;
    _.each(results, function(result) {
        $(Mustache.to_html(signedYearbookTemplate, result)).show().prependTo(yearbooksList);
    });
}

function onTextChanged(e) {
    // Add the element to the official DOM if it didn't already exist
    var el = $(e.target);       // el is the <textarea>
    var curr_result = el.parents('yearbook_result');
    var curr_element = getExistingElementById(curr_result.data('id'));
    if (curr_element.length) {
        // If there's an existing element in the DOM, update it
        curr_element.find('.yearbook_input').val(el.val());
    } else {
        // Get the parent, switch the class
        curr_result.clone().removeClass('yearbook_result')
            .hide().prependTo(yearbooksList);
        // Add callbacks to the new element
        registerYearbookInputHandlers();
    }
}

function clearFilter() {
    filterElement.val('');
    // Remove any search results
    yearbooksList.find('.yearbook_result').remove();
    yearbooksList.find('.signed_yearbook_result').remove();
    // Show the originally-loaded friends
    yearbooksList.find('.yearbook').show();
    filterActive = false;
}

function onGetFilteredResultsError(jqXHR, textStatus, errorThrown) {
    // TODO: handle the error
}