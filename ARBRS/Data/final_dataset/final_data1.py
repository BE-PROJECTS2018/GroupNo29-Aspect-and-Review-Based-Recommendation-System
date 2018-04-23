import json

f_product = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data.txt","r")
# f = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data.txt","w")
f_review = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data_reviews.txt","w")
count = 1
count_reviews=0
for i in f_product:
    loaded_json = json.loads(i)
    print(loaded_json.keys())
    for i in loaded_json["reviews"]:
        f_review.write(json.dumps(i))
        f_review.write('\n')
    # f.write(json.dumps(loaded_json))
    # f.write('\n')
    print(count)
    count+=1
