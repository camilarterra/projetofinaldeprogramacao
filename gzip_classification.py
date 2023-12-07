import gzip # font: Jiang, Z., Yang, M. Y., Tsirlin, M., Tang, R., & Lin, J. (2022). Less is More: Parameter-Free Text Classification with Gzip. arXiv preprint arXiv:2212.09410.
import json
import pymongo
import numpy as np # font: Jiang, Z., Yang, M. Y., Tsirlin, M., Tang, R., & Lin, J. (2022). Less is More: Parameter-Free Text Classification with Gzip. arXiv preprint arXiv:2212.09410.

#creating a class for the the data extraction
class SelectedData:
    def __init__ (self, user, commentsData, issueNumber):
        self.user = user
        self.commentsData = commentsData
        self.issueNumber = issueNumber



#creating a class for the bd data
class BDData:
    def __init__ (self, user, commentsData, issueNumber):
        self.user = user
        self.commentsData = commentsData
        self.issueNumber = issueNumber
        self.firstResultData = ""
        self.firstResultProbability = 0
        self.secondResultData = ""
        self.secondResultProbability = 0

    def resultK1(self, firstResultData, firstResultProbability):
        self.firstResultData = firstResultData
        self.firstResultProbability = firstResultProbability

    def resultK2(self, secondResultData, secondResultProbability):
        self.secondResultData = secondResultData
        self.secondResultProbability = secondResultProbability

    def printResults (self):
        print(f"\nUser: {self.user}")
        print(f"\nComments: {self.commentsData}")
        print(f"\nIssue Number: {self.issueNumber}")
        print(f"\nfirst Result Data: {self.firstResultData}")
        print(f"\nprob first Result Data: {self.firstResultProbability}")
        print(f"\nsecond Result Data: {self.secondResultData}")
        print(f"\nprob second Result Data: {self.secondResultProbability}")
        print(f"\n\n*******************\n\n")


# Creating a connetiong to the MongoDB server to get the data
connetionGet = pymongo.MongoClient("mongodb://localhost:27017/")

# Selecting the database with the data
databaseGet = connetionGet['conductor']

# Making the query the database to get the data
collectionGet = databaseGet['comments']

# Making the query for documents
results = collectionGet.find({})

#declaring a list of the class FinalData
list_SelectedData = []

# Making the selection for necessary data
for document in results:
    user = document["user"]["type"]
    commentsData = document["body"]
    issueNumber = document["issue_number"]
    if  "## Pull Request Test Coverage Report for" not in commentsData:
        selected_Data = SelectedData(user, commentsData, issueNumber)
        list_SelectedData.append(selected_Data)

num_lista1 = len(list_SelectedData)
print(f"tamanho lista 1: {num_lista1}")

list_SelectedDataFilter1 = []

for i in range(len(list_SelectedData)):
    user = list_SelectedData[i].user
    commentsData = list_SelectedData[i].commentsData
    issueNumber = list_SelectedData[i].issueNumber
    if  "?" in commentsData:
        selected_Data = SelectedData(user, commentsData, issueNumber)
        list_SelectedDataFilter1.append(selected_Data)


num_lista2 = len(list_SelectedDataFilter1)
print(f"tamanho lista 2: {num_lista2}")


list_SelectedDataFilter2= []

#filter the data that have "user" = "User" and saving in the list list_BDData2
for i in range(len(list_SelectedDataFilter1)):
    if list_SelectedDataFilter1[i].user == "User":
        user = list_SelectedDataFilter1[i].user
        commentsData = list_SelectedDataFilter1[i].commentsData
        issueNumber = list_SelectedDataFilter1[i].issueNumber
        selected_Data = SelectedData(user, commentsData, issueNumber)
        list_SelectedDataFilter2.append(selected_Data)

num_lista3 = len(list_SelectedDataFilter2)
print(f"tamanho lista 3: {num_lista3}")

# Closing the MongoDB connection
connetionGet.close()

resultData = []

for i in range(len(list_SelectedDataFilter2)):
    user = list_SelectedDataFilter2[i].user
    commentsData = list_SelectedDataFilter2[i].commentsData
    issueNumber = list_SelectedDataFilter2[i].issueNumber
    bd_data = BDData(user, commentsData, issueNumber)
    resultData.append(bd_data)

