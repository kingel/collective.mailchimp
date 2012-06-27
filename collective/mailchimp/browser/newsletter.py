# -*- coding: utf-8 -*-
import re
from zope.component.hooks import getSite
from zope.interface import Invalid
import greatape
from collective.mailchimp.interfaces import IMailchimpSettings

from Products.statusmessages.interfaces import IStatusMessage

from zope.component import getUtility

from z3c.form import form, field, button
from z3c.form.interfaces import WidgetActionExecutionError

from plone.z3cform.layout import wrap_form
from plone.registry.interfaces import IRegistry

from collective.mailchimp import _
from collective.mailchimp.interfaces import INewsletterSubscribe


class NewsletterSubscriberForm(form.Form):
    fields = field.Fields(INewsletterSubscribe)
    ignoreContext = True
    label = _(u"Subscribe to newsletter")

    def updateActions(self):
        super(NewsletterSubscriberForm, self).updateActions()
        self.actions['subscribe'].addClass('context')

    @button.buttonAndHandler(_(u"subscribe_to_newsletter_button",
                             default=u"Subscribe"),
                             name='subscribe')
    def handleApply(self, action):
        data, errors = self.extractData()
        if 'email' in data:
            # Fetch MailChimp settings
            registry = getUtility(IRegistry)
            mailchimp_settings = registry.forInterface(IMailchimpSettings)
            mailchimp = greatape.MailChimp(
                mailchimp_settings.api_key,
                mailchimp_settings.ssl,
                mailchimp_settings.debug)
            # Fetch MailChimp lists
            # XXX, Todo: For now we just fetch the first list.
            try:
                lists = mailchimp(method='lists')
                list_id = lists[0]['id']
            except greatape.MailChimpError, error:
                raise WidgetActionExecutionError(
                    Invalid(_(u"Could not fetch list from mailchimp.com: %s" %
                        error)))
            # Subscribe to MailChimp list
            merge_vars = dict(dummy='dummy')
            try:
                mailchimp(
                    method='listSubscribe',
                    id=list_id,
                    email_address=data['email'],
                    merge_vars=merge_vars,
                    )
            except greatape.MailChimpError, error:
                raise WidgetActionExecutionError('email',
                    Invalid(_(u"Could not subscribe to newsletter: %s" % error)))

            IStatusMessage(self.context.REQUEST).addStatusMessage(
                _(u"We have to confirm your email address. In order to " +
                   "finish the newsletter subscription, click on the link " +
                   "inside the email we just send you."),
                type="info")
            portal = getSite()
            self.request.response.redirect(portal.absolute_url())


NewsletterView = wrap_form(NewsletterSubscriberForm)
