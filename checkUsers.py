#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
from collections import * 
"""
Skelton of this routine provided by Udacity class. This program determines how many unique users
have contributed to an OSM map's data in this particular area of that map
"""

def get_user(element):
    # given an XML element if that element seems to have a userid in it "uid"
    # give back the user name value from that same element.
    if 'uid' in element.attrib:
        #ET.dump(element)
        return element.attrib['user']
    return


def process_map(filename):
    # routine looks in the inputted OSM file and loops through the file looking at each   
    # tag and counts up the users it finds.
    # updated below from original DA class code which just showed the name
    # to a Counter to give better data (how many) versus just the user names.
    users = Counter()
    for _, element in ET.iterparse(filename):
        users[get_user(element)] += 1

    print 'Found {0} user in {1}'.format(len(users),filename)
    return users


def test():
    # goes through files and print out result
    userCount = Counter()
    users = process_map('santafe.osm')
    pprint.pprint(users)
    users = process_map('LosAlamos.osm')
    pprint.pprint(users)
    users = process_map('OakPark.osm')
    pprint.pprint(users)



if __name__ == "__main__":
    test()
