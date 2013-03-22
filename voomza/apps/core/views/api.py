from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response


# TODO: could have a url here that redirects to
# /api/user/34325151/ of the currently-logged-in user
# then shows views accordingly from there

# @api_view(['GET'])
# def api_root(request, format=None):
#     """
#     The entry endpoint of our API.
#     """
#     return Response({
#         'friends': reverse('friend-list', request=request),
#         'friends-inapp': reverse('invite-list', request=request),
#         'friends-notinapp': reverse('invite-list', request=request),
#         'friends-books': reverse('invite-list', request=request),
#     })


@api_view(['GET'])
def task_progress(request, task_name, format=None):
    """
    This view looks for a task in the current session
    with the specified name, and returns its status
    """
    raise NotImplementedError
    return Response({ })

