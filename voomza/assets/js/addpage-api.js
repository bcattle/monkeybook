function addPage(page, book) {
    var id, pages = book.turn('pages');
    if (!book.turn('hasPage', page)) {
        var element = $('<div />',
            {'class': 'own-size',
                css: {width: 456, height: 333}
            }).
            html('<div class="loader"></div>');

        if (book.turn('addPage', element, page)) {
            getPage(page);
        }
    }
}

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
