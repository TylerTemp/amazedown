"""
Link for AmazeUI


Some codes are from: [markdown-newtab](https://github.com/Undeterminant/markdown-newtab/)

Load this AFTER link_image
"""
import re
import logging
from collections import OrderedDict
from markdown import Extension
from markdown.inlinepatterns import \
    LinkPattern, ReferencePattern, AutolinkPattern, AutomailPattern, \
    LINK_RE, REFERENCE_RE, SHORT_REF_RE, IMAGE_LINK_RE, IMAGE_REFERENCE_RE, \
    AUTOMAIL_RE

try:
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import urlsplit

logger = logging.getLogger('MARKDOWN.link_icon_tab')


# pylint: disable=invalid-name, too-few-public-methods
class LinkIconMixin(object):
    """Common extension logic; mixed into the existing classes."""

    _IMG_RE = re.compile(''.join(('^', IMAGE_LINK_RE, '$|^', IMAGE_REFERENCE_RE, '$|^<img\s.*?>$')))

    brands = OrderedDict((
        ('', 'am-icon-link'),
        ('yahoo.com', 'am-icon-yahoo'),
        ('youtube.com', 'am-icon-youtube'),
        ('plus.google.com', 'am-icon-google-plus'),
        ('google.com', 'am-icon-google'),
        ('twitter.com', 'am-icon-twitter'),
        ('facebook.com', 'am-icon-facebook'),
        ('github.com', 'am-icon-github'),
        ('instagram.com', 'am-icon-instagram'),
        ('reddit.com', 'am-icon-reddit-alien'),
    ))

    def __init__(self, *args, **kwargs):
        self._host = kwargs.pop('host', '')
        brands = kwargs.pop('brands', None)
        if brands is not None:
            allowed = set(brands).intersection(self.brands)
            allowed.add('')
            allowed_brands = OrderedDict((key, self.brands[key]) for key in allowed)
            self.brands = allowed_brands

        if self._host:
            self.brands = OrderedDict(self.brands)
            self.brands[self._host] = self.brands['']

        super(LinkIconMixin, self).__init__(*args, **kwargs)


    def handleMatch(self, match):
        """Handles a match on a pattern; used by existing implementation."""

        elem = super(LinkIconMixin, self).handleMatch(match)
        logger.debug(self.type())
        is_mail = self.type() == 'LinkIconAutomailPattern'

        if elem is not None and not self._IMG_RE.match(elem.text):
            logger.debug('handled %s', elem.get('href', None))
            text = elem.text
            link = elem.get('href')
            if is_mail:
                icon_class = 'am-icon-envelope'
            else:
                parsed = urlsplit(link)
                netloc = parsed.netloc
                icon_class = self.get_brand_icon(netloc)
                logger.debug('%s -> %s', netloc, icon_class)

            if icon_class is not None:
                logger.debug('pre-head icon %s', link)
                elem.set('class', icon_class)
                elem.text = ' ' + text

            if not is_mail and netloc not in (self._host, ''):
                logger.debug('external link %s', link)
                elem.text += ' <span class="am-icon-external-link"></span>'
                elem.set('target', '_blank')

        return elem

    def get_brand_icon(self, host):
        if host == '':
            return self.brands['']

        for k, icon in self.brands.items():
            if k == '':
                continue

            logger.debug('%s/%s - %s', host, k, icon)
            if host == k:
                return icon

            if host.endswith('.' + k):
                return icon

        return None


class LinkIconLinkPattern(LinkIconMixin, LinkPattern):
    """Links to URLs, e.g. [link](https://duck.co)."""
    pass



class LinkIconReferencePattern(LinkIconMixin, ReferencePattern):
    """Links to references, e.g. [link][1]."""
    pass



class LinkIconAutolinkPattern(LinkIconMixin, AutolinkPattern):
    """Autommatic links, e.g. <duck.co>."""
    pass


class LinkIconAutomailPattern(LinkIconMixin, AutomailPattern):
    pass


class LinkIconTabExtension(Extension):
    """Modifies HTML output to open links in a new tab."""

    def __init__(self, **kwargs):
        self.config = {'host': [kwargs.get('host', ''), 'host name'],
                       'brands': [kwargs.get('brands', None), 'auto banner']}
        super(LinkIconTabExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        host = self.getConfig('host', '')
        brands = self.getConfig('brands', None)

        md.inlinePatterns.add(
            'link_icon_tab_link',
            LinkIconLinkPattern(LINK_RE, md,
                                host=host, brands=brands),
            '<link')

        md.inlinePatterns.add(
            'link_icon_tab_reference',
            LinkIconReferencePattern(REFERENCE_RE, md,
                                     host=host, brands=brands),
            '<reference'
        )

        md.inlinePatterns.add(
            'link_icon_tab_short_reference',
            LinkIconReferencePattern(SHORT_REF_RE, md,
                                     host=host, brands=brands),
            '<short_reference'
        )

        md.inlinePatterns.add(
            'link_icon_tab_autolink',
            LinkIconReferencePattern(SHORT_REF_RE, md,
                                     host=host, brands=brands),
            '<autolink'
        )

        md.inlinePatterns.add(
            'link_icon_tab_automail',
            LinkIconAutomailPattern(AUTOMAIL_RE, md,
                                    host=host, brands=brands),
            '<automail'
        )

        # md.inlinePatterns['link'] = \
        #     LinkIconLinkPattern(LINK_RE, md, host=host)
        #
        # md.inlinePatterns['reference'] = \
        #     LinkIconReferencePattern(REFERENCE_RE, md, host=host)
        #
        # md.inlinePatterns['short_reference'] = \
        #     LinkIconReferencePattern(SHORT_REF_RE, md, host=host)
        #
        # md.inlinePatterns['autolink'] = \
        #     LinkIconAutolinkPattern(AUTOLINK_RE, md, host=host)


def makeExtension(**kwargs):
    """Loads the extension."""
    return LinkIconTabExtension(host=kwargs.get('host', ''),
                                brands=kwargs.get('brands', None))

if __name__ == '__main__':
    import markdown
    logging.basicConfig(level=logging.DEBUG)

    # text = '[![img](img_link)](/some/link "try")'
    # text = '[<img src="">](/some/link "try")'
    text = (
        '[text](http://inner.com/t)\n\n'
        '[text](/inner)\n\n'
        '[text](http://outter.com)\n\n'
        '[text](https://github.com)\n\n'
        '[text](https://gist.github.com)\n\n'
        '[text](https://plus.google.com)\n\n'
        '[text](https://www.google.com)\n\n'
        '[ins](https://instagram.com/p)\n\n'
        '[tjc](https://together.jolla.com)\n\n'
        '[blogjolla](https://blog.jolla.com)\n\n'
        '<tylertempdev@gmail.com>\n\n'
        '[supportjolla](https://isupportjolla.com)\n\n'
    )

    LinkIconMixin.brands['jolla.com'] = 'iconfont icon-jolla'

    result = markdown.markdown(text, extensions=[makeExtension(host='inner.com')])
    print(result)