#training with the examples and definitions found in literature
training_set = []
with open('examples.json', 'r') as f:
    data = json.load(f)
    data_dict = dict(data)
    for label, examples in data_dict.items():
        training_set += [(example, label) for example in examples]

test_set = [(bd_data.commentsData, -1) for bd_data in resultData]
print(f"testset: {len(test_set)}")

# start adapted of font: Jiang, Z., Yang, M. Y., Tsirlin, M., Tang, R., & Lin, J. (2022). Less is More: Parameter-Free Text Classification with Gzip. arXiv preprint arXiv:2212.09410.
def gzip_text_classification(training_set, test_set, k):
    training_set = np.array(training_set)
    test_set = np.array(test_set)
    pred_test_set = []
    
    for (x1, _) in test_set:
        Cx1 = len(gzip.compress(x1.encode()))
        distance_from_x1 = []
        for (x2, _) in training_set:
            Cx2 = len(gzip.compress(x2.encode()))
            x1x2 = " ".join([x1, x2])
            Cx1x2 = len(gzip.compress(x1x2.encode()))
            ncd = (Cx1x2 - min(Cx1, Cx2)) / max(Cx1, Cx2)
            distance_from_x1.append(ncd)
        
        sorted_idx = np.argsort(np.array(distance_from_x1))
        top_k_class = list(training_set[sorted_idx[:k], 1])

        unique_values, counts = np.unique(top_k_class, return_counts=True)
        relative_frequencies = counts / len(top_k_class)

        soft_prediction = {classname: 0 for classname in unique_values}
        for i, classname in enumerate(unique_values):
            soft_prediction[classname] = relative_frequencies[i]

        sorted_classes = sorted(soft_prediction.items(), key=lambda item: item[1], reverse=True)
        first_class, first_prob = sorted_classes[0]
        second_class, second_prob = sorted_classes[1] if len(sorted_classes) > 1 else (None, 0)

        pred_test_set.append((x1, first_class, first_prob, second_class, second_prob))
    return pred_test_set
# end adapted of font: Jiang, Z., Yang, M. Y., Tsirlin, M., Tang, R., & Lin, J. (2022). Less is More: Parameter-Free Text Classification with Gzip. arXiv preprint arXiv:2212.09410.

# K=1 -> parameter for KNN
K = 3
count = 0
pred_test = gzip_text_classification(training_set, test_set, K)

for i, (commentsData, first_class, first_prob, second_class, second_prob) in enumerate(pred_test):
    resultData[i].resultK1(first_class, first_prob)
    resultData[i].resultK2(second_class, second_prob)

# Creating a connetiong to the MongoDB server to save the data
connetionSave = pymongo.MongoClient("mongodb://localhost:27017/")

# Selecting the database to save
databaseSave = connetionSave['gzip_Classification']

# Making the query of the database to save
collectionSave = databaseSave['Result']

#looping for saving the result, and show data
for i, (commentsData, first_class, first_prob, second_class, second_prob) in enumerate(pred_test):
    resultData[i].resultK1(first_class, first_prob)
    resultData[i].resultK2(second_class, second_prob)

#sorting data
resultData.sort(key=lambda x: x.issueNumber)

for bd_data in resultData:
    print(f"Number: {count}")
    bd_data.printResults()
    count +=1

# Loop to setting the data for database
for bd_data in resultData:
    docSave = {
        "User": bd_data.user,
        "Comments": bd_data.commentsData,
        "Issue Number": bd_data.issueNumber,
        "First Result": bd_data.firstResultData,
        "First Result Probability": bd_data.firstResultProbability,
        "Second Result": bd_data.secondResultData,
        "Second Result Probability": bd_data.secondResultProbability
    }

    # inserting the data in the database
    collectionSave.insert_one(docSave)

issue_numbers = []

for bd_data in resultData:
    issue_numbers.append(bd_data.issueNumber)


issue_number_unique = sorted(list(set(issue_numbers)))

print("************")
num_lista2 = len(resultData)
print(f"tamanho lista 3: {num_lista2}")

print("************")
print("Numeros das issues analisadas:")
count = 1
for number in issue_number_unique:
    print(str(count)+": "+ str(number))
    count += 1

