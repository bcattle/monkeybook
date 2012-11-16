from django.db import models

class DefaultUnicodeBase(models.Model):
    """
    Stolen from django_facebook
    """
    def __unicode__(self):
        """
        Looks at some common ORM naming standards and tries to display those before
        default to the django default
        """
        attributes = ['name', 'title', 'slug']
        name = None
        for a in attributes:
            if hasattr(self, a):
                name = getattr(self, a)
        if not name:
            name = repr(self.__class__)
        return name

    def __repr__(self):
        return '<%s[%s]>' % (self.__class__.__name__, self.pk)

    class Meta:
        abstract = True
