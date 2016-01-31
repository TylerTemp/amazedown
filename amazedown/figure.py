import logging
from markdown import Extension
from markdown.util import etree
from markdown.inlinepatterns import \
    ImagePattern, ImageReferencePattern, IMAGE_REFERENCE_RE, IMAGE_LINK_RE

logger = logging.getLogger('MARKDOWN.figure')


class FigureMixin(object):

    def handleMatch(self, m):
        elem = super(FigureMixin, self).handleMatch(m)
        if elem.tag != 'img':
            return elem

        title = elem.get('title', None)

        root = etree.Element('figure')
        root.set('data-am-widget', 'figure')
        root.set('class', 'am am-figure am-figure-default')
        root.set('data-am-figure', "{  pureview: 'true' }")
        root.append(elem)

        if title:
            fig_caption = etree.SubElement(root, 'figcaption')
            fig_caption.set('class', 'am-figure-capition-btm')
            fig_caption.text = title
        return root


class FigurePattern(FigureMixin, ImagePattern):
    pass


class FigureReferencePattern(FigureMixin, ImageReferencePattern):
    pass


class FigureExtension(Extension):

    def extendMarkdown(self, md, md_globals):

        md.inlinePatterns.add(
            'figure_link',
            FigurePattern(IMAGE_LINK_RE, md), '<image_link')

        md.inlinePatterns.add(
            'figure_reference',
            FigureReferencePattern(IMAGE_REFERENCE_RE, md), '<image_reference')


def makeExtension(**kwargs):
    """Loads the extension."""
    return FigureExtension(**kwargs)


if __name__ == '__main__':
    import markdown
    logging.basicConfig(level=logging.DEBUG)

    text = """
![img_alt](img_link.jpg img_title)

![img_alt][0]

[0]: img_ref.jpg "img_ref_title"
    """
    # text = '[<img src="">](/some/link "try")'
    # text = '[text](http://link.com/t)'
    result = markdown.markdown(text, extensions=[
        makeExtension(),
    ])
    print(result)
