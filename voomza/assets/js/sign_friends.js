var signTemplate = null;
var signsList = null;
var yearbookTemplate = null;
var yearbooksList = null;

var csrftoken = $.cookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function(){
    Mustache.tags = ['[[', ']]'];

    signsList = $('.signs_list');
    yearbooksList = $('.yearbooks_list');
    // Load templates
    signTemplate = $('#yearbook_message_template').html();
    yearbookTemplate = $('#yearbook_template').html();
    yearbookMessageTemplate = $('#yearbook_message_template').html();
    // Pull their signs and yearbooks
    getSigns();
    getYearbooks();

    yearbooksList.scroll(function() {
        // If we're near the bottom, the typeahead filter isn't active,
        // we don't already have a pending request, and there is another page to load
        var el = $(this);
        if ((el.scrollTop() + el.outerHeight()) > .8 * this.scrollHeight
            && !filterActive && !$.active && nextYearbooksUrl) {
            // Load the next page of results
            getYearbooks();
        }
    });
});

function getSigns() {
    // Make the ajax call
    $.ajax({
        url: nextSignsUrl,
        success: onGetSigns,
        error: onGetSignsError
    });
}

function onGetSigns(data, textStatus, jqXHR) {
    nextSignsUrl = data.meta.next;
    var signs = data.objects;
    // If first time through and they have less
    // than a certain number, show Stacy at the end
    if (!data.meta.offset && data.objects.length < 6) {
        signs.push(STACY_DATA);
    }
    // Dump the friends into the list
    var sign_element;
    _.each(signs, function(sign) {
        sign_element = $(Mustache.to_html(signTemplate, sign))
            .hide().appendTo(signsList);
        sign_element.imagesLoaded(function(){
            this.fadeIn(500);
        });
    });
    // Hook up the button click handlers
    registerYearbookSignHandlers();
}

function onGetSignsError(jqXHR, textStatus, errorThrown) {
    // TODO
    console.log('error');
}

function registerYearbookSignHandlers() {
    $('.newSignBtn').click(function() {
        // Does user already have an entry in rt-hand column?
        var curr_yearbook = getExistingElementById($(this).data('id'));
        if (curr_yearbook.length) {
            // Focus it
            curr_yearbook.find('.yearbook_input').focus();
        } else {
            // Otherwise call the server for this user's profile
            var jqXHR = $.ajax({
                url: $(this).data('uri'),
                success: onGetYearbooks
            });
            // Go to the front of the class
            jqXHR.prepend = true;
        }
    });
}

function onModalYearbookSignSent(data, textStatus, jqXHR) {
    // Close the modal
    $.modal.close();
    // Remove the 'sign yearbook' button from the left pane
    $('.newSignBtn[data-id="' + jqXHR.facebook_id + '"]').hide();
    // Remove the user's div from the right column, if any
    getExistingElementById(jqXHR.facebook_id).remove();
    // Show the post to wall dialog
    showPostToWallDialog(jqXHR.facebook_id);
}

function onModalYearbookSignError(jqXHR, textStatus, errorThrown) {
    // TODO
}

function getYearbooks() {
    // Make the ajax call
    $.ajax({
        url: nextYearbooksUrl,
        success: onGetYearbooks,
        error: onGetYearbooksError
    });
}

function onGetYearbooks(data, textStatus, jqXHR) {
    var yearbooks;
    if (data.meta) {
        // If there is a `meta` attr, we got a list
        nextYearbooksUrl = data.meta.next;
        yearbooks = data.objects;
    } else {
        // Otherwise we got a single entry
        yearbooks = [data];
    }
    // Dump the yearbooks into the list
    var yearbooks_element;
    _.each(yearbooks, function(yb_data) {
        yearbooks_element = $(Mustache.to_html(yearbookTemplate, yb_data)).hide();
        if (jqXHR.prepend) {
            yearbooks_element.prependTo(yearbooksList);
        } else {
            yearbooks_element.appendTo(yearbooksList);
        }
        yearbooks_element.imagesLoaded(function(){
            this.fadeIn(500);
        });
    });
    // Register the focus, blur and click handlers
    registerYearbookInputHandlers();
    // If we prepended the elements, focus the first one
    if (jqXHR.prepend) {
        $('.yearbook_input').first().focus();
    }
}

function onGetYearbooksError(jqXHR, textStatus, errorThrown) {
    // TODO
}

