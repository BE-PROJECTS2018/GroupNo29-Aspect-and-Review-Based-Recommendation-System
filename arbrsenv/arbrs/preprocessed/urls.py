from django.conf.urls import include, url
from . import views

urlpatterns = [
    # preprocessed
    url(r'^$',views.index,name='index'),

    # products
    url(r'^products/$',views.products,name='products'),

    # products/123
    url(r'^products\/(?P<product_id>[0-9A-Za-z]+)$',views.productById,name='productById'),

    # users
    url(r'^users/$',views.users,name='users'),

    # users/123
    url(r'^users\/(?P<user_id>[0-9A-Za-z]+)$',views.userById,name='userById'),

    # admin
    url(r'^admin/$',views.admin,name='admin'),


    # searchWordsAdd/123
    url(r'^users\/(?P<user_id>[0-9A-Za-z]+)/searchKeywordsAdd$',views.searchKeywordsAdd,name='searchKeywordsAdd'),

    # sumbitReview
    url(r'^products\/(?P<product_id>[0-9A-Za-z]+)/submitReview$',views.submitReview,name='submitReview'),

    # check_all_spams
    url(r'^products\/(?P<product_id>[0-9A-Za-z]+)/checkSpams/$',views.checkSpams,name='checkSpams'),

    # check_helpfulNess
    url(r'^products\/(?P<product_id>[0-9A-Za-z]+)/helpfulnessCheck/$',views.helpfulnessCheck,name="helpfulnessCheck"),

    # reviews
    url(r'^reviews/$',views.reviews,name='reviews'),

    # review to Asp_Sent
    url(r'^asp_sent/$', views.asp_sent,name='asp_sent'),

    # review to Asp_Sent_View_Only
    url(r'^asp_sent_view_only/$', views.asp_sent_view_only,name='asp_sent_view_only'),

    # merge_asp_sent_for_product
    url(r'^merge_asp_sent_for_product/$', views.merge_asp_sent_for_product, name="merge_asp_sent_for_product"),

    # merge_asp_sent_for_product_View_Only
    url(r'^merge_asp_sent_for_product_view_only/$', views.merge_asp_sent_for_product_view_only, name="merge_asp_sent_for_product_view_only"),

    # Recommendation per user
    url(r'^users\/(?P<user_id>[0-9A-Za-z]+)/recommendation',views.recommendation,name='Recommendation'),

    # admin do_action_for_product
    url(r'^do_action_for_product/$',views.do_action_for_product,name='do_action_for_product'),

    # admin truncate_entities
    url(r'^truncate_entities/$',views.truncate_entities,name='truncate_entities'),

    # admin recommendation switch
    url(r'^recommendation_switch/$', views.recommendation_switch, name='recommendation_switch'),

]
