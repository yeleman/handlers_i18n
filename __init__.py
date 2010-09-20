"""

BIG HACKS

We need to patch rapidsms to stop handling translation blindlessly and
unicode conversion with a hammer.

Until it's done, these hacks will try to make it work. We need to patch
RapidSMS ASAP for this.

"""

from functools import update_wrapper
from rapidsms.messages.incoming import OutgoingMessage

# need to rename the old method to avoid recursive calls    
OutgoingMessage._text = OutgoingMessage.text

def text(self, *args, **kwargs):
    """
        Add a reference to the message the current sms is a response to
    """
    try:
        return OutgoingMessage._text.fget(self, *args, **kwargs)
    except UnicodeDecodeError:
        return " ".join(self._render_part(tmpl, **kwargs) for tmpl, kwargs in self._parts)

OutgoingMessage.text = property(update_wrapper(text, OutgoingMessage._text.fget))

OutgoingMessage.render_part = OutgoingMessage._render_part

def _render_part(self, template, **kwargs):
    return template % kwargs
    
OutgoingMessage._render_part = update_wrapper(_render_part, OutgoingMessage.render_part)
