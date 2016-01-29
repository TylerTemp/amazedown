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
class NewTabMixin(object):
    """Common extension logic; mixed into the existing classes."""

    _IMG_RE = re.compile(''.join(('^', IMAGE_LINK_RE, '$|^', IMAGE_REFERENCE_RE, '$|^<img\s.*?>$')))

    def __init__(self, *args, **kwargs):
        self._host = kwargs.pop('host', None)
        super(NewTabMixin, self).__init__(*args, **kwargs)
        logger.debug(self._host)

    def handleMatch(self, match):
        """Handles a match on a pattern; used by existing implementation."""
        
        elem = super(NewTabMixin, self).handleMatch(match)
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


class NewTabLinkPattern(NewTabMixin, LinkPattern):
    """Links to URLs, e.g. [link](https://duck.co)."""
    pass



class NewTabReferencePattern(NewTabMixin, ReferencePattern):
    """Links to references, e.g. [link][1]."""
    pass



class NewTabAutolinkPattern(NewTabMixin, AutolinkPattern):
    """Autommatic links, e.g. <duck.co>."""
    pass


class NewTabExtension(Extension):
    """Modifies HTML output to open links in a new tab."""

    def __init__(self, **kwargs):
        self.config = {'host': [kwargs.get('host', None), 'host name']}
        super(NewTabExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        host = self.getConfig('host', None)

        md.inlinePatterns['link'] = \
            NewTabLinkPattern(LINK_RE, md, host=host)

        md.inlinePatterns['reference'] = \
            NewTabReferencePattern(REFERENCE_RE, md, host=host)

        md.inlinePatterns['short_reference'] = \
            NewTabReferencePattern(SHORT_REF_RE, md, host=host)

        md.inlinePatterns['autolink'] = \
            NewTabAutolinkPattern(AUTOLINK_RE, md, host=host)


def makeExtension(**kwargs):
    """Loads the extension."""
    return NewTabExtension(host=kwargs.get('host', None))

if __name__ == '__main__':
    import markdown
    logging.basicConfig(level=logging.DEBUG)

    # text = '[![img](img_link)](/some/link "try")'
    # text = '[<img src="">](/some/link "try")'
    text = '[text](http://link.com/t)'
    result = markdown.markdown(text, extensions=[makeExtension(host='link.com')])
    print(result)
