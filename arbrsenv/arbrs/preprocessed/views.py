from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Product, Review, User ,UserProfile, Product_Asp_Sent, Category_Mapping, Recommendation, Admin
from time import strftime,gmtime
import time
import json
import nltk
import math
import re
import string
from pycorenlp import StanfordCoreNLP
from textblob import TextBlob
from nltk.corpus import wordnet
import unicodedata
import asp_sent_rules as rules
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


nlp = StanfordCoreNLP('http://localhost:9000')


def index(request):
    return render(request,'preprocessed/index.html')

def products(request):
    a = Product.objects.all()
    context = { "products" : a }
    return render(request, 'preprocessed/product/product_index.html',context)

def productById(request,product_id):
    a = Product.objects.get(asin=product_id)
    b = a.review_set.all().filter(isConsidered=True)
    c = User.objects.all()
    # try:
    d = json.dumps(Product_Asp_Sent.objects.get(asin=product_id).aspects)
    #
    e = UserProfile.objects.filter(asin=product_id)
    battery = [0,0,0]
    camera = [0,0,0]
    display = [0,0,0]
    processor = [0,0,0]
    overall = [0,0,0]
    for i in e:
        loaded_json = json.loads(i.asp_sent_dictionary)
        if loaded_json["battery"] > 2.5 :
            battery[0]+=1
        elif loaded_json["battery"] == 2.5:
            battery[1]+=1
        elif loaded_json["battery"] < 2.5:
            battery[2]+=1

        if loaded_json["camera"] > 2.5 :
            camera[0]+=1
        elif loaded_json["camera"] == 2.5:
            camera[1]+=1
        elif loaded_json["camera"] < 2.5:
            camera[2]+=1

        if loaded_json["display"] > 2.5 :
            display[0]+=1
        elif loaded_json["display"] == 2.5:
            display[1]+=1
        elif loaded_json["display"] < 2.5:
            display[2]+=1

        if loaded_json["processor"] > 2.5 :
            processor[0]+=1
        elif loaded_json["processor"] == 2.5:
            processor[1]+=1
        elif loaded_json["processor"] < 2.5:
            processor[2]+=1

        if loaded_json["overall"] > 2.5 :
            overall[0]+=1
        elif loaded_json["overall"] == 2.5:
            overall[1]+=1
        elif loaded_json["overall"] < 2.5:
            overall[2]+=1


    context = {"product": a, "reviews": b, "users": c, "product_asp_sent": d, "battery":battery, "camera":camera,"display":display, "processor":processor,"overall":overall}
# except:
    #     context = { "product" : a, "reviews" :b, "users" :c }
    return render(request,'preprocessed/product/product.html',context)

def users(request):
    a = User.objects.all()
    context = {"users": a }
    return render(request,'preprocessed/user/user_index.html',context)

def userById(request,user_id):
    a = User.objects.get(userID=user_id)
    b = a.review_set.all()
    c = UserProfile.objects.filter(userID=user_id)
    recommendation_status = Admin.objects.get(admin_user="tejas1106").recommendation_status
    if recommendation_status:
        recommendation(a.userID)
        try:
            recommendations = Recommendation.objects.filter(userID=a)

            # recommended_products
            r_products = [i.asin for i in recommendations]
            titles = []
            battery = []
            camera = []
            display = []
            processor = []
            overall = []

            for i in r_products:
                k = Product_Asp_Sent.objects.get(asin=i)
                titles.append(k.asin.title)
                t = k.aspects
                battery.append(json.loads(t)["asp_sent"]["battery"]["rating"])
                camera.append(json.loads(t)["asp_sent"]["camera"]["rating"])
                display.append(json.loads(t)["asp_sent"]["display"]["rating"])
                processor.append(json.loads(t)["asp_sent"]["processor"]["rating"])
                # camera.append(json.loads(t)["asp_sent"]["battery"]["rating"])

            # make array of array
            smart_array = json.dumps(
                {"titles": titles, "battery": battery, "camera": camera, "display": display, "processor": processor})

            # print(d)
            context = {"reviews": b, "user": a, "userprofile": c, "recommendations": recommendations,
                       "smart_array": smart_array}
        except:
            context = {"reviews": b, "user": a, "userprofile": c}
    else:
        context = {"reviews": b, "user": a, "userprofile": c}
    return render(request, 'preprocessed/user/user.html',context)

def admin(request):
    a = User.objects.all()
    b = Product.objects.all()
    c = Admin.objects.get(admin_user="tejas1106").recommendation_status
    context = {"users": a, "products": b, "recommendation_status":c}
    return render(request,'preprocessed/admin/admin.html',context)


