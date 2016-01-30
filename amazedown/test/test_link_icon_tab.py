import markdown
from amazedown.link_icon_tab import makeExtension
from unittest import TestCase, main


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

    def test_same_host_ref(self):
        self._e(
            '[test][0]\n\n[0]:http://%s/link/' % self.host,
            '<p><a class="am-icon-link" href="http://%s/link/"> test</a></p>' % self.host
        )

    def test_same_host_quick(self):
        self._e(
            '<http://%s/here/>' % self.host,
            '<p><a class="am-icon-link" href="http://%s/here/"> http://%s/here/</a></p>' % (self.host, self.host)
        )

    def test_no_host_link(self):
        self._e(
            '[text](/somewhere)',
            '<p><a class="am-icon-link" href="/somewhere"> text</a></p>',
        )

    def test_no_host_ref(self):
        self._e(
            '[test][0]\n\n[0]:/link/',
            '<p><a class="am-icon-link" href="/link/"> test</a></p>'
        )

    def test_diff_host_link(self):
        self._e(
            '[text](http://md.com/)',
            '<p><a href="http://md.com/" target="_blank">text <span class="am-icon-external-link"></span></a></p>'
        )

    def test_diff_host_ref(self):
        self._e(
            '[test][0]\n\n[0]:http://md.com/link/',
            '<p><a href="http://md.com/link/" target="_blank">test <span class="am-icon-external-link"></span></a></p>'
        )

    def test_diff_host_quick(self):
        self._e(
            '<http://md.com/here/>',
            '<p><a href="http://md.com/here/" target="_blank">http://md.com/here/ <span class="am-icon-external-link"></span></a></p>'
        )

    def _skip(self, md):
        self.assertEqual(
            markdown.markdown(md),
            markdown.markdown(md, extensions=[makeExtension(host=self.host)])
        )

    def test_skip_md_img(self):
        md = '[![](img_link)](link)'
        self._skip(md)

    def test_skip_html_img(self):
        md = '[<img src="img_link" />](link)'
        self._skip(md)


if __name__ == '__main__':
    main()