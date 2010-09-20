#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils import translation
from django.conf import settings

from rapidsms.contrib.handlers.handlers.base import BaseHandler
from rapidsms.conf import settings
from rapidsms.models import Contact

class KeywordHandlerI18n(BaseHandler):

    """
    This handler type can be subclassed to create keyword-based
    handlers with i18n. When a message is received, it is checked against the
    mandatory ``keyword`` attribute for a prefix
    match then for aliases (in the same or other languages). For example::

        >>> class AbcHandler(KeywordHandler):
        ...    keyword = "hello"
        ...    aliases = { 'fr-fr': ['bonjour']}
        ...    def help(self, keyword, language):
        ...        self.respond(_("Here is some help."))
        ...
        ...    def handle(self, text, keyword, language):
        ...        self.respond(_("You said: %s.") % text)

    If the keyword is matched and followed by some text, the ``handle``
    method is called::

        >>> AbcHandler.test("Hello")
        ['Here is some help.']

    If *just* the keyword is matched, the ``help`` method is called::

        >>> AbcHandler.test("bonjour mec")
        ['Vous avez dit: mec.']

    All other messages are silently ignored (as usual), to allow other
    apps or handlers to catch them.
    
    You can choose to set the local automatically or not by setting 
    AUTO_SET_LANG
    
    Keywords are case insensitive and are striped before comparison.
    
    'Keyword' will be used as the keyword for the default language code.
    
    """
    
    
    AUTO_SET_LANG = True
    _duplicate_aliases = set()
    
    
    @classmethod
    def _clean_keyword(cls, keyword):
        """
            Returns a keyword lowercase with no spaces around it.
        """
        return keyword.lower().strip()

    
    @classmethod
    def keywords(cls):
        """
            Return a mapping between all accepted keywords and a language code.
        """
        # try to get data from the cache first
        try:
            return cls._keywords_cache
        except AttributeError:
            duplicate_counter = {}
            try:
                # default keyword
                kw = cls._clean_keyword(cls.keyword)
                kw_mapping = {kw: settings.LANGUAGE_CODE}
            except AttributeError:
                return {}
            else:   
                # add aliases for the same language and other ones
                try:
                    for lang_code, aliases_list in cls.aliases:
                        for alias in aliases_list:
                            kw = cls._clean_keyword(alias)
                            duplicate_counter[kw] = duplicate_counter.get(kw, 0) + 1
                            kw_mapping[kw] = lang_code
                except AttributeError:
                    pass
        
        # create a list for duplicate keywords for which we will never force
        # the lang 
        for kw, count in duplicate_counter.iteritems():
            if count > 1:
                 cls._duplicate_aliases.add(kw)
        cls._keywords_cache = kw_mapping # set the cache
        
        return kw_mapping


    @classmethod
    def _match(cls, msg):
        """
            Check is a message match one of the keywords and return the 
            keyword and the language code.
        """
        
        text = msg.text
        lang_code = settings.LANGUAGE_CODE
        keyword = None

        if text:     
            splitted_text = msg.text.split(None, 1) + [None] 
            first_word = cls._clean_keyword(splitted_text.pop(0))
            try:
                keywords = cls.keywords()
                if first_word not in cls._duplicate_aliases:
                    lang_code = keywords[first_word]
                return (first_word, lang_code, splitted_text.pop(0))
            except KeyError:
                pass
            
        return keyword, lang_code, splitted_text.pop(0)


    @classmethod
    def dispatch(cls, router, msg):

        # filter message
        keyword, lang_code, text = cls._match(msg)
        if not keyword or not lang_code:
            return False

        # activate language
        contact = msg.connection.contact
        django_lang_bak = translation.get_language()
        if contact:
            if cls.AUTO_SET_LANG:
                contact_lang_bak = None
                contact.language = lang_code
                translation.activate(lang_code)
            else:
                translation.activate(contact.language)
        else:
            translation.activate(lang_code)
        
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
            if text:
                ret = inst.handle(text, keyword, lang_code)
            else:
                ret = inst.help(keyword, lang_code)
        # set back language to the original one
        finally:
            if cls.AUTO_SET_LANG:
                contact_lang_bak = None
                if contact_lang_bak:
                    contact.language = contact_lang_bak
                translation.activate(django_lang_bak)
        
		    if ret is not None:
		         return ret
		    
		    return True
        
        

        