def searchKeywordsAdd(request,user_id):
    a = User.objects.get(userID=user_id)
    b = a.review_set.all()
    context = {"reviews": b, "user": a}
    if(request.method == 'POST'):
        value = request.POST["keyword"]
        print(value)
        get_user = User.objects.get(userID=user_id)
        c = get_user.searchWords.replace(" ","")
        if(c==""):
            l = []
            l.append(value)
            print(l)
            get_user.searchWords=str(l)
            get_user.save()
        else:
            get_list = eval(get_user.searchWords)
            get_list.append(value)
            get_user.searchWords=str(get_list)
            get_user.save()
        return render(request, 'preprocessed/user/user.html', context)
    else :
        return HttpResponse('failed')

def submitReview(request,product_id):
    if(request.method=='POST'):
        r = Review.objects.filter(asin=product_id)
        try:
            reviewer = User.objects.get(userID=request.POST["inputUserID"])
        except:
            return HttpResponse("Something Went Wrong")
        review = request.POST["textareaReview"]

        isSpam = False
        for i in r:
            if(i.reviewText.strip(' \t\n\r')==review.strip(' \t\n\r')):
                if(reviewer.blackListed==False):
                    reviewer.blackListed=True
                reviewer.numberOfSpams+=1
                reviewer.save()
                isSpam=True
                break

        if(isSpam==False):
            new = Review()
            new.asin = Product.objects.get(asin=product_id)
            new.reviewerID = reviewer
            new.reviewText = review
            new.reviewTime = strftime("%m %d, %Y", gmtime())
            new.unixReviewTime = int(time.time())
            new.helpful = 0
            new.notHelpful = 0
            new.overall = 0
            new.summary = ""
            new.save()

            # asp_sent_parsing_of_review
            globalString = ""
            analyser = SentimentIntensityAnalyzer()
            # try:
            asp_sent = {"camera": ["neutral"], "battery": ["neutral"], "display": ["neutral"], "processor": ["neutral"],
                        "overall": ["neutral"]}
            asp_rating = {}
            sent_array = sent_tokenize(review)

            count = 0
            for k in sent_array:
                k = k.lower()
                sent_array[count] = k
                count += 1

            for ind in sent_array:
                text = str(ind)
                # text = """its fabulous phone. Amazing battery back up, good clarity, great memory, beautiful colour of phone."""
                negatives = {}
                d = {}
                rel_dictionary = {}
                pos_output = nlp.annotate(text, properties={
                    'annotators': 'pos',
                    'outputFormat': 'json'
                })

                dep_output = nlp.annotate(text, properties={
                    'annotators': 'depparse',
                    'outputFormat': 'json'
                })

                negatives = getNegRelations(dep_output, negatives)

                # making POS tags dictionary
                for i in pos_output['sentences'][0]['tokens']:
                    d[i['word']] = i['pos']

                for j in dep_output['sentences'][0]['basicDependencies']:
                    dep_name = j['dep']
                    gov = j['governorGloss']
                    dep = j['dependentGloss']
                    if dep_name not in rel_dictionary:
                        rel_dictionary[dep_name] = []
                    rel_dictionary[dep_name].append({'gov': gov, 'dep': dep})
                print(rel_dictionary)


                # passing through each dependency
                for j in dep_output['sentences'][0]['basicDependencies']:
                    gov = j['governorGloss']
                    dep = j['dependentGloss']
                    if j['dep'] == 'amod':
                        asp_sent = rules.amodRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                    elif j['dep'] == 'nsubj':
                        asp_sent = rules.nsubjRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                    elif j['dep'] == 'acl:relcl':
                        asp_sent = rules.aclReclRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                    elif j['dep'] == 'dobj':
                        sent_intensity = analyser.polarity_scores(ind)
                        if not sent_intensity['compound'] == 0:
                            asp_sent = rules.dobjRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                    # elif j['dep'] == 'nsubjpass':
                    #     sent_intensity = analyser.polarity_scores(ind)
                    #     if not sent_intensity['compound'] == 0:
                    #         asp_sent = rules.nsubjpassRules(gov, dep, d, rel_dictionary, negatives, asp_sent)

            # print(asp_sent)

            asp_sent_copy = asp_sent.copy()
            dictionary = {
                "camera": ["photo", "photos", "pictures", "picture", "focus", "clarity", "selfie", "portrait mode",
                           "portrait", "portraits", "flash", "hdr", "4k", "4k recording", "picture quality", "video",
                           "video quality", "dual mode", "front camera", "rear camera", "back camera",
                           "low light performance", "lens", "aperture", "color", "colour", "colors", "colours",
                           "shutter speed", "manual mode", "professional mode", "bokeh", "bokeh effect"],
                "battery": ["backup", "charging", "battery backup", "life", "battery life", "charging speed",
                            "-charging time", "screen-on time", "fast-charging", "quick-charging"],
                "processor": ["speed", "performance", "chip", "cpu", "-lag", "architecture"],
                "display": ["screen", "touch", "bezel", "aspect ratio", "aspect-ratio", "screen size", "resolution",
                            "edges", "edge", "glass", "brightness", "contrast", "pixel density", "dpi", "color",
                            "colors", "colours", "visibility", "outdoor visibility"],
                "overall": ["phone", "cell", "cellphone", "mobile", "gadget", "device", "mobile phone", "smartphone",
                            "smart phone", "android device"]
            }

            # print("\nAspect Sentiment Pairs:")

            for each in asp_sent_copy:
                flag = 0
                if each not in dictionary:
                    for key in dictionary:
                        if flag == 0:
                            if each not in dictionary[key]:
                                flag = 0
                            else:
                                flag = 1
                    if flag == 0:
                        asp_sent.pop(each, None)

            asp_sent_copy = asp_sent.copy()
            for each in asp_sent_copy:
                for key in dictionary:
                    if each in dictionary[key]:
                        # print(str(review.reviewerID.userID)+" "+str(review.asin))
                        # print(asp_sent[each])
                        asp_sent[key] = asp_sent[key] + asp_sent[each]
                        asp_sent.pop(each)

            for each in asp_sent:
                string = str(asp_sent[each])
                # print(each + " : " + string)

            for asp in asp_sent:
                length = len(asp_sent[asp])
                avg = 0
                sum = 0
                for word in asp_sent[asp]:
                    # blob_word = TextBlob(word)
                    sent_val = analyser.polarity_scores(word)
                    sum = sum + sent_val['compound']
                avg = sum / length
                asp_rating[asp] = avg
                # print(avg)

            # scaling on the 0 to 5 scale
            for asp in asp_sent:
                non_scaled = asp_rating[asp]
                scaled = (non_scaled + 1) * 2.5
                asp_rating[asp] = round(scaled,2)

            # print("\nRatings:")
            for each in asp_rating:
                string = str(asp_rating[each])
                # print(each + " : " + string)

            # Dumping Unicode to JSON format

            globalString = globalString+str("<h4>"+str(product_id)+str(json.dumps(asp_rating))+"</h4>")
            UserProfile.objects.create(userID = reviewer, asin = new.asin,asp_sent_dictionary = str(json.dumps(asp_rating)))
            data = {}
            data["asin"] = product_id
            data["asp_sent"] = {}
            for i in asp_rating:
                data["asp_sent"][i] = {"rating":asp_rating[i],"reviewers_count":1}


            print(json.dumps(data))

            fetched_product = Product_Asp_Sent.objects.get(asin=new.asin)
            asp_sent_fetched_product = json.loads(fetched_product.aspects)
            for j in data["asp_sent"]:
            # if aspect is already merged
                if j in asp_sent_fetched_product:
                    prev_reviewers_count = asp_sent_fetched_product[j]["reviewers_count"]
                    reviewers_count = data["asp_sent"][j]["reviewers_count"] + prev_reviewers_count
                    rating = (asp_sent_fetched_product[j]["rating"] * prev_reviewers_count + data["asp_sent"][j][
                        "rating"]) / reviewers_count
                    rating = round(rating, 2)
                    asp_sent_fetched_product[j] = {"rating": rating, "reviewers_count": reviewers_count}
                # if aspect is not merged
                else:
                    asp_sent_fetched_product[j] = data["asp_sent"][j]
            fetched_product.save()

        a = Product.objects.get(asin=product_id)
        b = a.review_set.all()
        c = User.objects.all()
        context = {"product": a, "reviews": b, "users": c}
        return render(request, 'preprocessed/product/product.html', context)
    else:
        return HttpResponse("<h1>Error in submitting</h1>")

