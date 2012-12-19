//var edit_row_template;

//$(document).ready(function(){
//    edit_row_template = $('#edit_row_template').html();
//    Mustache.tags = ['[[', ']]'];
//});

//function doPage(page) {
//    // Attach an edit row div to every image on the page
//    $('.p' + page).find('photo').each(function(index, value){
//        var data = {'page': page, 'index': index};
//        $(Mustache.to_html(edit_row_template, data)).appendTo(this);
//    });
//
//    // Register click handlers
//}

function registerNextPrevClickHandlers() {
    $('nextButton').click(function(){
        onNextPrevButtonClick(true);
    });
    $('prevButton').click(function(){
        onNextPrevButtonClick(false);
    });
}

function onNextPrevButtonClick(isNext) {
    // .data('page')    .data('index')
    console.log(isNext);
}