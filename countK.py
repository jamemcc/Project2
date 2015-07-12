#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
from collections import *
"""
Processes an Open Street Maps OSM file.  Counts the number of each type of K tag within a quality classification for the K tag values.  the classifications are;

 problem characters- key's with characters that should not be in a key
 lower colon - key's with a all lower case and a colon - these look like good key values
 lower - keys with only letters and all lower case - these look like good key categories
 other - keys with upper case and otherwise don't look too god like the ones above
"""


# regular expressions to search for
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# counters used to gather the values and counts found in each category
lower_colonKcount= Counter()
lowerKcount = Counter()
problemKcount = Counter()
otherKcount = Counter()

def key_type(element, keys):
    # function processes a given elemnt of XML looking to see if it's a tag with K values 
    # in it.  when found it evaluates the K value using regular expressions and other
    # criteria to determine what category that K value is in and then enummerates it in 
    # that category in 2 ways: counting it by category and then counting it by k value 
    # in category.
    if element.tag == "tag":
        #ET.dump(element)
        if 'k' in element.attrib:
            #print (element.attrib['k'])
            if problemchars.search( element.attrib['k']) is not None: 
                keys['problemchars'] +=1;   
                problemKcount[element.attrib['k']] += 1;
            elif lower_colon.match( element.attrib['k']) is not None: 
                keys['lower_colon'] +=1  
                lower_colonKcount[element.attrib['k']] += 1; 
            elif lower.match( element.attrib['k']) is not None: 
                keys['lower'] +=1;
                lowerKcount[element.attrib['k']] += 1; 
            else:
                keys['other'] +=1
                # next line may not work depending on the characters found
                #otherKcount[element.attrib['k']] += 1;
    return keys

def process_map(filename):
    # set up a counter and then loop through the given XML file processing each element
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys



def test(filename):
    # process each file given and then print out the result in the 5 categories
    lowerKcount = Counter()
    lower_colonKcount= Counter()
    problemKcount = Counter()
    otherKcount = Counter()
    keys = process_map(filename)
    print "===== {} ====================".format(filename)
    print "----- Problem Characters in Tags found are:{}".format(keys['problemchars'])
    pprint.pprint(problemKcount)
    print "----- Seemingly Valid Compound Tags found are:{}".format(keys['lower_colon'])
    pprint.pprint(lower_colonKcount)
    print "----- Normal Tags found are:{}".format(keys['lower'])
    pprint.pprint(lowerKcount)
    print "----- Other (strange) tags found are:{}".format(keys['other'])
    pprint.pprint(otherKcount)
otherKcount=[]


if __name__ == "__main__":
    # process all needed OSm files 
    test("santafe.osm")
    test("LosAlamos.osm")
    test("OakPark.osm")