# def submitReview(request,product_id):
#     if(request.method=='POST'):
#         new = Review()
#         new.asin = Product.objects.get(asin=product_id)
#         new.reviewerID = User.objects.get(userID=request.POST["inputUserID"])
#         new.reviewText = request.POST["textareaReview"]
#         new.reviewTime = strftime("%m %d, %Y", gmtime())
#         new.unixReviewTime = int(time.time())
#         new.helpful = 0
#         new.notHelpful = 0
#         new.overall = 0
#         new.summary = ""
#         new.save()
#
#         a = Product.objects.get(asin=product_id)
#         b = a.review_set.all()
#         c = User.objects.all();
#         context = {"product": a, "reviews": b, "users": c}
#         return render(request, 'preprocessed/product/product.html', context)
#     else:
#         return HttpResponse("<h1>Error in submitting</h1>")


def do_action_for_product(request):
    if(request.method == 'POST'):
        product_id = request.POST["product_id"]
        action = request.POST["action"]
        if product_id!="" and action!="":
            if action=="Check Spams":
                r = Review.objects.filter(asin=product_id)
                reviewArray = []
                count = 0
                for i in r:
                    count += 1
                    for j in r[count:]:
                        if (i.reviewText.strip(' \t\n\r') == j.reviewText.strip(' \t\n\r')):
                            if i.reviewerID.numberOfSpams > j.reviewerID.numberOfSpams:
                                i.reviewerID.blackListed = True
                                i.reviewerID.numberOfSpams += 1
                                reviewArray.append(i.reviewerID.userID)
                            elif i.reviewerID.numberOfSpams < j.reviewerID.numberOfSpams:
                                j.reviewerID.blackListed = True
                                j.reviewerID.numberOfSpams += 1
                                reviewArray.append(j.reviewerID.userID)
                            else:
                                j.reviewerID.blackListed = True
                                j.reviewerID.numberOfSpams += 1
                                reviewArray.append(j.reviewerID.userID)

                s = set(reviewArray)
                for i in s:
                    Review.objects.filter(asin=product_id).filter(reviewerID=i).delete()
                return admin(request)
            elif action=="Helpfulness Check":
                reviews = Review.objects.filter(asin=product_id)
                for i in reviews:
                    ratio = (i.helpful + 1) / (i.notHelpful + 1)
                    if ratio <= 0.5:
                        i.isConsidered = False
                        i.save()
                return admin(request)
            else :
                return HttpResponse("Something went wrong")

        else:
            return HttpResponse("Something went wrong")
    else :
        return HttpResponse('failed')




