// Adds pages to the yearbook based on html files in a directory

function getPage(page) {
    $.ajax({url: 'sample_pages/page' + page + '.html'}).
        done(function(pageHtml) {
            $('.sj-book .p' + page).html(pageHtml);
        });
}