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
    // custom status could be NOT_ENOUGH_PHOTOS
    if (data.status == "SUCCESS") {
        // Fire an event
        $(document).trigger('yearbookReady');
	// Stop checking
	clearInterval(successTimer);
    } else if (data.status == "NOT_ENOUGH_PHOTOS") {
        // Fire an event
        $(document).trigger('yearbookNotEnoughPhotos');
    } else if (data.status == "FAILURE") {
        // Fire an event
        $(document).trigger('yearbookFailure');
    } else {
        // Fire an event
        $(document).trigger('yearbookNotReady');
    }
}

function onGetProgressError(jqXHR, textStatus, errorThrown) {
    // TODO
    console.log('error : ' + textStatus);
}
