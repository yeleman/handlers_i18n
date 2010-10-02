#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

import datetime

from django.utils.translation import ugettext as _

from handlers_i18n.exceptions import ExitHandle

def require_args(args, min=None, max=None, slices=()):
    """
        Exits if the number of arguments does not match the requirement.
        
        Slices expect a iterable of items like:
        - an int
        - an tuple of boundaries that will be passed to xrange
        
        If len(args) matches one item of slices, the test passes. e.g.:
        
        (2, (4, 7), 9) would pass with 2, 4, 5, 6, 7, 9  
    """

    count = len(args)
    if min and count < min:
        raise ExitHandle(_(u'This command expects at least %(min)s value(s). '\
                           u'You provided %(args_number)s.') % {
                           'min': min, 'args_number': count} )
                           
    if max and count > max:
        raise ExitHandle(_(u'This command expects %(max)s value(s) maximum. '\
                           u'You provided %(args_number)s.') % {
                           'max': max, 'args_number': count} )

    if range:
        # checking the range
        for x in slices:
            try:
                if count in xrange(*x):
                    return
            except TypeError:
                if x == count:
                    return
                    
        # building a string for range in error message        
        args_range = set()
        for x in slices:
            try:
                args_range.update(xrange(*x))
            except TypeError:
                args_range.add(x)
        
        args_range = sorted(list(str(x) for x in args_range))
        if len(args_range) > 1:
            args_range = _('%(ranges)s or %(range)s') % {
                          'ranges': ', '.join(args_range[:-1]), 
                          'range': args_range[-1]}
        else:
            args_range = args_range.pop()            
        
        raise ExitHandle(_(u'This command expects %(range)s value(s). You '\
                          u'provided %(args_number)s.') % {'range': args_range,
                                                         'args_number': count})
        

def check_date(date_str, date_format, remove_separators=()):
    """
        Check is the date has the right format and return a date object.
        Otherwise, exist the handle.
    """
    
    translate_table = dict((ord(c), None) for c in remove_separators)
    date_str = date_str.translate(translate_table)

    try:
        return datetime.datetime.strptime(date_str, date_format)
    except ValueError:
        raise ExitHandle(_(u"%(date_str)s is not a valid date. "\
                           u"The expected date format is: %(format)s") % {
                           'date_str': date_str, 'format':date_format })
                               


def check_exists(code, model, field_code='code'):
    """
        Exit the handle if the objects does not exists.
        
        If it does, returns it.
        
        Code field must have a unique constraint and a verbose name for it to work.
    """
    
    try:
        obj = model.objects.get(**{field_code:code})
    except model.DoesNotExist:
        obj_name = unicode(model._meta.verbose_name)
        field_name = unicode(model._meta.get_field_by_name(field_code)[0].verbose_name)
        raise ExitHandle(_(u"No %(obj_name)s with %(field_name)s '%(code)s' "\
                           u"exists. Ask your administrator the right "\
                           u"%(field_name)s for your %(obj_name)s.") % {
                           'obj_name': _(obj_name), 'field_name':_(field_name), 
                           'code': code})
                               
    return obj                 
