"""
This routine will count up and then list the Ways found in an Open street maps 
XML dataset

"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "OakPark.osm"
# Regular expression to find street type - last full word in the name
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

reverseTypes = ["Aquecia","Acequia","Arroyo","Avenida", "Caballo","Calle",
            "Callecita","Calleja","Callejon", "Camino",
            "Caminito", "Campo", "Canada","Casa","Corrida","Corte",
            "Entrade","Estrasa","Estrada",
            "Hacienda","La","Las","Loma","Monte",
            "Parque","Pasaje", "Paseo","Placita","Plaza","Plazuela","Pueblo",
            "Puerto","Ruta", 
            "Senda","Sendero","Sentiero", "Sierra", "Tierra",
            "Valle","Vereda","Via","Viale","Viejo","Vis","Vista","Vuelta"]

twoWordTypes = ["County Road","El Camino","State Route"]


def audit_street_type(street_types, street_name):
    # function takes a street name and first splits it into words so it can test
    # the first word and then the first and second words befre finally finding 
    # the last word using a regular expresion all done to  determines it's 
    # street type and then populates a group variable "street types"
    # which groups all the street names by street type
    nameWords = street_name.split()
    #print allNameWords 
    if nameWords[0] in ["E","East","N","North","S","South","W","West"]:
        del nameWords[0] 
    if len(nameWords)> 2 and nameWords[1] in ["de","del","a"]:   
        street_type = nameWords[0] + ' ' + nameWords[1]
    elif len(nameWords)> 0 and nameWords[0] in reverseTypes:
        street_type = nameWords[0]
    elif len(nameWords)> 2 and nameWords[0] + ' ' +nameWords[1] in twoWordTypes:
        street_type = nameWords[0] + ' ' + nameWords[1]
    else: 
        m = street_type_re.search(street_name)
        if m:
            street_type = m.group()
        #if you just need a list of unexpected streets uncomment the following
        #if street_type not in expected:
    street_types[street_type].add(street_name)


def is_street_name(elem):
    # return boolean true or false if the key is addr:street
    return (elem.attrib['k'] == "name")


def audit(osmfile):
    # loop through an OSM file looking for all tags named node or way and then inside
    # those looping through all tags looking for one with K=addr:street 
    # (the street name tag) and with it calling the funciton which can count it.
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def test():
    # call routine to pull out all street types grouped and then print the results
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    """ next section count the street types"""
    for st_type, ways in st_types.iteritems():
        countways = 0
        if st_type in reverseTypes: reverseMarker = "yes"
        else:  reverseMarker = "no"
        for name in ways:
            countways +=1
        print st_type, ",", countways, ",", reverseMarker
    

    """for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "West Lexington St.":
                assert better_name == "West Lexington Street"
            if name == "Baldwin Rd.":
                assert better_name == "Baldwin Road"
    """

if __name__ == '__main__':
    test()
