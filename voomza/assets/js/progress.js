var successTimer = null;

$(document).ready(function (){
    // Poll for status of the yearbook
    successTimer = setInterval(getProgress, 1000);
});

function getProgress() {
    // Make the ajax call
    $.ajax({
        url: yearbookStatusUrl,
        success: onGetProgress,
        error: onGetProgressError
    });
}

function onGetProgress(data, textStatus, jqXHR) {
    // status could be PENDING, STARTED, RETRY, FAILURE, or SUCCESS
    $('.yearbookNotReadyInitial').hide();
    if (data.status == "SUCCESS") {
        // Update the link url and share modal (if any) with the hash
        var yearbookUrl = window.location.origin + yearbookUrlPath + data.hash + '/';
        $('a.yearbookReady').attr('href', yearbookUrl);
        $('.shareUrl').text(yearbookUrl);
        // Show the "view yearbook" button
        $('.yearbookNotReady').hide();
        $('.yearbookReady').show();
        // Stop the timer
        clearInterval(successTimer);
    } else {
        $('.yearbookNotReady').show();
    }
}

function onGetProgressError(jqXHR, textStatus, errorThrown) {
    // TODO
    console.log('error');
}