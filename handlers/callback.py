#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


import sys
import traceback

from django.utils import translation
from django.conf import settings

from base import BaseHandler
from rapidsms.conf import settings

from ..exceptions import ExitHandle

class CallbackHandler(BaseHandler):

    """
    This handler type can be subclassed to create callback handler, meaning
    it is going to valid wether this is handler is going to be called or not
    by providing a fonction that must return True or False.

        >>> class AbcHandler(CallbackHandler):
        ...    def match(self):
        ...        return self.message.startswth("I love you")
        ...
        ...    def handle(self, text, keyword, language):
        ...        self.respond(u"Me too")

    If the match() method returns True, it responds::

        >>> AbcHandler.test("I love you")
        [u'Me too.']


    All other messages are silently ignored (as usual), to allow other
    apps or handlers to catch them.
    
    """

    @classmethod
    def match(cls, msg):
        """
            You must implement this method youself. It must return something. If
            its boolean value is True, the SMS will be handled by this class.
            
            Handle() will be called with match() returned value
            as a parameter
            
        """
        raise NotImplementedError()


    @classmethod
    def dispatch(cls, router, msg):
        # filter message
        match = cls.match(msg)
        if not match:
            return False

        # todo: set the translation in an i18n app.
        contact = msg.connection.contact
        django_lang_bak = translation.get_language()
        if contact:
            translation.activate(contact.language)

        # todo make this part something common among all handlers        
        # excute handle
        ret = None
        try:
            # spawn an instance of this handler, and stash
            # the low(er)-level router and message object
            inst = cls(router, msg)

            # if any non-whitespace content was send after the keyword, send
            # it along to the handle method. the instance can always find
            # the original text via self.msg if it really needs it.
            # if we received _just_ the keyword, with
            # no content, some help should be sent back
            ret = inst.handle(match)
                
        except ExitHandle as exit:
        
            if exit.message:
                inst.respond(exit.message)
            if not exit.carry_on:
                return True
                
        except Exception as e:
            err, detail, tb = sys.exc_info()
            print err, detail
            traceback.print_tb(tb)
            
        # set back language to the original one
        finally:
        
            translation.activate(django_lang_bak)

            return ret if ret is not None else True
        
        

        

