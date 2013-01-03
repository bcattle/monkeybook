// Adds pages to the yearbook by making calls to an API

function getPage(page) {
    // Load pages from our API
    $.ajax({
        url: pagesUrl + page + "/",
        success: onGetPage,
        error: onGetPageError
    });
}

function onGetPage(data, textStatus, jqXHR) {
    $('.sj-book .p' + data.page).html(data.page_content);
}

function onGetPageError(jqXHR, textStatus, errorThrown) {
    // TODO
}
