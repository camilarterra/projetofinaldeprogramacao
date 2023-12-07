import pymongo

class data_list:
    def __init__ (self, user, commentsData, issueNumber):
        self.user = user
        self.commentsData = commentsData
        self.issueNumber = issueNumber
        self.firstResultData = ""
        self.firstResultProbability = 0
        self.secondResultData = ""
        self.secondResultProbability = 0

# Creating a connetiong to the MongoDB server to get the data
connectionDB = pymongo.MongoClient("mongodb://localhost:27017/")

# Selecting the database with the results data
gzip_classification_db = connectionDB['gzip_Classification']

# Making the query the database to get the data
gzip_classification_collection = gzip_classification_db['Result']

# MongoDB query to get all unique "Issue Number" values
unique_issue_numbers = gzip_classification_collection.distinct("Issue Number")


# Selecting the database with the metrics data
metrics_db = connectionDB['conductor']

# Making the query the database to get the data
metrics_collection = metrics_db['metrics']


# Selecting the database to save metrics and results data
metrics_and_results_collection = gzip_classification_db['metrics_and_results']
metrics_and_results_collection.drop()

for issue_number in unique_issue_numbers:
    metrics_document = metrics_collection.find_one({"issue_number": issue_number})
    results_documents = list(gzip_classification_collection.find({"Issue Number": issue_number}))

    metrics_document["results"] = results_documents

    keys = ["what", "who", "why", "where", "when", "how", "how_much"]
    counts = {key: (0, 0) for key in keys}

    for result in results_documents:
        first_result = result["First Result"]
        counts[first_result] = (counts[first_result][0] + 1, counts[first_result][1])

        second_result = result["Second Result"]
        if second_result != None:
            counts[second_result] = (counts[second_result][0], counts[second_result][1] + 1)
    metrics_document["result_counts"] = counts

    # Printing the results
    metrics_and_results_collection.insert_one(metrics_document)

connectionDB.close()
