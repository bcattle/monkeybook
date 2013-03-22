import logging
logger = logging.getLogger(__name__)


class RankedPhotosMixin(object):
    """
    A mixin with a bunch of helper methods for dealing with
    models containing ranked lists of photos
    """
    _all_used_ids = None

    def num_unused_photos(self, photos):
        """
        Returns the number of photos in a list
        that are unused
        """
        unused = 0
        for photo in photos:
            if not self.photo_is_used(photo):
                unused += 1
        return unused

    def photo_is_used(self, photo, used_ids=None):
        """
        Iterates through all image index fields on the model,
        verifying that the images they refer to are not "claimed"
        """
        used_ids = used_ids or []
        photo_id = self._get_id_from_dict_or_int(photo)
        if photo_id in used_ids:
            return True
        all_used_ids = self._get_all_used_ids()
        return photo_id in all_used_ids

    def _get_all_used_ids(self):
        all_ids = []
        for ranked_list_name, yb_fields in self.lists_to_fields.iteritems():
            for yb_field in yb_fields:
                photo_id = self.get_photo_id_from_field_string(ranked_list_name, yb_field)
                if not photo_id is None:
                    all_ids.append(photo_id)
        return all_ids

    def get_n_unused_photos(self, list_of_photos, n, force_landscape=False, start_index=0):
        unused_photos = []
        used_ids = []
        while len(unused_photos) < n:
            if force_landscape:
                unused_photo = self.get_first_unused_photo_landscape(list_of_photos, used_ids, start_index)
            else:
                unused_photo = self.get_first_unused_photo(list_of_photos, used_ids, start_index)
            if unused_photo is None:
                # List ran out, return what we had
                return unused_photos
            else:
                unused_photos.append(unused_photo)
                used_ids.append(self._get_id_from_dict_or_int(list_of_photos[unused_photo]))
        return unused_photos

    def get_first_unused_photo(self, list_of_photos, used_ids=None, used_indices=None, start_index=0, return_id=False):
        """
        Loops through photos in `list_of_photos`,
        If no photo unused, return None
        """
        used_indices = used_indices or []
        for index, photo in enumerate(list_of_photos[start_index:]):
            if index in used_indices:
                continue
            if not self.photo_is_used(photo, used_ids):
                if return_id:
                    return index + start_index, self._get_id_from_dict_or_int(photo)
                return index + start_index
        if return_id:
            return None, None
        return None

    def get_first_unused_photo_landscape(self, list_of_photos, used_ids=None, start_index=0, return_id=False):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        *and* photo width is greater than its height.
        If no photo unused, return None
        """
        from voomza.apps.books_common.models import FacebookPhoto

        for index, photo in enumerate(list_of_photos[start_index:]):
            if not self.photo_is_used(photo, used_ids) and photo:
                # Is the photo landscape?
                if hasattr(photo, 'keys'):
                    if photo['width'] < photo['height']:
                        continue
                    if return_id:
                        return index + start_index, self._get_id_from_dict_or_int(photo)
                    return index + start_index
                else:
                    # Bummer, just an id - look it up in the database
                    try:
                        photo_db = FacebookPhoto.objects.get(facebook_id=photo)
                        if not photo_db.is_landscape():
                            continue
                    except FacebookPhoto.DoesNotExist:
                        logger.warn('Attempted to look up fb photo %d, doesn\'t exist in db.' % photo)
                        continue
                    if return_id:
                        return index + start_index, photo_db.facebook_id
                    return index + start_index
        if return_id:
            return None, None
        return None

    def get_first_unused_photo_portrait(self, list_of_photos, used_ids=None, start_index=0):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        *and* photo height is greater than its width.
        If no photo unused, return None
        """
        from voomza.apps.books_common.models import FacebookPhoto

        for index, photo in enumerate(list_of_photos[start_index:]):
            if not self.photo_is_used(photo, used_ids) and photo:
                # Is the photo landscape?
                if hasattr(photo, 'keys'):
                    if photo['width'] > photo['height']:
                        continue
                else:
                    # Bummer, just an id - look it up in the database
                    try:
                        photo_db = FacebookPhoto.objects.get(facebook_id=photo)
                        if not photo_db.is_portrait():
                            continue
                    except FacebookPhoto.DoesNotExist:
                        logger.warn('Attempted to look up fb photo %d, doesn\'t exist in db.' % photo)
                        continue
                return index + start_index
        return None

    def get_next_unused_photo(self, ranked_list_name, yb_field, unused_index=0, force_landscape=False):
        """
        Get the next unused photo in a list referred to by field name
        `unused_index` : returns the nth unused photo
        """
        photo_list = getattr(self.rankings, ranked_list_name)
        # Dereference the field, get the current index of the image being used
        curr_photo_index = self.get_photo_index_from_field_string(yb_field)
        # Get `unused_index` unused photos after that
        unused_photos = self.get_n_unused_photos(
            photo_list, unused_index + 1, force_landscape=force_landscape, start_index=curr_photo_index
        )
        # Return the last of these
        if unused_photos:
            return unused_photos[-1]
        else:
            return None

    def get_photo_index_from_field_string(self, yb_field):
        """
        Returns the index of the image being referred to by `yb_field`
        """
        if '.' in yb_field:
            # Double-indirection
            photo_list_index_field, photo_index_field = yb_field.split('.')
            photo_index = getattr(self, photo_index_field)
        else:
            photo_index = getattr(self, yb_field)
        return photo_index

    def get_photo_from_field_string(self, ranked_list_name, yb_field):
        """
        De-references and returns the photo struct of a photo referred
        to by a field in the PhotoRankings and a field in the Yearbook.
        Examples:       'family_with', 'family_photo_1'
                        'top_friends', 'top_friend_1.top_friend_1_photo_1'
        Returns None if photo list or index is empty
        """
        ranked_list = getattr(self.rankings, ranked_list_name)
        if ranked_list:
            if '.' in yb_field:
                # Double-indirection
                photo_list_index_field, photo_index_field = yb_field.split('.')
                photo_list_index = getattr(self, photo_list_index_field)
                photo_index = getattr(self, photo_index_field)
                if (not photo_list_index is None) and (not photo_index is None):
                    photo_list = ranked_list[photo_list_index]
                    # `photo_list` could be a list of structs, or integers
                    return  photo_list[photo_index]
            else:
                # Dereference the field back to the original facebook id
                list_index = getattr(self, yb_field)
                if not list_index is None:
                    # `ranked_list` is either a list of structs, or integers
                    return ranked_list[list_index]
        return None

    def get_photo_id_from_field_string(self, ranked_list_name, yb_field):
        """
        De-references and returns the *id* of the photo referred
        to by a field in the PhotoRankings and a field in the Yearbook.
        Examples:       'family_with', 'family_photo_1'
                        'top_friends', 'top_friend_1.top_friend_1_photo_1'
        Returns None if photo list or index is empty
        """
        photo = self.get_photo_from_field_string(ranked_list_name, yb_field)
        return self._get_id_from_dict_or_int(photo)

    def dump_to_console(self):
        """
            top_photos    (45 photos)
            -------------------
                            1120392001 (U)
            top_photo_1 --> 1120392001 (U)
                            1120392001
        """
        print('Yearbook for user <%s>\n' % self.rankings.user.username)
        single_indirect = [item for item in self.lists_to_fields.iteritems() if '.' not in item[1][0]]
        dbl_indirect = [item for item in self.lists_to_fields.iteritems() if '.' in item[1][0]]

        # Do single indirection first
        for ranked_list_name, yb_fields in single_indirect:
            ranked_list = getattr(self.rankings, ranked_list_name)
            self.dump_list(ranked_list_name, ranked_list, yb_fields)

        for ranked_list_name, yb_fields in dbl_indirect:
            ranked_list = getattr(self.rankings, ranked_list_name)
            fields_by_index_field = {}
            for yb_field in yb_fields:
                list_index_field_name, photo_field_name = yb_field.split('.')
                if list_index_field_name in fields_by_index_field:
                    fields_by_index_field[list_index_field_name].append(photo_field_name)
                else:
                    fields_by_index_field[list_index_field_name] = [photo_field_name]

            # Now have a list of photo fields by field index,
            # dump these
            for list_name, fields in fields_by_index_field.iteritems():
                sub_list_index = getattr(self, list_name)
                sub_list_name_str = '%s : %s --> %d' % (ranked_list_name, list_name, sub_list_index)
                self.dump_list(sub_list_name_str, ranked_list[sub_list_index], fields)
        print('\n')

    def dump_list(self, list_name, photo_list, list_fields):
        """
        `list_fields` -> the fields that point into the list
        """
        MAX_PHOTOS_PER_LIST = 25
        # Print the name of the ranking table
        print('%s\t(%d photos)\n%s' % (list_name, len(photo_list), '-'*(len(list_name) + 20)))
        # For each entry in the list, print
        # (1) whether it is pointed to by a field in `yb_fields`
        # (2) the ID, and (3) whether the ID is in use elsewhere
        longest_field = max([len(field) for field in list_fields])
        for index, photo in enumerate(photo_list):
            field_str = ' '*(longest_field + 4)
            # Is it pointed to from `yb_fields`?
            for field in list_fields:
                if self.get_photo_index_from_field_string(field) == index:
                    field_str = '%s -->' % field
                    break
                    # Is it in use in the yearbook?
            in_use_str = ''
            if self.photo_is_used(photo):
                in_use_str = '(U)'
            score_str = portrait_str = ''
            if hasattr(photo, 'keys'):
                if 'score' in photo:
                    score_str = photo['score']
                if 'width' in photo and 'height' in photo:
                    if photo['width'] < photo['height']:
                        portrait_str = 'Portrait'
            photo_str = '%s %s %s %s %s' % (field_str, str(self._get_id_from_dict_or_int(photo)).ljust(18), str(score_str).ljust(3), in_use_str, portrait_str)
            print(photo_str)

            if index >= MAX_PHOTOS_PER_LIST:
                print(' '*(longest_field + 4) + '  ...')
                break
        print('\n')

    def _get_id_from_dict_or_int(self, photo):
        # If it's a dict, try the key 'object_id', then try 'id'
        if hasattr(photo, 'keys'):
            if 'object_id' in photo:
                return photo['object_id']
            else:
                return photo['id']
        else:
            return photo

