#!/usr/bin/env python
"""
Use PyMongo to query and summarize Way data across counties looking for the Spanish indicator metric
"""

def range_query():
    # Your code here
    #query = {"foundingDate" : {"$gte": datetime(2001,1,1)}}
    query = {'address.county': 'Santa Fe, NM', 'address.streetType': 'Camino'}
    return query
def get_db():
    # For local use
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.osm
    return db


""" Use this mainline to do raw query of data using query defined in function range_query
    if __name__ == "__main__":
    # For local use
    db = get_db()
    query = range_query()
    result = db.ways.find(query)
    print "Found ways:", result.count()
    import pprint
    pprint.pprint(result[0])
"""

def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [
        {"$group":
            {
                "_id":
                    {"county":"$address.county","spanishInd":"$address.spanishInd"},
                "hwCount":{"$sum":1}
            }
        },
        { "$sort": 
            { "hwCount": -1 } 
        },
        { "$group": 
            { 
                "_id": "$_id.county", "spanishInds": 
                    { "$push": 
                        { "aSpanishInd": "$_id.spanishInd", "count": "$hwCount" }, 
                    }
            }
        },
        { "$sort": 
            { "count": 1 } 
        }
    ]
    return pipeline

def tweet_sources(db, pipeline):
    result = db.ways.aggregate(pipeline)
    return result

if __name__ == '__main__':
    db = get_db()
    pipeline = make_pipeline()
    result = tweet_sources(db, pipeline)
    import pprint
    pprint.pprint(result)

