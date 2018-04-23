import json
f = open('mapped_data_reviews.txt','r')
f_write = open("mapped_data_users","w")

counter=0
for i in f:
    print(counter)
    counter=counter+1
    loaded_json = json.loads(i)
    user = {}
    user["userName"] = loaded_json["reviewerName"] if "reviewerName" in loaded_json else ""
    user["userID"] = loaded_json["reviewerID"]
    print(json.dumps(user))
    f_write.write(json.dumps(user)+'\n')
