from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.base import RedirectView
from registration.views import register
from aor.forms import  AuthenticationFormCaptcha, RegistrationFormCaptcha
from django.contrib.auth.views import login

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/forum/'), name='front-page'),
    url(r'^accounts/login/$', login, name="login",
        kwargs=dict(authentication_form=AuthenticationFormCaptcha)),
    url(r'^accounts/register/$', register,
        kwargs=dict(form_class=RegistrationFormCaptcha,
            backend='registration.backends.default.DefaultBackend'),
        name="registration"),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^forum/', include('pybb.urls', namespace='pybb')),
    url(r'^comments/', include('django.contrib.comments.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', include('robots.urls')),
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += staticfiles_urlpatterns()