import greatape

from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.registry.interfaces import IRegistry

from collective.mailchimp import _

available_fields = SimpleVocabulary([
    SimpleTerm(value=u'subscriber_list', title=_(u'Subscriber list')),
    SimpleTerm(value=u'email', title=_(u'E-Mail'))
    ])


class ICollectiveMailchimp(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.

    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """


class IMailchimpSettings(Interface):
    """Global mailchimp settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    api_key = schema.TextLine(
        title=_(u"MailChimp API Key"),
        description=_(u"help_api_key",
                      default=u"Enter in your MailChimp key here. Log into " +
                      "mailchimp.com, go to account -> extras -> API Keys & " +
                      "Authorized Apps and copy the API Key to this field."),
        required=True,
        default=u'',)

    debug = schema.Bool(
        title=_(u"Debug MailChimp"),
        description=_(u"help_debug",
                      default=u""),
        required=True,
        default=False)

    ssl = schema.Bool(
        title=_(u"SSL"),
        description=_(u"help_ssl",
                      default=u""),
        required=True,
        default=True)

    cache_sec = schema.Int(
        title=_(u"SSL"),
        description=_(u"help_cache_sec",
                      default=u""),
        required=True,
        default=500)

    available_fields = schema.Choice(
        title=_(u"Available fields"),
        description=_(u"help_available_fields",
                      default=u""),
        vocabulary=available_fields,
        required=False)

    lists_email_type = schema.TextLine(
        title=_(u"lists_email_type"),
        description=_(u"help_lists_email_type",
                      default=u""),
        required=True,
        default=u'html',)

    lists_double_optin = schema.Bool(
        title=_(u"lists_double_optin"),
        description=_(u"help_lists_double_optin",
                      default=u""),
        required=True,
        default=True)

    lists_update_existing = schema.Bool(
        title=_(u"lists_update_existing"),
        description=_(u"help_lists_update_existing",
                      default=u""),
        required=True,
        default=False)

    lists_replace_interests = schema.Bool(
        title=_(u"lists_replace_interests"),
        description=_(u"help_lists_replace_interests",
                      default=u""),
        required=True,
        default=True)

    @invariant
    def valid_api_key(obj):
        registry = getUtility(IRegistry)
        mailchimp_settings = registry.forInterface(IMailchimpSettings)
        mailchimp = greatape.MailChimp(
            obj.api_key,
            mailchimp_settings.ssl,
            mailchimp_settings.debug)
        try:
            return mailchimp(method='ping')
        except:
            raise Invalid(u"Your MailChimp API key is not valid. Please go " +
                "to mailchimp.com and check your API key.")