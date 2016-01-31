"""
Image link wrapper for AmazeUI

Load this BEFORE link_icon_tab
"""
import re
import logging
import mimetypes
from markdown import Extension
from markdown.util import etree
from markdown.inlinepatterns import \
    ImagePattern, ImageReferencePattern, LinkPattern, ReferencePattern, \
    LINK_RE, SHORT_REF_RE, REFERENCE_RE, IMAGE_REFERENCE_RE, IMAGE_LINK_RE


logger = logging.getLogger('MARKDOWN.link_image')


# pylint: disable=invalid-name, too-few-public-methods
class LinkImageMixin(object):
    """Common extension logic; mixed into the existing classes."""
    _COM_IMAGE_LINK_RE = re.compile('^%s$' % IMAGE_LINK_RE)
    _COM_IMAGE_REFERENCE_RE = re.compile('^%s$' % IMAGE_REFERENCE_RE)

    def handleMatch(self, m):
        """Handles a match on a pattern; used by existing implementation."""

        elem = super(LinkImageMixin, self).handleMatch(m)
        if elem is None:
            return None

        mime, _ = mimetypes.guess_type(elem.get('href'))
        if not mime or not mime.startswith('image'):
            logger.debug('not image link wrapper')
            return None

        text = elem.text
        inside = self._get_inside_img(text)
        logger.debug(text)
        if inside is None:
            logger.debug('inside image not found')
            return None

        logger.debug(inside)
        src, alt, title = inside

        root = etree.Element('figure')
        root.set('data-am-widget', 'figure')
        root.set('class', 'am am-figure am-figure-default')
        root.set('data-am-figure', "{  pureview: 'true' }")

        source_img = etree.SubElement(root, 'img') # root.find('img')
        source_img.set('src', src)
        source_img.set('data-rel', elem.get('href'))
        if alt:
            source_img.set('alt', alt)
        if title:
            source_img.set('title', title)
            fig_caption = etree.SubElement(root, 'figcaption')
            fig_caption.set('class', 'am-figure-capition-btm')
            fig_caption.text = title
        return root

    def _get_inside_img(self, text):
        if self._COM_IMAGE_LINK_RE.match(text) is None:
            logger.debug('image ref inside not found')
            if self._COM_IMAGE_REFERENCE_RE.match(text) is None:
                logger.debug('image link inside not found')
                return None
            pattern = ImageReferencePattern(IMAGE_REFERENCE_RE, self.markdown)
        else:
            pattern = ImagePattern(IMAGE_LINK_RE, self.markdown)

        m = pattern.compiled_re.match(text)
        elem = pattern.handleMatch(m)
        src = elem.get('src')
        alt = elem.get('alt', None)
        title = elem.get('title', None)
        return src, alt, title


class LinkImageLinkPattern(LinkImageMixin, LinkPattern):
    """[![image](img_url)](link.jpg)"""
    pass


class LinkImageReferencePattern(LinkImageMixin, ReferencePattern):
    """[![image](img_url)][1] or [![image](img_url)][ref]"""
    pass


class LinkImageExtension(Extension):
    """Modifies HTML output to open links in a new tab."""

    def extendMarkdown(self, md, md_globals):
        # md.inlinePatterns['reference'] = LinkImageReferencePattern(
        #     REFERENCE_RE, md)
        #
        # md.inlinePatterns['link'] = LinkImageLinkPattern(
        #     LINK_RE, md)
        #
        # md.inlinePatterns['short_reference'] = LinkImageReferencePattern(
        #     SHORT_REF_RE, md)

        md.inlinePatterns.add(
            'link_image_reference',
            LinkImageReferencePattern(REFERENCE_RE, md), '<reference')

        md.inlinePatterns.add(
            'link_image', LinkImageLinkPattern(LINK_RE, md), '<link')

        md.inlinePatterns.add(
            'link_image_short_reference',
            LinkImageReferencePattern(SHORT_REF_RE, md), '<short_reference')


def makeExtension(**kwargs):
    """Loads the extension."""
    return LinkImageExtension(**kwargs)


if __name__ == '__main__':
    import markdown
    from amazedown import link_icon_tab
    logging.basicConfig(level=logging.DEBUG)

    text = """
[![img_alt](img_small.jpg img_title)][0]

[link](//external/)

[link](//inner/)


[0]:img_big.jpg
    """
    # text = '[<img src="">](/some/link "try")'
    # text = '[text](http://link.com/t)'
    result = markdown.markdown(text, extensions=[
        makeExtension(),
        link_icon_tab.makeExtension(host='inner'),
    ])
    print(result)
