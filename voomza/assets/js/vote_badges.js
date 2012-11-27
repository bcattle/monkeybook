var loaded = false;
var pollTimer;
var emptyCount = 0
var TURN_OFF_AFTER = 8;
var dropped = false;


// Called when the user presses the "next" button,
// for example to move from the "family" to the
// "significant other" category
var badges = null;
var friendSelects = null;
var currentBadgeIndex = null;
var currentMaxTags = null;
var drop_zone;
var selectedFriends = new Object();
function setCurrentBadge(index) {
    if (index!=currentBadgeIndex) {
        if ($('.friend_selection').length) {
            // Store the currently-selected friend ids
            selectedFriends[currentBadgeIndex] = [];
            $('.friend_selection').each(function(){
                selectedFriends[currentBadgeIndex].push($(this).attr('data-id'));
            });
        }
        // Update the left-page indicator
        badges.removeClass('current');
        var currBadgeElement = $(badges[index]);
        currBadgeElement.addClass('current');
        // Update the message
        $('.badge_message_text').html(currBadgeElement.attr('data-message'));
        currentMaxTags = parseInt(currBadgeElement.attr('data-max-tags'));
        // Update the URL
        hash.add({b: index});
        // Clear the drop_zone
        drop_zone.empty();
        // Unhide any previously-selected users
        $('.selection').removeClass('selection');
        // Done
        currentBadgeIndex = index;
    }
}

// Called when user clicks X button or
// when another element is selected from the user list
// They could be clicking x on a multi select, so
// this should figure out what they did
function clearSelection() {
    // Clear div

    // Make all elements in list visible
    $('.selection').removeClass('selection');
}

// Called when the user chooses an element
function addToSelection(element) {
    // Insert new div into friend container
    var user_id = element.attr('data-id');
    var selected_html = Mustache.to_html(selectedFriendTemplate, friends_by_id[parseInt(user_id)]);
    $('.drop_zone').append(selected_html);

    // If there's a filter, clear it
    clearFilter();
}



var currOffset = 0;
var friends_by_id = new Object();
var friendTemplate = null;
var selectedFriendTemplate = null;
var friends_elements = null;
function onGetFriends(data) {
    friendsLoaded();
    // We might have gotten a duplicate dataset
    if (data.offset < currOffset)
        return;
    var friends = data.friends;
    if (friends.length) {
        // Dump the friends into the list div
        var list = $('.friends_list');
        _.each(friends, function(friend){
            var friend_html = Mustache.to_html(friendTemplate, friend);
            if (filter_on) {
                $(friend_html).hide();
            }
            list.append(friend_html);
            friends_by_id[friend.facebook_id] = friend;
        });

        // Used by typeahead
        friends_elements = $('.friend_container');
        // Make friend_containers draggable
        friends_elements.draggable({
            addClasses: false,
            helper: 'clone',
            appendTo: 'body',
            containment: 'document',
            opacity: 0.75,
            revert: 'invalid',
            scroll: false,
            zIndex: 100,
            start: function(event, ui) {
                dropped = false;
                $(this).hide();
            },
            stop: function(event, ui) {
                if (dropped==true) {
                    $(this).remove();
                } else {
                    $(this).show();
                }
            }
        });
        // Set the click handler
        friends_elements.click(function(){
            addToSelection(this);
        });
        // Set the hover action
        friends_elements.mouseenter(function(){
//            friends_elements.removeClass('selected_friend');
            $('.selected_friend').removeClass('selected_friend');
            $(this).addClass('selected_friend');

        });

        // Get another page of results
        currOffset += friends.length;
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
        var loaded = true;
        $('.loading').hide();
        $('.loaded').show();
    }
}

$(document).ready(function() {
    badges = $('.badge_container');
    friendSelects = $('.select_container');
    drop_zone = $('.drop_zone');
    // Set the current badge
    // If there's one in the url, use that
    if (hash.get('b')) {
        setCurrentBadge(hash.get('b').toString());
    } else {
        setCurrentBadge(0);
    }

    Dajaxice.setup({'default_exception_callback': friendsTimeout});
    // Get the first page of friends
    // we don't trust this function, so we keep calling it
    // to make sure new results didn't come into the server
    var get_friends = function() { Dajaxice.yearbook.get_friends(onGetFriends, {'offset': currOffset}); };
    get_friends();
    pollTimer = setInterval(get_friends, 1000);
    setTimeout(friendsTimeout, 10000);

    // Load templates
    Mustache.tags = ['[[', ']]'];
    friendTemplate = $('#friend_template').html();
    selectedFriendTemplate = $('#selected_friend_template').html();

    // Make the landing site droppable
    $('.drop_zone').droppable({
        hoverClass: 'drop_zone_hover',
        drop: function(event, ui) {
            dropped = true;
//            var dropped_id = $(ui.draggable[0]).attr('data-id');
            // Select the user
//            addToSelection(dropped_id);
            addToSelection($(ui.draggable[0]));
        }
    });

    $('#submit').click(nextBadge);
    $('#skip').click(nextBadge);
});

function nextBadge() {
    if (currentBadgeIndex == lastBadge) {
        // Collect the data and submit the form
        Dajaxice.yearbook.save_badge_votes(submitCallback, {
            'friend_ids': selected_ids
        });
    } else {
        setCurrentBadge(currentBadgeIndex + 1);
    }
}


function submitCallback(data) {
    // If everything worked, redirect to the next page
    top.location.href = data.next_url;
}


function friendsTimeout() {
    if (!loaded) {
        // Only run if the first call timed out
        // TODO: show an error message
    }
}

