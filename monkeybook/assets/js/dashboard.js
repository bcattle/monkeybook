var friendBookTemplate, friendBookList;

function onGetFriendsBooks(data, textStatus, jqXHR) {
    // Get the next page of results, if any
    var nextUrl = data.meta.next;
    if (nextUrl)
        $.ajax(nextUrl);

    if (!data.objects.length) {
        $('#no_friend_books').show();
    } else {
        var lastId;
        _.each(data.objects, function(book) {
            // We may get more than one book per person
            // reject any users we've already seen
            if (book.fb_id == lastId)
                return;
            lastId = book.fb_id;
            var book_element = $(Mustache.to_html(friendBookTemplate, book).trim())
                .hide().appendTo(friendBookList);

            book_element.imagesLoaded(function(){
                this.fadeIn(500);
//            this.show("scale", {}, 500);
            });
        });
    }

    // Fire an event
    $(document).trigger('friendsBooksLoaded', data.objects.length);
}

function onGetFriendsBooksError(jqXHR, textStatus, errorThrown) {
    $(document).trigger('friendsBooksLoaded', {'count': 0});
}

$(document).ready(function() {
    // Load template
    friendBookTemplate = $('#friend_book_template').html();
    friendBookList = $('.friend-books');

    // Load friends' books from the server and populate
    $.ajaxSetup({
        success: onGetFriendsBooks,
        error: onGetFriendsBooksError
    });
    $.ajax(friendsBooksUrl);
});
