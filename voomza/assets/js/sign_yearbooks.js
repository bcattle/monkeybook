var loaded = false;
var yearbookTemplate = null;

function onGetYearbooks(yearbooks) {
    yearbooksLoaded();
    var container = $('.all_yearbooks');
    for (var idx in yearbooks) {
        container.append(Mustache.to_html(yearbookTemplate, yearbooks[idx]));
    }
}

function yearbooksLoaded() {
    if (!loaded) {
        loaded = true;
        $('.loading').hide();
        $('.loaded').show();
    }
}

$(document).ready(function() {
    Dajaxice.setup({'default_exception_callback': yearbookTimeout});
    // Get the yearbooks
    Dajaxice.yearbook.get_yearbooks_to_sign(onGetYearbooks);

    // Load template
    Mustache.tags = ['[[', ']]'];
    yearbookTemplate = $('#yearbook_template').html();

    $('.sign_yearbook_submit').click(function() {


        Dajaxice.yearbook.sign_yearbook(submitCallback, {'friend_ids': selected_ids});
    });

});

function yearbookTimeout() {
    if (!loaded) {
        // Only run if the first call timed out
        // TODO: show an error message
    }
}

function submitCallback(next_url) {
    // If everything worked, redirect to the next page
}
