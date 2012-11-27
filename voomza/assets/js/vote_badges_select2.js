var friendSelect = null;
var loaded = false;
var pollTimer;
var emptyCount = 0
var TURN_OFF_AFTER = 8;
var currOffset = 0;
var selectedByBadge = [];

function makeSelectBox() {
    // Initialize the element using select2
    friendSelect.select2({
        placeholder: 'Type to search for a friend',
        maximumSelectionSize: currentMaxTags,
        width: '300px'
    });
//    friendSelect.select2('open');
}

function onGetFriends(data) {
    friendsLoaded();
    // We might have gotten a duplicate dataset
    if (data.offset < currOffset)
        return;
    var friends = data.friends;
    if (friends.length) {
        // Add the friends to the select
        _.each(friends, function(friend){
            friendSelect.append('<option value="' + friend.facebook_id + '">'
                + friend.name + '</option>');
        });

        // Update select box
        makeSelectBox();

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
    // Set the current badge
    // If there's one in the url, use that
//    var get_b = parseInt(hash.get('b'));
//    if (!isNaN(get_b) && get_b < lastBadge) {
//        setCurrentBadge(get_b);
//    } else {
//        setCurrentBadge(0);
//    }
    friendSelect = $('#friendSelect');
    setCurrentBadge(0);

    Dajaxice.setup({'default_exception_callback': friendsTimeout});
    // Get the first page of friends
    // we don't trust this function, so we keep calling it
    // to make sure new results didn't come into the server
    var get_friends = function() { Dajaxice.yearbook.get_friends(onGetFriends, {'offset': currOffset}); };
    get_friends();
    pollTimer = setInterval(get_friends, 1000);
    setTimeout(friendsTimeout, 10000);

    $('#submit').click(nextBadge);
    $('#skip').click(skipBadge);
});

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

// Called when the user presses the "next" button,
// for example to move from the "family" to the
// "significant other" category
var badges = null;
var currentBadgeIndex = null;
var currentMaxTags = null;
function setCurrentBadge(index) {
    if (index!=currentBadgeIndex) {
        // Update the left-page indicator
        badges.removeClass('current');
        var currBadgeElement = $(badges[index]);
        currBadgeElement.addClass('current');
        // Update the message
        $('.badge_message_text').html(currBadgeElement.data('message'));
        currentMaxTags = parseInt(currBadgeElement.data('max-tags'));
        // Re-initialize the select2 with the currentMaxTags
        makeSelectBox();
        // Done
        currentBadgeIndex = index;
    }
}

function nextBadge() {
    // Store the current selections
    selectedByBadge.push(friendSelect.select2('val'));
    if (currentBadgeIndex == lastBadge) {
        // Collect the data and submit the form
        Dajaxice.yearbook.save_badge_votes(submitCallback, {
            'selected_friends': selectedByBadge
        });
    } else {
        // Clear and show next badge
        friendSelect.select2('val', '');
        setCurrentBadge(currentBadgeIndex + 1);
    }
}

function skipBadge() {
    // Clear the current selection
    friendSelect.select2('val', '');
    nextBadge();
}