def reviews(request):
    reviews = Review.objects.all()
    context = {"reviews":reviews}
    return render(request,'preprocessed/review/review_index.html',context)


# Reviews to Aspect Sentiment Code

def asp_sent(request):
    analyser = SentimentIntensityAnalyzer()
    # Create product asp_sentiment_dictionary
    f = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/productwise_asp_sent_dictionary.txt", "w")

    products = Product.objects.all()
    globalString = ""
    for product in products:
        reviews = Review.objects.filter(asin=product)
        counter=0

        for review in reviews:
            try:
                counter=counter+1
                asp_sent = {"camera": ["neutral"], "battery": ["neutral"], "display": ["neutral"], "processor": ["neutral"],
                            "overall": ["neutral"]}
                asp_rating = {}
                sent_array = sent_tokenize(review.reviewText)

                count = 0
                for k in sent_array:
                    k = k.lower()
                    sent_array[count] = k
                    count += 1

                for ind in sent_array:
                    text = str(ind)
                    # text = """its fabulous phone. Amazing battery back up, good clarity, great memory, beautiful colour of phone."""
                    negatives = {}
                    d = {}
                    rel_dictionary = {}
                    pos_output = nlp.annotate(text, properties={
                        'annotators': 'pos',
                        'outputFormat': 'json'
                    })

                    dep_output = nlp.annotate(text, properties={
                        'annotators': 'depparse',
                        'outputFormat': 'json'
                    })

                    negatives = getNegRelations(dep_output, negatives)

                    # making POS tags dictionary
                    for i in pos_output['sentences'][0]['tokens']:
                        d[i['word']] = i['pos']

                    for j in dep_output['sentences'][0]['basicDependencies']:
                        dep_name = j['dep']
                        gov = j['governorGloss']
                        dep = j['dependentGloss']
                        if dep_name not in rel_dictionary:
                            rel_dictionary[dep_name] = []
                        rel_dictionary[dep_name].append({'gov': gov, 'dep': dep})
                    print(rel_dictionary)


                    # passing through each dependency
                    for j in dep_output['sentences'][0]['basicDependencies']:
                        gov = j['governorGloss']
                        dep = j['dependentGloss']
                        if j['dep'] == 'amod':
                            asp_sent = rules.amodRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        elif j['dep'] == 'nsubj':
                            asp_sent = rules.nsubjRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        elif j['dep'] == 'acl:relcl':
                            asp_sent = rules.aclReclRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        elif j['dep'] == 'dobj':
                            sent_intensity = analyser.polarity_scores(ind)
                            if not sent_intensity['compound'] == 0:
                                asp_sent = rules.dobjRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        # elif j['dep'] == 'nsubjpass':
                        #     sent_intensity = analyser.polarity_scores(ind)
                        #     if not sent_intensity['compound'] == 0:
                        #         asp_sent = rules.nsubjpassRules(gov, dep, d, rel_dictionary, negatives, asp_sent)

                # print(asp_sent)

                asp_sent_copy = asp_sent.copy()
                dictionary = {
                    "camera": ["photo", "photos", "pictures", "picture", "focus", "clarity", "selfie", "portrait mode",
                               "portrait", "portraits", "flash", "hdr", "4k", "4k recording", "picture quality", "video",
                               "video quality", "dual mode", "front camera", "rear camera", "back camera",
                               "low light performance", "lens", "aperture", "color", "colour", "colors", "colours",
                               "shutter speed", "manual mode", "professional mode", "bokeh", "bokeh effect"],
                    "battery": ["backup", "charging", "battery backup", "life", "battery life", "charging speed",
                                "-charging time", "screen-on time", "fast-charging", "quick-charging"],
                    "processor": ["speed", "performance", "chip", "cpu", "-lag", "architecture"],
                    "display": ["screen", "touch", "bezel", "aspect ratio", "aspect-ratio", "screen size", "resolution",
                                "edges", "edge", "glass", "brightness", "contrast", "pixel density", "dpi", "color",
                                "colors", "colours", "visibility", "outdoor visibility"],
                    "overall": ["phone", "cell", "cellphone", "mobile", "gadget", "device", "mobile phone", "smartphone",
                                "smart phone", "android device"]
                }

                # print("\nAspect Sentiment Pairs:")

                for each in asp_sent_copy:
                    flag = 0
                    if each not in dictionary:
                        for key in dictionary:
                            if flag == 0:
                                if each not in dictionary[key]:
                                    flag = 0
                                else:
                                    flag = 1
                        if flag == 0:
                            asp_sent.pop(each, None)

                asp_sent_copy = asp_sent.copy()
                for each in asp_sent_copy:
                    for key in dictionary:
                        if each in dictionary[key]:
                            # print(str(review.reviewerID.userID)+" "+str(review.asin))
                            # print(asp_sent[each])
                            asp_sent[key] = asp_sent[key] + asp_sent[each]
                            asp_sent.pop(each)

                for each in asp_sent:
                    string = str(asp_sent[each])
                    # print(each + " : " + string)

                for asp in asp_sent:
                    length = len(asp_sent[asp])
                    avg = 0
                    sum = 0
                    for word in asp_sent[asp]:
                        # blob_word = TextBlob(word)
                        sent_val = analyser.polarity_scores(word)
                        sum = sum + sent_val['compound']
                    avg = sum / length
                    asp_rating[asp] = avg
                    print(avg)

                # scaling on the 0 to 5 scale
                for asp in asp_sent:
                    non_scaled = asp_rating[asp]
                    scaled = (non_scaled + 1) * 2.5
                    asp_rating[asp] = round(scaled,2)

                # print("\nRatings:")
                for each in asp_rating:
                    string = str(asp_rating[each])
                    # print(each + " : " + string)

                # Dumping Unicode to JSON format

                globalString = globalString+str("<h4>"+str(product.asin)+str(json.dumps(asp_rating))+"</h4>")
                UserProfile.objects.create(userID = review.reviewerID, asin = review.asin,asp_sent_dictionary = str(json.dumps(asp_rating)))
                data = {}
                data["asin"] = product.asin
                data["asp_sent"] = {}
                for i in asp_rating:
                    data["asp_sent"][i] = {"rating":asp_rating[i],"reviewers_count":1}

                f.write(json.dumps(data))
                f.write('\n')
            except:
                print("Error")

    return HttpResponse(globalString)

