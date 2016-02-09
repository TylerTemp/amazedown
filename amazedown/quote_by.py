import re
from markdown.blockprocessors import BlockQuoteProcessor
from markdown import Extension
import logging

logger = logging.getLogger('MARKDOWN.quote_by')


class QuoteByProcessor(BlockQuoteProcessor):
    BY_RE = re.compile(r'(?P<pre>[ ]{0,3}>[ ]*)'
                       r'(-- ?|—— ?)'
                       r'(?P<name>.*)'
                       )

    def run(self, parent, blocks):
        block = blocks[0]
        reversed_line_result = []
        BY_RE = self.BY_RE
        no_more = False
        line_count = 0
        for each_line in block.splitlines()[::-1]:
            if no_more:
                reversed_line_result.append(each_line)
                continue

            logger.debug(each_line)
            match = BY_RE.match(each_line)
            if match:
                each_line = match.expand('\g<pre><small>\g<name></small>')
                line_count += 1
            else:
                no_more = True

            reversed_line_result.append(each_line)

        line_result = reversed_line_result[::-1]
        sep_at = len(line_result) - line_count
        raw_result = line_result[:sep_at]
        by_result = line_result[sep_at:]
        raw = '\n'.join(raw_result)
        by = '<br/>\n'.join(by_result)
        logger.debug(raw)
        logger.debug(by)

        blocks[0] = '%s\n%s' % (raw, by)
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