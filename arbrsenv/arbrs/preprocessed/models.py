from django.db import models

class Product(models.Model):
    asin = models.CharField(max_length=25,primary_key=True)
    title = models.CharField(max_length=500)
    # price = models.FloatField()
    imUrl = models.CharField(max_length=500)
    description = models.CharField(max_length=2000)
    categories = models.CharField(max_length=2000,default="")
    # brand = models.CharField(max_length=1000)
    # salesRank = models.CharField(max_length=1000)
    # also_viewed = models.CharField(max_length=1500,default="")
    buy_after_viewing = models.CharField(max_length=1500,default="")

    def __str__(self):
        return self.asin+" "+self.title

class User(models.Model):
    userID = models.CharField(max_length=25,primary_key=True)
    userName = models.CharField(max_length=100)
    searchWords = models.CharField(max_length=2000,null=True)
    blackListed = models.BooleanField(default=False)
    numberOfSpams = models.IntegerField(default=0)

    def __str__(self):
        return self.userID+" "+self.userName

class Review(models.Model):
    asin = models.ForeignKey(Product,on_delete=models.CASCADE)
    reviewerID = models.ForeignKey(User,on_delete=models.CASCADE)
    helpful = models.IntegerField(default=0)
    notHelpful = models.IntegerField(default=0)
    reviewText = models.CharField(max_length=2000)
    overall = models.FloatField()
    summary = models.CharField(max_length=1000)
    # unixReviewTime = models.CharField(max_length=100)
    reviewTime = models.CharField(max_length=100)
    isConsidered = models.BooleanField(default=True)

    def __str__(self):
        return self.reviewerID.userID+" "+self.reviewerID.userName+" "+self.asin.asin

class UserProfile(models.Model) :
    userID = models.ForeignKey(User,on_delete = models.CASCADE)
    userName = models.CharField(max_length=100)
    asin = models.ForeignKey(Product,on_delete = models.CASCADE)
    asp_sent_dictionary = models.CharField(max_length = 2000)

    def __str__(self):
        return str(self.userID.userID)+" "+str(self.asin.asin)

class Category_Mapping(models.Model) :
    category = models.CharField(max_length = 255,primary_key=True)
    products = models.CharField(max_length=2000,null=True)

    def __str__(self):
        return self.category
.1
class Recommendation(models.Model) :
    userID = models.ForeignKey(User,on_delete = models.CASCADE)
    asin = models.ForeignKey(Product,on_delete = models.CASCADE,related_name='product_recommended')
    recommended_on_asin = models.ForeignKey(Product,on_delete = models.CASCADE,related_name='product_recommended_on')
    aspects_for_recommendation = models.CharField(max_length=2000,null=True)

    def __str__(self):
        return str(self.userID.userID)+" "+str(self.asin.asin)+" "+str(self.recommended_on_asin.asin)


class Product_Asp_Sent(models.Model):
    asin = models.ForeignKey(Product,on_delete=models.CASCADE)
    aspects = models.CharField(max_length=2000,default="")

    def __str__(self):
        return str(self.asin.asin)

class Admin(models.Model):
    admin_user = models.CharField(max_length=100)
    recommendation_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.admin_user)