def asp_sent_view_only(request):
    analyser = SentimentIntensityAnalyzer()
    # Create product asp_sentiment_dictionary

    products = Product.objects.all()
    globalString = ""
    for product in products:
        reviews = Review.objects.filter(asin=product)
        counter=0

        for review in reviews:
            try:
                counter=counter+1
                asp_sent = {"camera": ["neutral"], "battery": ["neutral"], "display": ["neutral"], "processor": ["neutral"],
                            "overall": ["neutral"]}
                asp_rating = {}
                sent_array = sent_tokenize(review.reviewText)

                count = 0
                for k in sent_array:
                    k = k.lower()
                    sent_array[count] = k
                    count += 1

                for ind in sent_array:
                    text = str(ind)
                    # text = """its fabulous phone. Amazing battery back up, good clarity, great memory, beautiful colour of phone."""
                    negatives = {}
                    d = {}
                    rel_dictionary = {}
                    pos_output = nlp.annotate(text, properties={
                        'annotators': 'pos',
                        'outputFormat': 'json'
                    })

                    dep_output = nlp.annotate(text, properties={
                        'annotators': 'depparse',
                        'outputFormat': 'json'
                    })

                    negatives = getNegRelations(dep_output, negatives)

                    # making POS tags dictionary
                    for i in pos_output['sentences'][0]['tokens']:
                        d[i['word']] = i['pos']

                    for j in dep_output['sentences'][0]['basicDependencies']:
                        dep_name = j['dep']
                        gov = j['governorGloss']
                        dep = j['dependentGloss']
                        if dep_name not in rel_dictionary:
                            rel_dictionary[dep_name] = []
                        rel_dictionary[dep_name].append({'gov': gov, 'dep': dep})
                    print(rel_dictionary)


                    # passing through each dependency
                    for j in dep_output['sentences'][0]['basicDependencies']:
                        gov = j['governorGloss']
                        dep = j['dependentGloss']
                        if j['dep'] == 'amod':
                            asp_sent = rules.amodRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        elif j['dep'] == 'nsubj':
                            asp_sent = rules.nsubjRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        elif j['dep'] == 'acl:relcl':
                            asp_sent = rules.aclReclRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        elif j['dep'] == 'dobj':
                            sent_intensity = analyser.polarity_scores(ind)
                            if not sent_intensity['compound'] == 0:
                                asp_sent = rules.dobjRules(gov, dep, d, rel_dictionary, negatives, asp_sent)
                        # elif j['dep'] == 'nsubjpass':
                        #     sent_intensity = analyser.polarity_scores(ind)
                        #     if not sent_intensity['compound'] == 0:
                        #         asp_sent = rules.nsubjpassRules(gov, dep, d, rel_dictionary, negatives, asp_sent)

                # print(asp_sent)

                asp_sent_copy = asp_sent.copy()
                dictionary = {
                    "camera": ["photo", "photos", "pictures", "picture", "focus", "clarity", "selfie", "portrait mode",
                               "portrait", "portraits", "flash", "hdr", "4k", "4k recording", "picture quality", "video",
                               "video quality", "dual mode", "front camera", "rear camera", "back camera",
                               "low light performance", "lens", "aperture", "color", "colour", "colors", "colours",
                               "shutter speed", "manual mode", "professional mode", "bokeh", "bokeh effect"],
                    "battery": ["backup", "charging", "battery backup", "life", "battery life", "charging speed",
                                "-charging time", "screen-on time", "fast-charging", "quick-charging"],
                    "processor": ["speed", "performance", "chip", "cpu", "-lag", "architecture"],
                    "display": ["screen", "touch", "bezel", "aspect ratio", "aspect-ratio", "screen size", "resolution",
                                "edges", "edge", "glass", "brightness", "contrast", "pixel density", "dpi", "color",
                                "colors", "colours", "visibility", "outdoor visibility"],
                    "overall": ["phone", "cell", "cellphone", "mobile", "gadget", "device", "mobile phone", "smartphone",
                                "smart phone", "android device"]
                }

                # print("\nAspect Sentiment Pairs:")

                for each in asp_sent_copy:
                    flag = 0
                    if each not in dictionary:
                        for key in dictionary:
                            if flag == 0:
                                if each not in dictionary[key]:
                                    flag = 0
                                else:
                                    flag = 1
                        if flag == 0:
                            asp_sent.pop(each, None)

                asp_sent_copy = asp_sent.copy()
                for each in asp_sent_copy:
                    for key in dictionary:
                        if each in dictionary[key]:
                            # print(str(review.reviewerID.userID)+" "+str(review.asin))
                            # print(asp_sent[each])
                            asp_sent[key] = asp_sent[key] + asp_sent[each]
                            asp_sent.pop(each)

                for each in asp_sent:
                    string = str(asp_sent[each])
                    # print(each + " : " + string)

                for asp in asp_sent:
                    length = len(asp_sent[asp])
                    avg = 0
                    sum = 0
                    for word in asp_sent[asp]:
                        # blob_word = TextBlob(word)
                        sent_val = analyser.polarity_scores(word)
                        sum = sum + sent_val['compound']
                    avg = sum / length
                    asp_rating[asp] = avg
                    print(avg)

                # scaling on the 0 to 5 scale
                for asp in asp_sent:
                    non_scaled = asp_rating[asp]
                    scaled = (non_scaled + 1) * 2.5
                    asp_rating[asp] = round(scaled,2)

                # print("\nRatings:")
                for each in asp_rating:
                    string = str(asp_rating[each])
                    # print(each + " : " + string)

                # Dumping Unicode to JSON format

                globalString = globalString+str("<h4>"+str(product.asin)+str(json.dumps(asp_rating))+"</h4>")

            except:
                print("Error")

    return HttpResponse(globalString)

