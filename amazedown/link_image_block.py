import re
import logging
import mimetypes
from markdown.blockprocessors import BlockProcessor
from markdown import Extension
from markdown.util import etree

logger = logging.getLogger('MARKDOWN.link_image_block')


class LinkImageBlockProcesser(BlockProcessor):

    _LINK_IMG_RE = re.compile(r'^'
                              r'\[\s?'
                                   r'!\[(?P<alt>[\s\S]*?)\]'  # ![] img alt
                                   r'('
                                       r'\('
                                           r'(?P<src>.+?)'
                                           r'(\s+'
                                               r'(?P<img_title>.+?)'
                                           r')?\s?'
                                       r'\)'
                                   r'|'
                                       r'\[(?P<img_ref>.*?)\]'
                                   r')'  # img src
                              r'\s?\]' # [] link text
                              r'('
                                   r'\('
                                        r'(?P<href>.*?)'
                                        r"""(\s+['"]"""
                                            r'(?P<title>.+?)'
                                        r"""['"])?\s?"""
                                   r'\)'  # () link link & title
                              r'|'  # or
                                  r'\[(?P<ref>.+?)\]'  # [] link ref
                              r')'
                              r'$')

    def test(self, parent, block):
        # return True
        block = block.strip()
        logger.info(repr(block))
        self._matched = self._LINK_IMG_RE.match(block)

        return self._matched is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)

        matched = getattr(self, '_matched', None)
        if matched is None:
            matched = self._LINK_IMG_RE.match(block.rstrip())

        matched_dict = matched.groupdict()
        logger.debug(matched_dict)

        href = matched_dict['href']
        link_title = matched_dict['title']

        if href is None:
            ref = matched_dict['ref']
            if ref is None or ref not in self.parser.markdown.references:
                logger.debug('no ref found')
                blocks.insert(0, block)
                return False

            href, link_title = self.parser.markdown.references[ref]

        elif href.startswith('<'):
            href = href[1:-1]

        href_mime = mimetypes.guess_type(href)[0]
        if href_mime is None or not href_mime.startswith('image'):
            logger.debug('%s not image', href)
            blocks.insert(0, block)
            return False

        src = matched_dict['src']
        img_title = matched_dict['img_title']
        if src is None:
            img_ref = matched_dict['img_ref']
            if img_ref is None or img_ref not in self.parser.markdown.references:
                logger.debug('no ref found')
                blocks.insert(0, block)
                return False

            src, img_title = self.parser.markdown.references[img_ref]

        img_title = img_title or link_title

        root = etree.SubElement(parent, 'figure')
        root.set('data-am-widget', 'figure')
        root.set('class', 'am am-figure am-figure-default')
        root.set('data-am-figure', "{  pureview: 'true' }")

        source_img = etree.SubElement(root, 'img')  # root.find('img')
        source_img.set('src', src)
        source_img.set('data-rel', href)
        if matched_dict['alt']:
            source_img.set('alt', matched_dict['alt'])
        if img_title:
            source_img.set('title', img_title)
            fig_caption = etree.SubElement(root, 'figcaption')
            fig_caption.set('class', 'am-figure-capition-btm')
            fig_caption.text = img_title

        return True


class LinkImageBlockExtension(Extension):
    """ Add definition lists to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of DefListProcessor to BlockParser. """
        md.parser.blockprocessors.add('link_image_block',
                                      LinkImageBlockProcesser(md.parser),
                                      '>empty')


def makeExtension(configs=None):
    if configs is None:
        configs = {}
    return LinkImageBlockExtension(configs=configs)


if __name__ == '__main__':
    import markdown
    logging.basicConfig(level=logging.DEBUG, format='\033[32m%(levelname)1.1s\033[0m[%(lineno)3s]%(msg)s')

    md = """
[![img](imglink imgtitle)](link.jpg)

[![img][img-id]](<http://link.com/pic.jpg>)

[![img][0]](link.png 'title')

[![img][img-id]][link]

[
![im
g][0]
][1]


[0]: link
[1]: link-1.jpg
[img-id]: pic2.jpg
[link]: some.jpg
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
