"""
Link for AmazeUI


Some codes are from: [markdown-newtab](https://github.com/Undeterminant/markdown-newtab/)
"""
import re
import logging
from markdown import Extension
from markdown.inlinepatterns import \
    LinkPattern, ReferencePattern, AutolinkPattern, \
    LINK_RE, REFERENCE_RE, SHORT_REF_RE, AUTOLINK_RE, IMAGE_LINK_RE, IMAGE_REFERENCE_RE

try:
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import urlsplit

logger = logging.getLogger('MARKDOWN.link_icon_tab')


# pylint: disable=invalid-name, too-few-public-methods
class LinkIconMixin(object):
    """Common extension logic; mixed into the existing classes."""

    _IMG_RE = re.compile(''.join(('^', IMAGE_LINK_RE, '$|^', IMAGE_REFERENCE_RE, '$|^<img\s.*?>$')))

    def __init__(self, *args, **kwargs):
        self._host = kwargs.pop('host', None)
        super(LinkIconMixin, self).__init__(*args, **kwargs)
        logger.debug(self._host)

    def handleMatch(self, match):
        """Handles a match on a pattern; used by existing implementation."""
        
        elem = super(LinkIconMixin, self).handleMatch(match)
        if self._host is None:
            return elem

        text = elem.text
        if elem is not None and not self._IMG_RE.match(text):
            link = elem.get('href')
            parsed = urlsplit(link)
            if parsed.netloc in (self._host, ''):
                elem.set('class', 'am-icon-link')
                elem.text = ' ' + text
            else:
                elem.text += ' <span class="am-icon-external-link"></span>'
                elem.set('target', '_blank')
        return elem


class LinkIconLinkPattern(LinkIconMixin, LinkPattern):
    """Links to URLs, e.g. [link](https://duck.co)."""
    pass



class LinkIconReferencePattern(LinkIconMixin, ReferencePattern):
    """Links to references, e.g. [link][1]."""
    pass



class LinkIconAutolinkPattern(LinkIconMixin, AutolinkPattern):
    """Autommatic links, e.g. <duck.co>."""
    pass


class LinkIconTabExtension(Extension):
    """Modifies HTML output to open links in a new tab."""

    def __init__(self, **kwargs):
        self.config = {'host': [kwargs.get('host', None), 'host name']}
        super(LinkIconTabExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        host = self.getConfig('host', None)

        md.inlinePatterns['link'] = \
            LinkIconLinkPattern(LINK_RE, md, host=host)

        md.inlinePatterns['reference'] = \
            LinkIconReferencePattern(REFERENCE_RE, md, host=host)

        md.inlinePatterns['short_reference'] = \
            LinkIconReferencePattern(SHORT_REF_RE, md, host=host)

        md.inlinePatterns['autolink'] = \
            LinkIconAutolinkPattern(AUTOLINK_RE, md, host=host)


def makeExtension(**kwargs):
    """Loads the extension."""
    return LinkIconTabExtension(host=kwargs.get('host', None))

if __name__ == '__main__':
    import markdown
    logging.basicConfig(level=logging.DEBUG)

    # text = '[![img](img_link)](/some/link "try")'
    # text = '[<img src="">](/some/link "try")'
    text = '[text](http://link.com/t)'
    result = markdown.markdown(text, extensions=[makeExtension(host='link.com')])
    print(result)