# Aspect Sentiment Code
def corefResolver(line):
    ind_sent = []
    complete_coref_output = nlp.annotate(line,properties={'annotators':'dcoref','outputFormat':'json'})
    coref_output = complete_coref_output['corefs']
    raw_sent = TextBlob(line)
    sent_array = raw_sent.sentences
    for j in sent_array:
        ind_sent.append(str(j))
    for k in coref_output:
        prop_noun = ""
        for m in coref_output[k]:
            if m['type'] == 'NOMINAL' and prop_noun == "":
                prop_noun = m['text']
            elif m['type'] == 'PRONOMINAL' and prop_noun != "":
                sent_num = int(m['sentNum'])
                ind_sent[sent_num-1] = ind_sent[sent_num-1].replace(m['text'],prop_noun)

    return ind_sent

#insert aspect-sentiment pair in asp_sent dictionary
def insert_asp_sent(asp,sent):
    if asp not in asp_sent:
        asp_sent[asp] = []
    asp_sent[asp].append(sent)

#get negative relations for further reference
def getNegRelations(dep_output,negatives):
    for j in dep_output['sentences'][0]['basicDependencies']:
        gov = j['governorGloss']
        if j['dep'] == 'neg':
            negatives[gov] = ''
    return negatives


# Merge Aspect Sentiment for Product
def merge_asp_sent_for_product(request):
    string = ""
    products = Product.objects.all()
    f_output = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/merged_productwise_asp_sent_dictionary.txt","w")
    for product in products:

        data = {"asin":product.asin,"asp_sent":{}}
        f_input = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/productwise_asp_sent_dictionary.txt", "r")
        for i in f_input:
            loaded_json = json.loads(i)
            if loaded_json["asin"] == product.asin:
                for j in loaded_json["asp_sent"]:

                    # if aspect is already merged
                    if j in data["asp_sent"]:
                        prev_reviewers_count = data["asp_sent"][j]["reviewers_count"]
                        reviewers_count = loaded_json["asp_sent"][j]["reviewers_count"]+prev_reviewers_count
                        rating = (data["asp_sent"][j]["rating"]*prev_reviewers_count+loaded_json["asp_sent"][j]["rating"])/reviewers_count
                        rating = round(rating,2)
                        data["asp_sent"][j] = {"rating": rating,"reviewers_count" : reviewers_count }
                    # if aspect is not merged
                    else:
                        data["asp_sent"][j] = loaded_json["asp_sent"][j]
        f_output.write(json.dumps(data))
        f_output.write("\n")

        a = Product_Asp_Sent()
        a.asin = product
        a.aspects = json.dumps(data)
        a.save()

        string += "\n"+str(json.dumps(data))+"\n"

    return HttpResponse(string)

