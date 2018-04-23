from django.contrib import admin
from .models import Product, Review, User, UserProfile, Category_Mapping, Product_Asp_Sent, Recommendation, Admin

# # Register your models here.
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Review)
admin.site.register(Category_Mapping)
admin.site.register(UserProfile)
admin.site.register(Product_Asp_Sent)
admin.site.register(Recommendation)
admin.site.register(Admin)