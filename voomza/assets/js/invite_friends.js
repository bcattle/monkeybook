var loaded = false;
var currOffset = 0;
var friendTemplateChecked = null;
var friendTemplateUnchecked = null;
var pollTimer;
var emptyCount = 0
var TURN_OFF_AFTER = 8;
var friends_elements = null;
var selectNoneWasClicked = false;

function onGetFriends(data) {
    friendsLoaded();
    // We might have gotten a duplicate dataset
    if (data.offset < currOffset)
    return;
    var friends = data.friends;
    if (friends.length) {
//        console.log('Got friends, starting id ' + friends[0].facebook_id);
        // Dump the friends into the list
        var list = $('.friends_list');
        for (var idx in friends) {
            if (selectNoneWasClicked) {
                // Show the users with checkbox empty
                list.append(Mustache.to_html(friendTemplateUnchecked, friends[idx]));
            } else {
                list.append(Mustache.to_html(friendTemplateChecked, friends[idx]));
            }
        }
        // Update list of friend elements
        friends_elements = $('.friend');
        // Get another page of results
        currOffset += friends.length;
        //                console.log('Offset now ' + currOffset);
        Dajaxice.yearbook.get_friends(onGetFriends, {'offset': currOffset});
    } else {
        emptyCount++;
        if (emptyCount > TURN_OFF_AFTER) {
            // Turn off polling for new results
            clearInterval(pollTimer);
        }
    }
}

function friendsLoaded() {
    if (!loaded) {
    loaded = true;
    $('.loading').hide();
    $('.loaded').show();
    }
}

$(document).ready(function() {
    Dajaxice.setup({'default_exception_callback': friendsTimeout});
    // Get the first page of friends
    // we don't trust this function, so we keep calling it to make sure
    // new results didn't come into the server
    var get_friends = function() { Dajaxice.yearbook.get_friends(onGetFriends, {'offset': currOffset}); };
    get_friends();
    //            pollTimer = setInterval(get_friends, 1000);
    //            setTimeout(friendsTimeout, 10000);

    // Load template
    Mustache.tags = ['[[', ']]'];
    friendTemplateChecked = $('#friend_template_checked').html();
    friendTemplateUnchecked = $('#friend_template_unchecked').html();

    $('#selectNone').click(function() {
        $('.friends_list input').removeAttr('checked');
        selectNoneWasClicked = true;
        });

    $('#selectAll').click(function() {
        $('.friends_list input').attr('checked', 'checked');
        selectNoneWasClicked = false;
    });

    $('#submit').click(function() {
        var selected_ids = $('.friends_list input:checked').map(function(){
        return $(this).attr("value");
        }).get();
        if (selected_ids.length) {
            // Show the invites dialog
            var max_invites = 50;
            if ($.browser.msie) {
                max_invites = 25;
            }
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

function friendsTimeout() {
    if (!loaded) {
    alert('Dajaxice exception');

    // Only run if the first call timed out
    //TODO: show an error message
    }
}

function fbSubmitCallback(data) {
    // If this came back from facebook, it contains 'request' (an id)
    // and 'to' an array of user ids. save these to db
    Dajaxice.yearbook.invites_sent(dbSubmitCallback, {
        'request_id': data.request,
        'friend_ids': data.to
    });
}

function dbSubmitCallback(data) {
    top.location.href = data.next_url;
}