# Merge Aspect Sentiment for Product(View_only)
def merge_asp_sent_for_product_view_only(request):
    string = ""
    products = Product.objects.all()

    for product in products:

        data = {"asin":product.asin,"asp_sent":{}}
        f_input = open("/home/tejas1106/acad_bin/be_project/ARBRS/Data/final_dataset/productwise_asp_sent_dictionary.txt", "r")
        for i in f_input:
            loaded_json = json.loads(i)
            if loaded_json["asin"] == product.asin:
                for j in loaded_json["asp_sent"]:

                    # if aspect is already merged
                    if j in data["asp_sent"]:
                        prev_reviewers_count = data["asp_sent"][j]["reviewers_count"]
                        reviewers_count = loaded_json["asp_sent"][j]["reviewers_count"]+prev_reviewers_count
                        rating = (data["asp_sent"][j]["rating"]*prev_reviewers_count+loaded_json["asp_sent"][j]["rating"])/reviewers_count
                        rating = round(rating,2)
                        data["asp_sent"][j] = {"rating": rating,"reviewers_count" : reviewers_count }
                    # if aspect is not merged
                    else:
                        data["asp_sent"][j] = loaded_json["asp_sent"][j]

        string += "\n"+str(json.dumps(data))+"\n"

    return HttpResponse(string)

def truncate_entities(request):
    if request.method == "POST":
        entity = request.POST["entity"]
        print(entity)
        if entity =="Product_Asp_Sent":
            Product_Asp_Sent.objects.all().delete()
            return admin(request)
        elif entity == "UserProfile":
            print("UserProfile")
            UserProfile.objects.all().delete()
            return admin(request)
        elif entity == "Recommendation":
            Recommendation.objects.all().delete()
            return admin(request)
        else:
            return HttpResponse("Something Went Wrong")
    else:
        return HttpResponse("Something Went Wrong")

