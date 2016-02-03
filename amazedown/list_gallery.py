"""
format(No nest, ONLY ACCEPT "-"):

    -   ![img](link "title")
    -   [![img2](preview-link)](link "title2")

result:

     <ul data-am-widget="gallery" class="am-gallery am-avg-sm-1 am-gallery-bordered" data-am-gallery="{pureview:{target: 'a', weChatImagePreview: false}}" >
       <li>
         <div class="am-gallery-item">
           <a href="link">
             <img src="link" alt="img"/>
             <h6 class="am-gallery-title">title</h6>
           </a>
         </div>
       </li>
       <li>
         <div class="am-gallery-item">
           <a href="link">
             <img src="preview-link"  alt="img2"/>
             <h6 class="am-gallery-title">title2</h6>
           </a>
         </div>
       </li>
     </ul>
"""

import logging
from markdown.blockprocessors import BlockProcessor
from markdown import Extension
from markdown.util import etree
from amazedown.image_block import ImageBlockProcesser
from amazedown.link_image_block import LinkImageBlockProcesser

logger = logging.getLogger('MARKDOWN.list_gallery')


class ListGalleryProcesserProcesser(BlockProcessor):
    _IMG_RE = ImageBlockProcesser._IMG_RE
    _LINK_IMG_RE = LinkImageBlockProcesser._LINK_IMG_RE

    def test(self, parent, block):
        if not block.startswith('-') or len(block) < 2:
            return None

        result = self._match_result = self._formal(block)
        if result is None:
            return False
        logger.debug(result)
        return True

    def run(self, parent, blocks):
        result = getattr(self, '_match_result', None)
        if not result:
            result = self._formal(blocks[0])

        blocks.pop(0)

        root = etree.SubElement(parent, 'ul')
        root.set('data-am-widget', 'gallery')
        root.set('class', 'am-gallery am-avg-sm-1 am-gallery-bordered')
        root.set('data-am-gallery',
                 "{pureview:{target: 'a', weChatImagePreview: false}}")
        for each in result:
            # {'preview': 'link4', 'src': 'pre-link4', 'title': None}
            item = etree.SubElement(root, 'li')
            container = etree.SubElement(item, 'div')
            container.set('class', 'am-gallery-item')

            preview_link = etree.SubElement(container, 'a')
            preview_link.set('href', each['preview'] or each['src'])

            img = etree.SubElement(preview_link, 'img')
            img.set('src', each['src'])

            if each['alt']:
                img.set('alt', each['alt'])

            if each['title']:
                img.set('title', each['title'])
                title = etree.SubElement(preview_link, 'h6')
                title.set('class', "am-gallery-title")
                title.text = each['title']

        return True

    def _formal(self, block):
        items = block.split('\n-')
        items[0] = items[0][1:]
        result = []
        for item in items:
            item = item.lstrip()
            logger.debug(repr(item))
            matched = self._IMG_RE.match(item)
            if matched:
                group_dict = matched.groupdict()
                preview = None
                src = group_dict['src']
                title = group_dict['title']
                if src is None:
                    ref = group_dict['ref']
                    if (ref is None or
                                ref not in self.parser.markdown.references):
                        logger.debug('ref not found')
                        return None
                    src, title = self.parser.markdown.references[ref]

            else:
                matched = self._LINK_IMG_RE.match(item)
                if not matched:
                    logger.debug('none matched')
                    return None

                group_dict = matched.groupdict()

                preview = group_dict['href']
                link_title = group_dict['title']

                if preview is None:
                    ref = group_dict['ref']
                    if (ref is None or
                                ref not in self.parser.markdown.references):
                        return None

                    preview, link_title = self.parser.markdown.references[ref]

                elif preview.startswith('<'):
                    preview = preview[1:-1]

                src = group_dict['src']
                img_title = group_dict['img_title']
                if src is None:
                    img_ref = group_dict['img_ref']
                    if (img_ref is None or
                                img_ref not in self.parser.markdown.references):
                        logger.debug('no ref found')
                        return None

                    src, img_title = self.parser.markdown.references[img_ref]

                title = img_title or link_title

            result.append({'src': src, 'preview': preview, 'title':title,
                           'alt': group_dict['alt']})
            logger.debug(result[-1])

        return result

class ListGalleryExtension(Extension):
    """ Add definition lists to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of DefListProcessor to BlockParser. """
        md.parser.blockprocessors.add('list_gallery',
                                      ListGalleryProcesserProcesser(md.parser),
                                      '<ulist')


def makeExtension(configs=None):
    if configs is None:
        configs = {}
    return ListGalleryExtension(configs=configs)


if __name__ == '__main__':
    import markdown
    logging.basicConfig(
        level=logging.DEBUG,
        format='\033[32m%(levelname)1.1s\033[0m[%(lineno)3s]%(msg)s')

    md = """
-   ![im
g1](link1 title1)
-   [![i
    mg2](pre-link2)](link2 "title2")
-   ![img3][ref3]
-   [![img4][ref4]][link4]

[ref3]: link3
[ref4]: pre-link4
[link4]: link4
    """

    print(markdown.markdown(md, extensions=[makeExtension()]))
    # print(markdown.markdown(md))
