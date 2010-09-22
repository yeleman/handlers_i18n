#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

class ExitHandle(Exception):
    """
        Exception raised in a handle when you want to leave the method.
        
        If you pass a message, it will be sent as a response.
        
        I you pass carry_on = True, the phase won't be short circuited
    """
    
    def __init__(self, message='', carry_on=False):
        self.message = message
        self.carry_on = carry_on
        Exception.__init__(self, message)