# Recommendation Logic
def recommendation(user_id):
    string  =""
    product_recommended = []
    product_recommended_on_product = []
    aspects_for_recommendation = []
    user = User.objects.get(userID=user_id)
    userProfiles = UserProfile.objects.filter(userID=user_id)

    for userProfile in userProfiles:
        asp_sent_dict = json.loads(userProfile.asp_sent_dictionary)
        categories = eval(userProfile.asin.categories)

        for category in categories:
            get_category = Category_Mapping.objects.get(category=category)
            products = eval(get_category.products)

            for product_id in products:
                get_Product_Asp_Sent = json.loads(Product_Asp_Sent.objects.get(asin=product_id).aspects)["asp_sent"]
                count=0
                # string+=str(get_Product_Asp_Sent)
                stringg = ""
                for i in get_Product_Asp_Sent:
                    # string+=str(float(json.dumps(get_Product_Asp_Sent[i]["rating"])))
                    if(i in asp_sent_dict):
                        # string+=str(asp_sent_dict[i])
                        print(i)
                        if (float(json.dumps(get_Product_Asp_Sent[i]["rating"])) > float(json.dumps(asp_sent_dict[i]))+0.1):
                            print(str(float(json.dumps(get_Product_Asp_Sent[i]["rating"])))+"  "+str(float(json.dumps(asp_sent_dict[i]))))
                            count+=1
                            stringg = stringg + i
                            stringg = stringg + ", "
                            if(product_id!=userProfile.asin.asin):
                                tempAsin = product_id
                                product_recommended.append(tempAsin)
                                string+=tempAsin
                                product_recommended_on_product.append(userProfile.asin.asin)
                                aspects_for_recommendation.append(stringg)

    for i in range(len(product_recommended)):
        # a = Recommendation()
        userID1 = User.objects.get(userID = user_id)
        asin1 = Product.objects.get(asin=product_recommended[i])
        recommended_on_asin1 = Product.objects.get(asin=product_recommended_on_product[i])
        aspectss_for_recommendation = aspects_for_recommendation[i]
        try:
            obj = Recommendation.objects.get(userID=userID1,asin=asin1)
        except Recommendation.DoesNotExist:
            obj = Recommendation(userID=userID1,asin=asin1,recommended_on_asin=recommended_on_asin1,aspects_for_recommendation=aspectss_for_recommendation)
            obj.save()
        # a.save()
    # return HttpResponse(string)

def recommendation_switch(request):
    get_admin = Admin.objects.get(admin_user="tejas1106")
    if get_admin.recommendation_status:
        get_admin.recommendation_status = False
    elif not get_admin.recommendation_status:
        get_admin.recommendation_status = True
    else:
        return HttpResponse("Something Went Wrong")
    get_admin.save()
    return admin(request)



## Preprocessing Phases
def checkSpams(request,product_id):
    product = Product.objects.get(asin=product_id)
    r = Review.objects.filter(asin=product_id)
    reviewArray=[]
    count=0
    for i in r:
        count+=1
        for j in r[count:]:
            if (i.reviewText.strip(' \t\n\r') == j.reviewText.strip(' \t\n\r')):
                if i.reviewerID.numberOfSpams > j.reviewerID.numberOfSpams:
                    i.reviewerID.blackListed = True
                    i.reviewerID.numberOfSpams+=1
                    reviewArray.append(i.reviewerID.userID)
                elif i.reviewerID.numberOfSpams < j.reviewerID.numberOfSpams:
                    j.reviewerID.blackListed = True
                    j.reviewerID.numberOfSpams += 1
                    reviewArray.append(j.reviewerID.userID)
                # elif i.unixReviewTime > j.unixReviewTime:
                #     i.reviewerID.blackListed = True
                #     i.reviewerID.numberOfSpams += 1
                #     reviewArray.append(i.reviewerID.userID)
                else:
                    j.reviewerID.blackListed = True
                    j.reviewerID.numberOfSpams += 1
                    reviewArray.append(j.reviewerID.userID)

    s = set(reviewArray)
    for i in s:
        Review.objects.filter(asin=product_id).filter(reviewerID=i).delete()
    return HttpResponse('<h2>done</h2>')

def helpfulnessCheck(request,product_id):
    reviews = Review.objects.filter(asin = product_id)
    for i in reviews:
        ratio = (i.helpful + 1) / (i.notHelpful + 1)
        if ratio <= 0.5:
            i.isConsidered = False
            i.save()
    return HttpResponse("<h3>done</h3>")





