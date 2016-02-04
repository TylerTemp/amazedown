"""
format(No nest):

    -   +   *   [![img1](preview-link)](link "title2")
                [![img2](preview-link)](link "title2")
            *   [![img3](preview-link)](link "title2")
                [![img4](preview-link)](link "title2")
        +   *   [![img5](preview-link)](link "title2")
                [![img6](preview-link)](link "title2")
            *   [![img7](preview-link)](link "title2")
                [![img8](preview-link)](link "title2")
    -   +   *   [![img9](preview-link)](link "title2")
                [![img10](preview-link)](link "title2")
            *   [![img11](preview-link)](link "title2")
                [![img12](preview-link)](link "title2")
        +   *   [![img13](preview-link)](link "title2")
                [![img14](preview-link)](link "title2")
            *   [![img15](preview-link)](link "title2")
                [![img16](preview-link)](link "title2")

result:

     <ul data-am-widget="gallery" class="am-gallery am-avg-sm-{*} am-avg-md-{+} am-avg-lg-{-} am-gallery-bordered" data-am-gallery="{pureview:{target: 'a', weChatImagePreview: false}}" >
       <li>
         <div class="am-gallery-item">
           <a href="link">
             <img src="preview-link"  alt="img2"/>
             <h6 class="am-gallery-title">title2</h6>
           </a>
         </div>
       </li>
       ...
     </ul>
"""

import re
import logging
from markdown.blockprocessors import BlockProcessor
from markdown import Extension
from markdown.util import etree

logger = logging.getLogger('MARKDOWN.list_gallery')


class ListGalleryProcesserProcesser(BlockProcessor):
    # _IMG_RE = ImageBlockProcesser._IMG_RE
    # _LINK_IMG_RE = LinkImageBlockProcesser._LINK_IMG_RE

    _IMG_RE = re.compile(

          r'\[\s?'
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
               r')'  # img src
          r'\s?\]' # [] link text
          r'('
               r'\('
                    r'(?P<preview>.*?)'
                    r"""(\s+['"]"""
                        r'(?P<preview_title>.+?)'
                    r"""['"])?\s?"""
               r'\)'  # () link link & title
          r'|'  # or
              r'\[(?P<preview_ref>.+?)\]'  # [] link ref
          r')'

        r'|'

            r'!\[(?P<alt2>[\s\S]*?)\]'  # ![] img alt
            r'('
                r'\('
                    r'(?P<src2>.+?)'
                    r'(\s+'
                        r'(?P<title2>.+?)'
                    r')?\s?'
                r'\)'
            r'|'
                r'\[(?P<ref2>.*?)\]'
            r')'

    )

    _LEADING = re.compile(r'[\+\-\*]')
    _EMPTY = re.compile(r'^[\n\ ]*$')

    def test(self, parent, block):
        if not block.startswith('-') or len(block) < 2:
            return None

        logger.debug(block)

        result = self._raw_result = self._formal(block)

        return bool(result)

    def run(self, parent, blocks):
        result = getattr(self, '_raw_result', None)
        if not result:
            result = self._formal(blocks[0])

        blocks.pop(0)

        levels = self._parse_level(x['level'] for x in result)
        if levels is None:
            logger.debug('level failed')
            return False

        logger.debug('get levels %s', levels)

        large, middle, small = levels

        small = small or 1

        wrapper = etree.SubElement(parent, 'div')
        root = etree.SubElement(wrapper, 'ul')
        root.set('data-am-widget', 'gallery')

        classes = ['am-gallery', 'am-gallery-bordered',
                   'am-avg-sm-%s ' % small]

        if middle:
            classes.append('am-avg-md-%s' % middle)
        if large:
            classes.append('am-avg-lg-%s' % large)

        root.set('class', ' '.join(classes))

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
        prev_end = None
        results = []
        refs = self.parser.markdown.references
        for each in self._IMG_RE.finditer(block):
            this_result = {}
            this_start, this_end = each.span(0)
            if prev_end is None:
                prev = 0
            else:
                prev = prev_end

            leading = block[prev: this_start]
            space, count = self._LEADING.subn(' ', leading)
            logger.debug(repr(space))
            logger.debug(self._EMPTY.match(space))
            if not self._EMPTY.match(space) or count > 3:
                logger.debug('leading failed %s / %s', leading, count)
                return None

            this_result['level'] = count

            prev_end = this_end

            group_dict = each.groupdict()

            alt = group_dict['alt'] or group_dict['alt2']
            title = (group_dict['title'] or
                     group_dict['title2'] or
                     group_dict['preview_title'])
            src = group_dict['src'] or group_dict['src2']
            if not src:
                ref = group_dict['ref'] or group_dict['ref2']
                if ref is None or ref not in refs:
                    return None

                src, title = refs[ref]

            preview_ref = group_dict['preview_ref']
            if preview_ref:
                if preview_ref not in refs:
                    return None

                preview, _title = refs[preview_ref]
                if title is None:
                    title = _title
            else:
                preview = group_dict['preview']

            this_result['alt'] = alt
            this_result['title'] = title
            this_result['src'] = src
            this_result['preview'] = preview or src

            results.append(this_result)
            logger.debug(this_result)

        return results

    def _parse_level(self, levels):
        level = [0, 0, 0] # l, m, s

        loop = []
        for index, each in enumerate(levels):
            if loop and loop[0] == each:
                break

            loop.append(each)

        first = loop.pop(0)
        loop.append(first)
        if first == 3:
            gap_limit = 2
        else:
            gap_limit = 1

        for index, each in enumerate(loop, 1):
            logger.debug(each)
            gap = first - each
            if gap > gap_limit or level[gap] != 0:
                continue

            level[gap] = index
            logger.info((index, each, gap, level))

        logger.debug(level)
        return level


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
        format='\033[32m%(levelname)1.1s\033[0m[%(lineno)3s]%(message)s')

    md = """
-   +   *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
        *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
    +   *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
        *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
    +   *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
        *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
-   +   *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
        *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
    +   *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
        *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
    +   *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
        *   [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
            [![img2](preview-link)](link "title2")
    """


#     md = """
# -   *   [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#     *   [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
# -   *   [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#     *   [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#         [![img2](preview-link)](link "title2")
#     """

    result = markdown.markdown(md, extensions=[makeExtension()])
    # result = markdown.markdown(md)

    print(result)
