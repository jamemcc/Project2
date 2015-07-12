#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
"""
Code template provided by Udacity.  Assigned task was to explore the data a bit more.
check the "k" value for each "<tag>" and see if they can be valid keys in MongoDB,
as well as see if there are any other potential problems.

We have provided you with 3 regular expressions to check for certain patterns
in the tags. As we saw in the quiz earlier, we would like to change the data model
and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with problematic characters.

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    # function is passed an XML element.  it is expected these elements would come from
    # xml.etree.ElementTree and it;'s iterparse function but could come from other 
    # similar decomposition.   It will pass back (and thus continuosly build) a counter 
    # of the type of key it finds.
    # The logic of this function checks to see if the element passed in is a key.  If it 
    # is it runs a check using regular expressions to determine the key type. 
    if element.tag == "tag":
        # YOUR CODE HERE
        #ET.dump(element)
        if 'k' in element.attrib:
            if problemchars.search( element.attrib['k']) is not None: keys['problemchars'] +=1;   
            elif lower_colon.match( element.attrib['k']) is not None: keys['lower_colon'] +=1   
            elif lower.match( element.attrib['k']) is not None: keys['lower'] +=1   
            else:keys['other'] +=1
    return keys



def process_map(filename):
    # set counters to 0 and then loop through an XML file using xml.etree.ElementTree
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



def test(filename):
    # process a file and when done print out filename and the count of key types 
    # found in that file
    keys = process_map(filename)
    print ("========= {} ========").format(filename)
    pprint.pprint(keys)


if __name__ == "__main__":
    # process files in a row so the output can be dumped to CSV and later compared
    test('santafe.osm')
    test('LosAlamos.osm')    
    test('OakPark.osm')
