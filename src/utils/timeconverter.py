#! /usr/bin/env python3

# Copyright (C)
# Author: alberto-ferrero

""""
Collection of methods to convert UTC time.
"""

from datetime import datetime, timezone
from datetime import timezone

UTC = timezone.utc

def getTimestampFromDate(date: str) -> int:
        """ Convert date into utctimestamp [millis] """
        dateList = date.split(".")
        dateList[-1] = dateList[-1].split("Z")[0]
        if len(dateList) == 1:
            dateList.append("000")
        if len(dateList[-1]) > 4:
            dateList[-1] = dateList[-1][:4] 
        date = ".".join(dateList) + "Z"
        return int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC).timestamp() * 1000)

def getDateFromTimestamp(ts: int) -> str:
        """ Convert utctimestamp [millis] to date """
        return datetime.utcfromtimestamp(ts / 1000.0).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def getDatetimeFromDate(date: str) -> datetime:
        """ Convert utctimestamp [millis] to date """
        dateList = date.split(".")
        dateList[-1] = dateList[-1].split("Z")[0]
        if len(dateList) == 1:
            dateList.append("000")
        if len(dateList[-1]) > 4:
            dateList[-1] = dateList[-1][:4] 
        date = ".".join(dateList) + "Z"
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)

# -*- coding: utf-8 -*-