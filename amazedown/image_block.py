import re
import logging
from markdown.blockprocessors import BlockProcessor
from markdown import Extension
from markdown.util import etree

logger = logging.getLogger('MARKDOWN.image_block')


class ImageBlockProcesser(BlockProcessor):

    _IMG_RE = re.compile(
        r'^'
        r'!\[(?P<alt>[\s\S]*?)\]'  # ![] img alt
        r'('
            r'\('
                r'(?P<src>.+?)'
                r'(\s+'
                    r'(?P<title>.+?)'
                r')?\s?'
            r'\)'
        r'|'
            r'\[(?P<ref>.*?)\]'
        r')'
        r'$')

    def test(self, parent, block):
        # return True
        block = block.strip()
        logger.info(repr(block))
        self._matched = self._IMG_RE.match(block)

        return self._matched is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)

        matched = getattr(self, '_matched', None)
        if matched is None:
            matched = self._IMG_RE.match(block.rstrip())

        matched_dict = matched.groupdict()
        logger.debug(matched_dict)

        src = matched_dict['src']
        title = matched_dict['title']
        if src is None:
            ref = matched_dict['ref']
            if ref is None or ref not in self.parser.markdown.references:
                logger.debug('no ref found')
                blocks.insert(0, block)
                return False

            src, title = self.parser.markdown.references[ref]

        root = etree.SubElement(parent, 'figure')
        root.set('data-am-widget', 'figure')
        root.set('class', 'am am-figure am-figure-default')
        root.set('data-am-figure', "{  pureview: 'true' }")

        source_img = etree.SubElement(root, 'img')  # root.find('img')
        source_img.set('src', src)
        if matched_dict['alt']:
            source_img.set('alt', matched_dict['alt'])
        if title:
            source_img.set('title', title)
            fig_caption = etree.SubElement(root, 'figcaption')
            fig_caption.set('class', 'am-figure-capition-btm')
            fig_caption.text = title

        return True


class ImageBlockExtension(Extension):
    """ Add definition lists to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of DefListProcessor to BlockParser. """
        md.parser.blockprocessors.add('image_block',
                                      ImageBlockProcesser(md.parser),
                                      '>empty')
        # md.parser.blockprocessors['paragraph'] = \
        #                               LinkImageBlockProcesser(md.parser)



def makeExtension(configs=None):
    if configs is None:
        configs = {}
    return ImageBlockExtension(configs=configs)


if __name__ == '__main__':
    import markdown
    logging.basicConfig(level=logging.DEBUG, format='\033[32m%(levelname)1.1s\033[0m[%(lineno)3s]%(msg)s')

    md = """
![img](imglink imgtitle)]

![img][img-id]

![img][0]

![img][img-id]

![img][0]

[0]: link
[1]: link-1.jpg
[img-id]: pic2.jpg
"""

#     md = """
# [![img](imglink)](http://link)
# [![img](imglink)](<http://link>)
# [![img](imglink)](http://link "title")
# [![img](imglink)](http://link 'title')
#     """
#
#     md = """
# [![img](imglink)](http://link)-
# [![img](imglink)](<http://link>)
#     """

#     md = """[![img][0]](http://link "title")
#
# [0]: link-0.jpg
#     """

    # md = """[![img](imglink
    # img title)](http://link "title")"""
    # md = '[![img][img-id]](<http://link.com/pic.jpg>)'
    print(markdown.markdown(md, extensions=[makeExtension()]))
    # print(markdown.markdown(md))
