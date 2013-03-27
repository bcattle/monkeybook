var friendBookTemplate, friendBookList;

function onGetFriendsBooks(data, textStatus, jqXHR) {
    var nextUrl = data.meta.next;

    // If something, call the next url
    if (false)
        $.ajax(nextUrl);

    _.each(data.objects, function(book) {
        var book_element = $(Mustache.to_html(friendBookTemplate, book).trim())
            .hide().appendTo(friendBookList);

        book_element.imagesLoaded(function(){
//            this.fadeIn(500);
            this.show("scale", {}, 500);
        });
    });

}

function onGetFriendsBooksError(jqXHR, textStatus, errorThrown) {

}

$(document).ready(function() {
    // Load friends' books from the server and populate

    // Get the first page of friends
    $.ajaxSetup({
        success: onGetFriendsBooks,
        error: onGetFriendsBooksError
    });
    $.ajax(friendsBooksUrl);

    // Load template
    friendBookTemplate = $('#friend_book_template').html();
    friendBookList = $();
});
