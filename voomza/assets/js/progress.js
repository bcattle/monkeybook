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
    var status = data.status;
    // status could be PENDING, STARTED, RETRY, FAILURE, or SUCCESS
    $('.yearbookNotReadyInitial').hide();
    if (status == "SUCCESS") {
        // Show the "view yearbook" button
        $('.yearbookNotReady').hide();
        $('.yearbookReady').show();
        clearInterval(successTimer);
    } else {
        $('.yearbookNotReady').show();
    }
}

function onGetProgressError(jqXHR, textStatus, errorThrown) {
    // TODO
    console.log('error');
}