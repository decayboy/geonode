# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.db import models
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib import auth
from django.db.models import signals
from django.conf import settings

from taggit.managers import TaggableManager

from geonode.base.enumerations import COUNTRIES
from geonode.groups.models import GroupProfile
from geonode.notifications_helper import send_notification
# from account.models import EmailAddress

from .utils import format_address
from .languages import LANGUAGES
from .timezones import TIMEZONES


email_subject = """Welcome to IHP-WINS/Bienvenue sur IHP-WINS"""

email_format = """Dear contributor,

Your account ({}) has been approved and is now active on the Water Information Network System.
You can now log in to {}

To manage your account, please go to {}/notifications/settings/.

The IHP-WINS Team

----------------------------------------------------

Cher contributeur,

Votre compte ({} a été approuvé et est désormais actif sur le Système de Réseau d’Informations sur l’Eau.
Vous pouvez dès à présent vous connecter sur {}.

Pour gérer votre compte, rendez-vous sur {}/notifications/settings/.

L’équipe IHP-WINS"""


class ProfileUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)


class Profile(AbstractUser):

    """Fully featured Geonode user"""

    approved = models.BooleanField(
        _('Is the user approved?'),
        default=False,
        help_text=_('approve user'))
    organization = models.CharField(
        _('Organization Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('name of the responsible organization'))
    profile = models.TextField(
        _('Profile'),
        null=True,
        blank=True,
        help_text=_('introduce yourself'))
    position = models.CharField(
        _('Position Name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('role or position of the responsible person'))
    voice = models.CharField(_('Voice'), max_length=255, blank=True, null=True, help_text=_(
        'telephone number by which individuals can speak to the responsible organization or individual'))
    fax = models.CharField(_('Facsimile'), max_length=255, blank=True, null=True, help_text=_(
        'telephone number of a facsimile machine for the responsible organization or individual'))
    delivery = models.CharField(
        _('Delivery Point'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('physical and email address at which the organization or individual may be contacted'))
    city = models.CharField(
        _('City'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('city of the location'))
    area = models.CharField(
        _('Administrative Area'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('state, province of the location'))
    zipcode = models.CharField(
        _('Postal Code'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('ZIP or other postal code'))
    country = models.CharField(
        choices=COUNTRIES,
        max_length=3,
        blank=True,
        null=True,
        help_text=_('country of the physical address'))
    keywords = TaggableManager(_('keywords'), blank=True, help_text=_(
        'commonly used word(s) or formalised word(s) or phrase(s) used to describe the subject \
            (space or comma-separated'))
    language = models.CharField(
        _("language"),
        max_length=10,
        choices=LANGUAGES,
        default=settings.LANGUAGE_CODE
    )
    timezone = models.CharField(
        max_length=100,
        default="",
        choices=TIMEZONES,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self._previous_active_state = self.is_active

    def get_absolute_url(self):
        return reverse('profile_detail', args=[self.username, ])

    def __unicode__(self):
        return u"%s" % (self.username)

    def class_name(value):
        return value.__class__.__name__

    objects = ProfileUserManager()
    USERNAME_FIELD = 'username'

    def group_list_public(self):
        return GroupProfile.objects.exclude(
            access="private").filter(groupmember__user=self)

    def group_list_all(self):
        return GroupProfile.objects.filter(groupmember__user=self).distinct()

    def is_member_of_group(self, group_slug):
        """
        Returns if the Profile belongs to a group of a given slug.
        """
        return self.groups.filter(name=group_slug).exists()

    def keyword_list(self):
        """
        Returns a list of the Profile's keywords.
        """
        return [kw.name for kw in self.keywords.all()]

    @property
    def name_long(self):
        if self.first_name and self.last_name:
            return '%s %s (%s)' % (self.first_name,
                                   self.last_name, self.username)
        elif (not self.first_name) and self.last_name:
            return '%s (%s)' % (self.last_name, self.username)
        elif self.first_name and (not self.last_name):
            return '%s (%s)' % (self.first_name, self.username)
        else:
            return self.username

    @property
    def location(self):
        return format_address(self.delivery, self.zipcode,
                              self.city, self.area, self.country)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        self._notify_account_activated()
        self._previous_active_state = self.is_active

    def _notify_account_activated(self):
        """Notify user that its account has been activated by a staff member"""
        became_active = self.is_active and not self._previous_active_state
        if became_active and self.last_login is None:
            # send_notification(users=(self,), label="account_active")
            pass


def get_anonymous_user_instance(Profile):
    return Profile(pk=-1, username='AnonymousUser')


def profile_post_save(instance, sender, **kwargs):
    """
    Make sure the user belongs by default to the anonymous group.
    This will make sure that anonymous permissions will be granted to the new users.
    """
    from django.contrib.auth.models import Group
    anon_group, created = Group.objects.get_or_create(name='anonymous')
    instance.groups.add(anon_group)
    # do not create email, when user-account signup code is in use
    if getattr(instance, '_disable_account_creation', False):
        return


def profile_pre_save(instance, sender, **kw):
    matching_profiles = Profile.objects.filter(id=instance.id)
    if matching_profiles.count() == 0:
        return
    if instance.is_active and not matching_profiles.get().is_active:
        send_notification((instance,), "account_active")
        if not instance.approved:
            instance.approved = True
            message = email_format.format(instance.username, settings.SITEURL, settings.SITEURL,
                                          instance.username, settings.SITEURL, settings.SITEURL)
            try:
                send_mail(
                    email_subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=True,
                )
            except:
                pass


def profile_signed_up(user, form, **kwargs):
    staff = auth.get_user_model().objects.filter(is_staff=True)
    send_notification(staff, "account_approve", {"from_user": user})


signals.pre_save.connect(profile_pre_save, sender=Profile)
signals.post_save.connect(profile_post_save, sender=Profile)
