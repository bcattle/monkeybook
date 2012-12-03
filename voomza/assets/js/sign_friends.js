var signTemplate = null;
var signsList = null;
var yearbookTemplate = null;
var yearbooksList = null;

$(document).ready(function(){
    signsList = $('.signs_list');
    yearbooksList = $('.yearbooks_list');
    // Load templates
    signTemplate = $('#sign_template').html();
    yearbookTemplate = $('#yearbook_template').html();
    yearbookMessageTemplate = $('#yearbook_message_template').html();
    // Pull their signs and yearbooks
    getSigns();
    getYearbooks();
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
}

function registerYearbookSignHandlers() {
    $('.viewSignBtn').click(function() {
        // Unhide the loading message
        $('.yearbook_message_modal_loading').show();
        // Request message from server
        onViewSignRecieved();
        // Show modal with loading spinner
        $('#yearbook_message_modal').modal();
    });
    $('.newSignBtn').click(function() {

    });
}

function onViewSignRecieved(data, textStatus, jqXHR) {
    // Called when server responds with yearbook sign message
    // Hide the loading message
    $('.yearbook_message_modal_loading').hide();
    // Ditch any old message
    var modal_body = $('.yearbook_message_modal_body');
    modal_body.empty();
    // Render with STACY_DATA for now
    modal_body.append(Mustache.to_html(yearbookMessageTemplate, STACY_DATA));
    registerModalHandlers();
}

function registerModalHandlers() {
    // Registers handlers to create new yearbook sign from modal
    $('.modalNewSignBtn').click(function() {
        // Hide the button
        $(this).hide();
        // Show the sign input
        $('.message_sign_input_container').slideDown(500);
    });
    $('.modal_yearbook_input').focus(function(){
        $(this).animate({height: '80px'}, 500);
    });
    $('.signYearbookButtonModal').click(function (){
        // Send the yearbook sign
    });
}

function onViewSignError(jqXHR, textStatus, errorThrown) {
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
    nextYearbooksUrl = data.meta.next;
    var yearbooks = data.objects;
    // Dump the yearbooks into the list
    var yearbooks_element;
    _.each(yearbooks, function(sign) {
        yearbooks_element = $(Mustache.to_html(yearbookTemplate, sign))
            .hide().appendTo(yearbooksList);
        yearbooks_element.imagesLoaded(function(){
            this.fadeIn(500);
        });
    });
    // Register the focus, blur and click handlers
    registerYearbookInputHandlers();
}

function onGetYearbooksError(jqXHR, textStatus, errorThrown) {
    // TODO
}

function registerYearbookInputHandlers() {
    // Sets the sign yearbook focus / blur and submit button handlers
    $('.yearbook_input').focus(function(e){
        var input = $(e.target);
        var yearbook = input.parents('.yearbook');
        // Show name label
        yearbook.find('.yearbook_name').slideDown(500);
        // Slide open textarea
        input.animate({height: '122px'}, 500, 'swing', function(){
            // Scroll to this yearbook
            yearbooksList.scrollTo(yearbook, 500, {axis:'y'});
        });
        // Slide open footer
        yearbook.find('.yearbook_footer').slideDown(500);
    });
    $('.yearbook_input').blur(function(e) {
        var input = $(e.target);
        var yearbook = input.parents('.yearbook');
        // Hide name label if they haven't typed anything
        if (!input.val().length) {
            yearbook.find('.yearbook_name').slideUp(500);
        }
        // Slide back textarea
        input.animate({height: '40px'}, 500);
        input.scrollTop(0);
        // Slide footer closed
        yearbook.find('.yearbook_footer').slideUp(500);
    });
    $('.signYearbookButton').click(function(){
        // Collapse the yearbook and show the loading spinner

        // Submit the yearbook sign

        // Show the post to wall dialog
    });
}