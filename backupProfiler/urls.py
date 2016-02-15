from django.conf.urls import patterns, include, url
# from django.contrib import admin
import views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import settings
from django.conf import settings

viewer = views.ViewsHandler()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', viewer.homepage, name='home'),
    url(r'^overview/', viewer.overviewPage, name='overview'),
    url(r'^smsdata/', viewer.allSMSpage, name='smsdata'),
    url(r'^calldata/', viewer.allCallspage, name='calldata'),
    url(r'^top10/', viewer.top10Data, name='top10'),
    url(r'^calendardata/', viewer.allCalendarpage, name='calendardata'),
    url(r'^appdata/', viewer.allAppPage, name='appdata'),
    url(r'^appspecific/', viewer.appSpecificsPage, name='appspecific'),
    url(r'^accounts/', viewer.accountsPage, name='accounts'),
    url(r'^appplists/', viewer.appPlistsPage, name='appplists'),
    url(r'^safaridata/', viewer.safariPage, name='safaridata'),
    url(r'^snapdata/', viewer.snapchatPage, name='snapdata'),
    url(r'^hopstopdata/', viewer.hopstopPage, name='hopstopdata'),
    url(r'^images/', viewer.imagesPage, name='images'),
    url(r'^update/', viewer.updateCurrent, name='update'),
    url(r'^create/', viewer.createBackup, name='create'),
    url(r'^wifi/', viewer.wifiPage, name='wifi'),
    url(r'^keychain/', viewer.keychainPage, name='keychain'),
    url(r'^notesdata/', viewer.notesPage, name='notesdata'),
    url(r'^dbs/', viewer.dbsPage, name='dbs'),
) # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


