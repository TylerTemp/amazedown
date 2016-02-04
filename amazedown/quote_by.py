import re
from markdown.blockprocessors import BlockQuoteProcessor
from markdown import Extension
from markdown import util
import logging

logger = logging.getLogger('MARKDOWN.quote_by')


class QuoteByProcessor(BlockQuoteProcessor):
    BY_RE = re.compile(r'(?P<pre>\n[ ]{0,3}>[ ]*)'
                       r'(-- ?|—— ?)'
                       r'(?P<name>.*?)'
                       r'(?P<end>\s*$)')

    def run(self, parent, blocks):
        logger.debug(blocks[0])
        blocks[0] = self.BY_RE.sub(
            r'\g<pre><small>\g<name></small>\g<end>',
            blocks[0])
        return super(QuoteByProcessor, self).run(parent, blocks)


class QuoteByExtension(Extension):
    """ Add definition lists to Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of DefListProcessor to BlockParser. """
        md.parser.blockprocessors.add('quote_by',
                                      QuoteByProcessor(md.parser),
                                      '<quote')


def makeExtension(configs=None):
    if configs is None:
        configs = {}
    return QuoteByExtension(configs=configs)


if __name__ == '__main__':
    import markdown
    logging.basicConfig(
        level=logging.DEBUG,
        format='\033[32m%(levelname)1.1s\033[0m[%(lineno)3s]%(message)s')

    md = """
> sth
> goes -goes
> --here

> sth
> goes -goes
> --here

>
> -- here

>
> - here

>
> —— here

>
> ——here

>
> — here

>
> —here
        """

    result = markdown.markdown(md, extensions=[makeExtension()])
    print(result)