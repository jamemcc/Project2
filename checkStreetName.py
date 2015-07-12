"""
Template provided as part of Udacity Class
Program Summarizes all found street names by street type.  it is intended to be used as exploratory audit of any OSM file as regarding the number and street types found in that area.
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "santa-fe_new-mexico.osm"

# Regular expression to find street type - last full word in the name
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

def audit_street_type(street_types, street_name):
    # function takes a street name and using a regular expresion determines it's 
    # street type and then populates a group variable "street types"
    # which groups all the street names by street type
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        #if you just need a list of unexpected streets uncomment the following
        #if street_type not in expected:
        street_types[street_type].add(street_name)


def is_street_name(elem):
    # return boolean true or false if the key is addr:street
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    # loop through an OSM file looking for all tags named node or way and then inside
    # those looping through all tags looking for one with K=addr:street 
    # (the street name tag) and with it calling the funciton which can count it.
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def test():
    # call routine to pull out all street types grouped and then print the results
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))

 
if __name__ == '__main__':
    test()
