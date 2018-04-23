from preprocessed.models import Product, Review, User, Category_Mapping
import json
#

# Loading Product
# Inserting Data into Database

counter=0
f = open('/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data.txt','r')
for i in f:
    counter=counter+1
    print("Product : "+str(counter))
    loaded_json = json.loads(i)
    a = Product()
    a.asin = loaded_json["asin"]
    a.title = loaded_json["title"] if "title" in loaded_json else ""
    # a.price = loaded_json["price"] if "price" in loaded_json else 0
    a.description = loaded_json["description"] if "description" in loaded_json else ""
    a.imUrl = loaded_json["imUrl"] if "imUrl" in loaded_json else ""
    a.categories = loaded_json["categories"] if "categories" in loaded_json else ""
    # a.brand = loaded_json["brand"] if "brand" in loaded_json else ""
    # a.salesRank = loaded_json["salesRank"] if "salesRank" in loaded_json else ""
    # a.also_viewed = loaded_json["related"]["also_viewed"] if "related" in loaded_json else ""
    a.buy_after_viewing = loaded_json["buy_after_viewing"] if "buy_after_viewing" in loaded_json else ""
    a.save()

# # Loading Category_Mapping (?????)
# counter = 0
# f = open('/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data.txt','r')
# products = Product.objects.all()
# l = []
# for i in f:
#     loaded_json = json.loads(i)
#     for i in loaded_json["categories"]:
#         l.append(i)
# categories = list(set(l))
#
# for i in categories:
#     a = Category_Mapping()
#     a.category = i
#     a.save()
#
# f = open('/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data.txt','r')
# for i in f:
#     loaded_json = json.loads(i)
#     for j in loaded_json["categories"]:
#         a = Category_Mapping.objects.get(category=j)
#         # print(str(a.products))
#         c = str(a.products).replace(" ", "")
#         print(c)
#         if c == "":
#             l = []
#             l.append(loaded_json["asin"])
#             a.products = str(l)
#             a.save()
#         else:
#             get_list = eval(str(a.products))
#             get_list.append(loaded_json["asin"])
#             a.products = str(get_list)
#             a.save()
#         a.products = str(eval(a.products).append(loaded_json["asin"]))
#         a.save()

# Loading User
# Inserting Data into Database
counter=1
f = open('/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data_users','r')
for i in f:
    print(counter)
    counter=counter+1
    loaded_json = json.loads(i)
    a = User()
    a.userID = loaded_json["userID"]
    a.userName = loaded_json["userName"] if "userName" in loaded_json else ""
    a.searchWords = loaded_json["searchWords"] if "searchWords" in loaded_json else ""
    a.save()
#
# Loading Review
# Inserting Data into Database
counter=0
f = open('/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/mapped_data.txt','r')
for i in f:
    counter = counter + 1
    print("Review : " + str(counter))
    load = json.loads(i)
    tempAsin = load["asin"]
    array = load["reviews"]
    # print(array)
    for loaded_json in array:

        a = Review()
        b = Product.objects.get(asin=tempAsin)
        c = User.objects.get(userID=loaded_json["reviewerID"])
        a.asin = b
        a.reviewerID = c
        a.reviewText = loaded_json["reviewText"] if "reviewText" in loaded_json else ""
        if "helpful" in loaded_json:
            b = loaded_json["helpful"]
            a.helpful = b[0]
            a.notHelpful = b[1]
        else:
            a.helpful = 0
            b.notHelpful = 0
        a.overall = loaded_json["overall"] if "overall" in loaded_json else 0
        a.summary = loaded_json["summary"] if "summary" in loaded_json else ""
        # a.unixReviewTime = loaded_json["unixReviewTime"] if "unixReviewTime" in loaded_json else ""
        a.reviewTime = loaded_json["reviewTime"] if "reviewTime" in loaded_json else ""
        a.save()
        # print(c)
