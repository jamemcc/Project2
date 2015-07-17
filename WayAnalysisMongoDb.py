#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import xml.etree.cElementTree as ET
#from lxml import etree as ET
import pprint
import re
import codecs
import json
"""
transform OSM XML data into MONGODb importable structure for anlysis of WAY dataThe output is a list list of dictionaries in JSON format that will be importable with MongoImport 
 
uses a custom procedure to capture Street Prefix.  
 """

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
lower = re.compile(r'^([a-z]|_)*$') 
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$') 
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]') 


# Regular expression to find street type - last full word in the name
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# list of spanish Pre-types to look for
reverseTypes = ["Aquecia","Acequia","Arroyo","Avenida", "Caballo","Calle",
            "Callecita","Calleja","Callejon",
            "Caltamira","Cam","Camino","CAmino",
            "Caminito", "Campo", "Canada","Casa",
            "Cereza","Cii","Cli","Cll","Corrida","Corte",
            "Entrade","Estrasa","Estrada",
            "Hacienda","La","Las","Loma","Monte",
            "Parque","Pasaje", "Paso","Paseo","Placita","Plaza","Plazuela","Pueblo",
            "Puerto","Ristra", "Ruta", 
            "Senda","Sendero","Sentiero", "Sierra", "Tierra",
            "Valle","Vereda","Via","Viale","Viejo","Vis","vis","Vista","Vuelta"]

# list of 2 word types to look for
twoWordTypes = ["County Road","El Camino","State Route"]

# list of street names to fix
mapping = { "Ave":"Avenue",
            "Blvd":"Boulevard",
            "Caltamira":"Calle Altimira Court",
            "Cam":"Camino",
            "CAmino ":"Camino",
            "Cereza":"Plaza Rojo",
            "Cii":"Calle",
            "Cli":"Calle",
            "Cll":"Calle",
            "DR ":"Drive",
            "Dr":"Drive",
            "Entrade":"Entrada",
            "Ln":"Lane",
            "Paso":"Paseo",
            "Rd":"Road",
            "Ristra":"Ristra Plaza",
            "St": "Street",
            "Vis":"Via",
            "vis":"Vista",
            }
fixed = 0

def update_name(name, mapping):
    # This function looks up a passed in street type and replaces it with one from the array called mapping
    global fixed
    if name in mapping:
        fixed = fixed + 1
        print ("{} - found : {}, replaced with: {}").format(fixed,name,mapping[name])
        name = name.replace(name, mapping[name])
    return name

def determineStreetType(street_name):
    # function takes a street name and first splits it into words so it can test
    # the first word and then the first and second words befre finally finding 
    # the last word using a regular expresion all done to  determines it's 
    # street type and then populates a group variable "street types"
    # which groups all the street names by street type
    SpanishInd = False
    nameWords = street_name.split()
    #print allNameWords 
    if nameWords[0] in ["E","East","N","North","S","South","W","West"]:
        del nameWords[0] 
    if len(nameWords)> 2 and nameWords[1] in ["de","del","a"]:   
        street_type = nameWords[0]
        SpanishInd = True
    elif len(nameWords)> 0 and nameWords[0] in reverseTypes:
        street_type = nameWords[0]
        SpanishInd = True
    elif len(nameWords)> 2 and nameWords[0] + ' ' +nameWords[1] in twoWordTypes:
        street_type = nameWords[0] + ' ' + nameWords[1]
    else: 
        m = street_type_re.search(street_name)
        if m:
            street_type = m.group()
        else:
            street_type = ""
        #if you just need a list of unexpected streets uncomment the following
        #if street_type not in expected:
    # take the street type and look it up and replace it if found in mapping array
    better_name = update_name(street_type, mapping)
    return(better_name, SpanishInd)


