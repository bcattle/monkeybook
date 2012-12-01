var loaded = false;
var friendTemplate = null;
var checkedAttr = 'checked="checked"';
var friendsList = null;
var selectNoneWasClicked = false;

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function onGetFriends(data, textStatus, jqXHR) {
    nextFriendsUrl = data.meta.next;
    // Get the next page of results, if we need to
    // We pull the lesser of `max_invites` or their number of friends
    var friends_so_far = data.meta.offset + data.objects.length;
    if (friends_so_far < max_invites && nextFriendsUrl) {
        $.ajax(nextFriendsUrl);
    }

    // Dump the friends into the list
    var friends = data.objects;
    var friend_element;
    _.each(friends, function(friend) {
        if (!selectNoneWasClicked) {
            // Show the users with checkbox checked
            friend.checked = checkedAttr;
        }
        // All divs are injected hidden
        friend_element = $(Mustache.to_html(friendTemplate, friend))
            .hide().appendTo(friendsList);
        // Add a callback to show after the image has loaded
        friend_element.imagesLoaded(function(){
            this.addClass('friend');
            if (!filterActive) {
                this.fadeIn(500);
            }
        });
        // Add a callback, clicking element changes checkbox
        addCheckboxClickCallback(friend_element);
    });

    // Show the loaded page, if needed
    friendsLoaded();
}

function addCheckboxClickCallback(el) {
    el.click(function(e){
        if (!$(e.target).is(':checkbox')) {
            var checkbox = $(this).find(':checkbox');
            checkbox.attr('checked', !checkbox.is(':checked'));
            checkbox.change();
        }
    });
}

function onGetFriendsError(jqXHR, textStatus, errorThrown) {
    if (!loaded) {
        // Only run if the first call timed out
        console.log('ajax error');
        //TODO: show an error message
    }
}

function friendsLoaded() {
    if (!loaded) {
        loaded = true;
        $('.loading').hide();
        $('.loaded').show();
    }
}

var max_invites = 50;
$(document).ready(function() {
    friendsList = $('.friends_list');

    // How many invites can we send?
    // Pull this number of top friends by default
    if ($.browser.msie) {
        max_invites = 25;
    }

    // Set up ajax
    $.ajaxSetup({
        success: onGetFriends,
        error: onGetFriendsError
    });

    // Get the first page of friends
//    $.ajax(nextFriendsUrl);

    // Load template
    Mustache.tags = ['[[', ']]'];
    friendTemplate = $('#friend_template').html();


    $('#selectNone').click(function() {
        $('.friends_list input').removeAttr('checked');
        selectNoneWasClicked = true;
        });

    $('#selectAll').click(function() {
        $('.friends_list input').attr('checked', 'checked');
        selectNoneWasClicked = false;
    });

    $('.list').scroll(function(e) {
        // If we're near the bottom, the typeahead filter isn't active,
        // we don't already have a pending request, and there is another page to load
        if (this.scrollTop > .8 * this.scrollHeight
                && !filterActive && !$.active && nextFriendsUrl) {
            // Load the next page of results
            $.ajax(nextFriendsUrl);
        }
    });

    $('#submit').click(function() {
        var selected_ids = $('.friends_list input:checked').map(function(){
        return $(this).attr("value");
        }).get();
        if (selected_ids.length) {
            // Show the invites dialog
            FB.ui({method: 'apprequests',
                to: selected_ids.slice(0,max_invites).toString(),
                title: 'My Great Invite',
                message: 'Check out this Awesome App!'
            }, fbSubmitCallback);
        } else {
            // Just redirect to the next page
            top.location.href = nextUrl;
        }
    });
});

function fbSubmitCallback(data) {
    // If this came back from facebook, it contains 'request' (an id)
    // and 'to' an array of user ids. save these to db

    var patch_objects = [];
    _.each(data.to, function(to_id){
        patch_objects.push({
            request_id: data.request,
            facebook_user_id: to_id
        });
    });
    var patch_data = {
        objects: patch_objects,
        deleted_objects: []
    };

    $.ajax({
        url: invitesSentUrl,
        type: 'PATCH',
        data: JSON.stringify(patch_data),
        contentType: 'application/json',
        dataType: 'json',
        processData: false,
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        },
        // Fix to allow ie to do PATCH (http://stackoverflow.com/a/12785714/1161906)
        xhr: function() {
            return window.XMLHttpRequest == null || new window.XMLHttpRequest().addEventListener == null
                ? new window.ActiveXObject("Microsoft.XMLHTTP")
                : $.ajaxSettings.xhr();
        },
        success: function() {},
        error: function() {},
//        error: function(jqXHR, textStatus, errorThrown) {
//            console.log('error');
//        },
        complete: function(){
            // Whether or not it worked, go on to next page
            top.location.href = nextUrl;
        }
    });
}
