from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^$',
        views.ClaseList.as_view(),
        name='index'
    ),
    url(
        r'^nueva/$',
        views.ClaseCreate.as_view(),
        name='create'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        views.ClaseUpdate.as_view(),
        name='update'
    ),
    url(
        r'^descarga/$',
        views.ClaseJson.as_view(),
        name='json'
    ),
    url(
        r'^version/$',
        views.VersionView.as_view(),
        name='version'
    ),
]
