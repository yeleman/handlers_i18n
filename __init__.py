"""

BIG HACKS

We need to patch rapidsms to stop handling translation blindlessly and
unicode conversion with a hammer.

Until it's done, these hacks will try to make it work. We need to patch
RapidSMS ASAP for this.

"""

from functools import update_wrapper

from django.db import models

from rapidsms.messages.incoming import OutgoingMessage
from rapidsms.models import ConnectionBase, Contact

# need to rename the old method to avoid recursive calls    
OutgoingMessage._text = OutgoingMessage.text

def text(self, *args, **kwargs):
    """
        Remove unicode conversion from the method
    """
    try:
        return OutgoingMessage._text.fget(self, *args, **kwargs)
    except UnicodeDecodeError:
        return " ".join(self._render_part(tmpl, **kwargs) for tmpl, kwargs in self._parts)

OutgoingMessage.text = property(update_wrapper(text, OutgoingMessage._text.fget))

OutgoingMessage.render_part = OutgoingMessage._render_part

def _render_part(self, template, **kwargs):
    """
        Remove translation from the method
    """
    return template % kwargs
    
OutgoingMessage._render_part = update_wrapper(_render_part, OutgoingMessage.render_part)

# forbid connection without a user
ConnectionBase.contact  = models.ForeignKey(Contact)

