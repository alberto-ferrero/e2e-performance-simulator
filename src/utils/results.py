#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

class AppResult:
    def __init__ (self, code : int, result):
      self.code: int = code
      self.result: dict = result
      self.error: bool = False if code == 200 else True
      #Manage error
      if self.error:
        raise Exception('ERROR: failed due to "{}", error code {}'.format(self.result, self.code))

# -*- coding: utf-8 -*-