var currInput = null;
function registerYearbookInputHandlers() {
    // Sets the sign yearbook focus / blur and submit button handlers
    $('.yearbook_input').focus(function(e){
        // If an input is open, close it
        var newInput = $(e.target);
        if (!currInput || currInput[0] != newInput[0]) {
            if (currInput) {
                closeInput(currInput);
            }
            currInput = newInput;
            var yearbook = currInput.parents('.yearbook');
            // Show name label
//            yearbook.find('.yearbook_name').slideDown(500);
            // Slide open textarea
            currInput.animate({height: '122px'}, 500, 'swing', function(){
                // Scroll to this yearbook
                yearbooksList.scrollTo(yearbook, 500, {axis:'y'});
            });
            // Slide open footer
            yearbook.find('.yearbook_footer').slideDown(500);
        }
    });
//    $('.signYearbookButton').one('click', onSubmitButtonClicked);
    $('.signYearbookButton').click(onSubmitButtonClicked);
}

function closeInput(input) {
    // Slides the input element shut
    var yearbook = input.parents('.yearbook');
    // Hide name label if they haven't typed anything
//    if (!input.val().length) {
//        yearbook.find('.yearbook_name').slideUp(500);
//    }
    // Slide back textarea
    input.animate({height: '40px'}, 500);
    input.scrollTop(0);
    // Slide footer closed
    yearbook.find('.yearbook_footer').slideUp(500);
}

function onSubmitButtonClicked(e) {
    var el = $(e.target);
    var yearbook = el.parents('.yearbook');
    var text = yearbook.find('.yearbook_input').val();
    if (text.length) {
        // Disable the button
        el.attr('disabled', 'disabled');
        // Hide everything else
        yearbook.find('.yearbook_content').slideUp(500);
        yearbook.find('.yearbook_footer').slideUp(500);
        // Submit the yearbook sign
        sendYearbookSign(
            yearbook,
            text,
            onYearbookSignSent,
            onYearbookSignError
        );
        // If there's a filter, clear it
        if (filterActive)
            clearFilter();
    }
}

var lastSendYearbookData;
function sendYearbookSign(yearbook, text, success, error) {
//    console.log('sendYearbookSign called');
    var id = yearbook.data('id');
    // Submit the yearbook sign
    var data = {
        'to_facebook_user_id': id,
        'text': text
    };
    // Reject duplicates
    if (lastSendYearbookData != null && _.isEqual(data, lastSendYearbookData)) {
//        console.log('rejecting duplicate');
        return;
    }
    // Show the sending message
    yearbook.find('.yearbook_sending_message').slideDown(500);
    var sendYearbookXHR = $.ajax({
        url: signsUrl,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        processData: false,
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        },
        success: success,
        error: error
    });
    sendYearbookXHR.facebook_id = id;
    lastSendYearbookData = data;
}

function onYearbookSignSent(data, textStatus, jqXHR) {
//    console.log('onYearbookSignSent called');

    var to_id = jqXHR.facebook_id;
    var yearbook = $('.yearbook[data-id="' + jqXHR.facebook_id + '"]');
    // Show the success indicator
    yearbook.find('.yearbook_sending_message').hide();
    var sent = yearbook.find('.yearbook_sent_message');
    sent.show();
    setTimeout(function(){
        sent.fadeOut(500);
    }, 2000);
    // Set class that it worked
    yearbook.removeClass('yearbook').addClass('yearbook_sent');
    // Show the post to wall dialog
    showPostToWallDialog(to_id);
}

function showPostToWallDialog(to_id) {
    FB.ui({
        method: 'feed',
        display: 'iframe',
        redirect_uri: document.location.href,
        to: to_id,
        link: 'https://developers.facebook.com/docs/reference/dialogs/',
        picture: 'http://fbrell.com/f8.jpg',
        name: 'Facebook Dialogs',
        caption: 'Reference Documentation',
        description: 'Using Dialogs to interact with users.',
        actions: '',    // links in the post
        ref: ''     // for analytics
    }, function(response) {
        // Should return response['post_id']
        // but this never gets called due to x-domain error
        // in redirect coming back from fb dialog
        console.log('Back from facebook dialog');
    });
}

function onYearbookSignError(jqXHR, textStatus, errorThrown) {
    // TODO
    console.log('error');
}
