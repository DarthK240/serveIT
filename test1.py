import firebase_admin
from firebase_admin import db
from firebase_admin import credentials, firestore
import json
from google.cloud.firestore_v1 import GeoPoint
from datetime import datetime

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()

class FirestoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GeoPoint):
            return {'latitude': obj.latitude, 'longitude': obj.longitude}
        elif isinstance(obj, datetime):
            # Convert the Firestore timestamp to a datetime object and serialize
            return obj.isoformat()
        return super().default(obj)

# Gathering specific Document IDs for donors
specific_donor = "customer"
consolidated_data1 = []
collection_refA = db.collection(specific_donor)
document_idsA = [doc.id for doc in collection_refA.stream()]

# Gathering specific Document IDs for teen drivers
specific_teen = "teendriver"
consolidated_data2 = []
collection_refB = db.collection(specific_teen)
document_idsB = [doc.id for doc in collection_refB.stream()]

# Function for gathering data from Documents
def my_function(collection_name, document_id, result_list, persona):
    # Reference to a specific document
    doc_ref = db.collection(collection_name).document(document_id)
    # Get the document snapshot
    doc_snapshot = doc_ref.get()
    # Check if the document exists
    if doc_snapshot.exists:
        # Access the document data
        doc_data = doc_snapshot.to_dict()
        if persona=='customer':
            hardcode_values = {'serviceDuration':1200.000000000, 'vehicle':None, 'previousCustomer':None, 'nextCustomer': None,
                                'arrivalTime':None, 'startServiceTime':None, 'departureTime':None,
                                'drivingTimeSecondsFromPreviousStandstill': None}
            doc_data.update(hardcode_values)

        if persona=='teendriver':

            hardcode_values = {'customers':[], 'totalDemand':0, 'totalDrivingTimeSeconds':0}
            doc_data.update(hardcode_values)

        #print("Document data:", doc_data)
        result_list.append(doc_data)
        #return(result_list)

# Donor Code
for document_id in document_idsA:
    my_function(specific_donor, document_id, consolidated_data1, 'customer')

# Teen Code
for document_id in document_idsB:
    my_function(specific_teen, document_id, consolidated_data2, 'teendriver')

donor_file_path = "/Users/darthkrishnan/serveit/consolidated_donor_data.json"
teen_file_path = "/Users/darthkrishnan/serveit/consolidated_teen_data.json"

static_di = {"name": "demo","southWestCorner": [36.044659, -80.244217], "northEastCorner": [36.099861,-79.766235],
            "startDateTime": "2024-01-31T07:30:00", "endDateTime": "2024-02-01T00:00:00", "depots": [{
            "id": "1", "location": [36.08500988379876,-80.12924492296452]}, {"id": "2", "location": [
            36.079845716714175, -79.98111801941987]}]}

# Save the dictionary with GeoPoint to a JSON file using the custom encoder
with open(donor_file_path, 'w') as json_file:
    json.dump(consolidated_data1, json_file, indent=2, cls=FirestoreEncoder)

with open(teen_file_path, 'w') as json_file:
    json.dump(consolidated_data2, json_file, indent=2, cls=FirestoreEncoder)

donor_dictionary = json.load("/Users/darthkrishnan/serveit/consolidated_donor_data.json")
teen_dictionary = json.load("/Users/darthkrishnan/serveit/consolidated_teen_data.json")


'''
# Merge both large .json files
json_files = ["consolidated_donor_data.json", "consolidated_teen_data.json"]
python_objects = []
for json_file in json_files:
    with open(json_file, "r") as f:
        python_objects.append(json.load(f))

# Dump all the Python objects into a single JSON file.
with open("combined.json", "w") as f:
    json.dump(python_objects, f, indent=4)
'''
