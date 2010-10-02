#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
module_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_HANDLERS = ()
EXCLUDED_HANDLERS = (module_name + '.handlers.base.BaseHandler',
                     module_name + '.handlers.callback.CallbackHandler',
                     module_name + '.handlers.keyword.KeywordHandler',
                     module_name + '.handlers.keyword.PatternHandler')
