import markdown
from amazedown.link_icon_tab import makeExtension
from unittest import TestCase


class TestNewHost(TestCase):

    def setUp(self):
        self.host = 'test.com'

    def _e(self, md, res):
        html = markdown.markdown(md,
                                 extensions=[makeExtension(host=self.host)])
        self.assertEqual(html, res)

    def _n(self, md, res):
        html = markdown.markdown(md,
                                 extensions=[makeExtension(host=self.host)])
        self.assertNotEqual(html, res)

    def test_same_host_link(self):
        self._e(
            '[text](http://%s/)' % self.host,
            '<p><a class="am-icon-link" href="http://%s/"> text</a></p>' % self.host,
        )


if __name__ == '__main__':
    from unittest import main
    main()