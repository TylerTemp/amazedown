import re
from markdown.blockprocessors import BlockQuoteProcessor
from markdown import Extension
from markdown import util
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
    md = """
> 基于芬兰日报的各方消息，Sailfish系统开发方Jolla公司陷入财政危机。
> 据今日消息，公司将随之开始大量裁员。
>
> 目前有超过100名员工在为Jolla工作。宣传主管Juhani Lassila已确认将有超过一半的员工
> 将被裁员。Lassila表示，不管困难如何，他们都打算保证寄送用户的Jolla平板。
> 裁员并不是这件事的影响因素。
>
> _“我们将在近期发布财政状况的变更信息。我们目前暂时使用一轮轮资，这轮资金本应在11月中止。”_
> Lassila如是说。
>
> 在2014到2015年，Jolla已经有4起总共近1000欧元的支付拖欠纪录。
>
> Suomen perintätoimisto（收税员）和失业保险基金（政府基金）的Intrum Justitia（收税员）
> 对此提出了起诉。根据资金注册信息显示，这些费用还有一项尚未偿还：在2014年已经降到500欧元
> 的失业保险基金未偿贷款。[^1]
>
> Jolla宣传主管Juhani Lassila称他并不清楚这些纪录。
>
> -- 原文自芬兰晨报，Taneli Koponen
> -- 英文翻译自Review Jolla，Simo Ruoho
        """

    result = markdown.markdown(md, extensions=[makeExtension()])
    print(result)