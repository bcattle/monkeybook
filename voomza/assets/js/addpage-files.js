function addPage(page, book) {
    var id, pages = book.turn('pages');
    if (!book.turn('hasPage', page)) {
        var element = $('<div />',
            {'class': 'own-size',
                css: {width: 456, height: 333}
            }).
            html('<div class="loader"></div>');

        if (book.turn('addPage', element, page)) {
            loadPage(page);
        }
    }
}

function loadPage(page) {
    $.ajax({url: '../pages/page' + page + '.html'}).
        done(function(pageHtml) {
            $('.sj-book .p' + page).html(pageHtml);
        });
}