def shape_element(element,file_in):
    # function takes in an Open street maps XML element and determines if it is a
    # Way Node and if so transforms it into a MongoDb formatted output.
    node = {}
    # process only top level tag: "way"
    if element.tag == "way":
        # Set up temporary containers for desired pieces of the Way to extract
        node['file'] = file_in
        node['type'] = element.tag
        lat=float(0)
        lon=float(0)
        addrBuild={}
        ndref = []
        refExists = True
        created = {}
        for name, value in element.attrib.items():
            # loop through all name value pairs in the topmost way element to find 
            # user/created info

            # print '{0}="{1}"'.format(name, value)
            # -attributes for latitude and longitude should be added to a "pos" array, 
            if name == "lat":
                lat=float(value);
            elif name == "lon":
                lon=float(value);
            #- attributes in the CREATED array should be added under a key "created" 
            elif name == "version" or name == "changeset" or name == "timestamp" or name   == "user" or name == "uid":
                created[name] = value

            else: node[name] = value
        if lon !=0 and lat !=0: node['pos'] = [lat,lon]
        node["created"] = created

        # load the entire way element into an eTree heirarchy Dictionary
        tree = ET.ElementTree(element)
        #print ET.tostring(tree, pretty_print = True)
        # find the root of the heirarchy so you can iterate through the tags within
        root = tree.getroot()
        for child_of_element in root:
            # decompose heirarchy of the element and find and decompose
            #  the actual address info
            addrExists = False
            labelExists = False
            namefound = False
            refCount = 0
            for name, value in child_of_element.attrib.items():
                # go through each name value pair amalgamating name and tiger data
                #print ("Name is {}, Value is {}").format(name,value)
                if name == 'k':
                    if problemchars.search( value) is not None: continue;
                    #- if "k" value contains problematic characters, it should 
                    # be ignored
                    elif lower_colon.match( value) is not None:
                        #- if "k" value contains ":", it should has good data to store though the good key is what comes after the colon
                        addrPiece = value.split(':')
                        if addrPiece[0] == 'tiger' and len(addrPiece) == 2 and addrPiece[1] != "name":
                            # use tiger: tags as address info except if it's a repeat of name           
                            addrExists = True
                            label = addrPiece[1]

                    else: 
                        # for all other (single tag) keys save their value
                        label = value
                        addrExists = True
                  
                elif name == 'v' and addrExists:
                    labelExists = True
                    addrBuild[label] = value
                    # look for an build street types and spanish type indicator
                    if label == "name":
                        streetType, spanishInd = determineStreetType(value)
                        #print("for {}, found type {} and Spanish Indicator {}").format(value, streetType,spanishInd)
                        addrBuild["streetType"] = streetType
                        addrBuild["spanishInd"] = spanishInd

                    #print addrBuild
                elif name == 'ref':
                    """- for "way" specifically:<nd ref
                        should be turned into "node_refs": ["305896090", "1719825889"]
                    """
                    if not refExists:
                        refExists = True
                    #print("found name ref, with value= {}").format(value)
                    ndref.append(value)
                    refCount += refCount
            if refExists: 
                node['node_refs'] = ndref; 
                node['refCount'] = refCount;
        if labelExists: node['address'] = addrBuild;
        #return node
    elif element.tag == "node":
        # Set up temporary containers for desired pieces of the Way to extract
        node['file'] = file_in
        node['type'] = element.tag
        created = {}
        for name, value in element.attrib.items():
            # loop through all name value pairs in the topmost way element to find 
            # user/created info

            # print '{0}="{1}"'.format(name, value)
            # -attributes for latitude and longitude should be added to a "pos" array, 
            if name == "lat":
                lat=float(value);
            elif name == "lon":
                lon=float(value);
            #- attributes in the CREATED array should be added under a key "created" 
            elif name == "version" or name == "changeset" or name == "timestamp" or name   == "user" or name == "uid":
                created[name] = value

            else: node[name] = value
        if lon !=0 and lat !=0: node['pos'] = [lat,lon]
        node["created"] = created

        return node
    else:
        return None

def process_map(file_in, pretty = False):
    # go through the specifed file_in and process it
    file_out = "{0}.json".format(file_in)
    data = []
    x=2
    with codecs.open(file_out, "w") as fo:
        print "1"
        for _, element in ET.iterparse(file_in, events=('end',)):
            el = shape_element(element,file_in)
            if el:
                #data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
                """element.clear()
                for ancestor in element.xpath('ancestor-or-self::*'):
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]
                """
            else:
                """
                for ancestor in element.xpath('ancestor-or-self::*'):
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]
                """
            if (x % 100000) == 0:  print ("moving on to element {}").format(x)
            x+=1
    return data

def test():
# NOTE: if you are running this code on your computer, with a larger dataset,  
# call the process_map procedure with pretty=False. The pretty=True option adds  
# additional spaces to the output, making it significantly larger. 
    process_map('los-angeles_california.osm', False)
    process_map('OakPark.osm', False)
    process_map('LosAlamos.osm', False)
    process_map('santafe.osm', False)


if __name__ == "__main__":
    test()
