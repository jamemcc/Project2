#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use iterative parsing to process an OpenSrteetMaps XML file to count
what tags are there.  Results determine how much of 
which data you can expect to have in the map.
The output is a dictionary with the tag name as the key
and number of times this tag can be encountered in the map as value.
"""
import xml.etree.ElementTree as ET
import pprint

 
def count_tags(filename):
    # for given filename loop through each element counting the type of tag.
    show = 0 
    findCnt=0 
    elementTagsDict = {}
    for event, element in ET.iterparse(filename,events=("start","end")): 
        if show == 1:  
            print '"1 event = {0}, element = {1}'.format(event, element) 
            ET.dump(element) 
        if event == "end": continue
        if element.tag in elementTagsDict: 
             elementTagsDict[element.tag] += 1
        else: elementTagsDict[element.tag] = 1
    return elementTagsDict

def test():
    # processs each desired OSM file
    tags = count_tags('OakPark.osm')
    pprint.pprint(tags)

if __name__ == "__main__":
    test()
