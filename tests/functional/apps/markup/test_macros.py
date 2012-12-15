#-*- coding: utf-8 -*-
from django.test import TestCase

from inyoka.wiki.models import Page
from inyoka.markup import parse, RenderContext


class TestMacros(TestCase):

    def test_missing_link_in_picture_ticket_635(self):
        page = Page(name='Something')
        parse("[[Bild(Bildname, 1)]]").render(RenderContext(wiki_page=page),
                                              format='html')

    def test_toc_indention_ticket_688(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
== Stufe 2 (5) ==
text""").render(RenderContext(), format='html')
        new_html = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li><li><a href="#Stufe-2-5" class="crosslink">Stufe 2 (5)
</a></li></ol></li></ol>"""
        self.assertIn(new_html, html)

    def test_toc_continuous_indent_no_crop(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_continuous_indent_crop_one(self):
        html = parse("""[[Inhaltsverzeichnis(3)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_continuous_indent_crop_multiple(self):
        html = parse("""[[Inhaltsverzeichnis(2)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_indent_one_missing_middle(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_indent_multiple_missing_middle(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_indent_one_missing_begin(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_indent_multiple_missing_begin(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li style="list-style: none"><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_continuous_unindent_no_crop(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text
== Stufe 2 (2) ==
text
= Stufe 1 (2) =
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li><li><a href="#Stufe-2-2" class="crosslink">Stufe 2 (2)
</a></li></ol></li><li><a href="#Stufe-1-2" class="crosslink">Stufe 1 (2)
</a></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_continuous_unindent_crop_one(self):
        html = parse("""[[Inhaltsverzeichnis(3)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text
== Stufe 2 (2) ==
text
= Stufe 1 (2) =
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li><li><a href="#Stufe-2-2" class="crosslink">Stufe 2 (2)
</a></li></ol></li><li><a href="#Stufe-1-2" class="crosslink">Stufe 1 (2)
</a></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_continuous_unindent_crop_multiple(self):
        html = parse("""[[Inhaltsverzeichnis(2)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text
== Stufe 2 (2) ==
text
= Stufe 1 (2) =
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a></li><li><a href="#Stufe-2-2" class="crosslink">Stufe 2 (2)
</a></li></ol></li><li><a href="#Stufe-1-2" class="crosslink">Stufe 1 (2)
</a></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_unindent_one_missing_middle(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text
= Stufe 1 (2) =
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li></ol></li><li><a href="#Stufe-1-2" class="crosslink">Stufe 1 (2)
</a></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_unindent_multiple_missing_middle(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
= Stufe 1 (2) =
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li></ol></li><li><a href="#Stufe-1-2" class="crosslink">Stufe 1 (2)
</a></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_unindent_one_missing_end(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text
== Stufe 2 (2) ==
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li><li><a href="#Stufe-2-2" class="crosslink">Stufe 2 (2)
</a></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_unindent_multiple_missing_end(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

    def test_toc_broken_indent_and_unindent(self):
        html = parse("""[[Inhaltsverzeichnis(10)]]
== Stufe 2 (1) ==
text
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
== Stufe 2 (2) ==
text
= Stufe 1 (2) =
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-2-1" class="crosslink">Stufe 2 (1)
</a><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li></ol></li><li><a href="#Stufe-2-2" class="crosslink">Stufe 2 (2)
</a></li></ol></li><li><a href="#Stufe-1-2" class="crosslink">Stufe 1 (2)
</a></li></ol>"""
        self.assertIn(html_assert, html)

        html = parse("""[[Inhaltsverzeichnis(10)]]
= Stufe 1 (1) =
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text
== Stufe 2 (2) ==
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li><a href="#Stufe-1-1" class="crosslink">Stufe 1 (1)
</a><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li><li><a href="#Stufe-2-2" class="crosslink">Stufe 2 (2)
</a></li></ol></li></ol>"""
        self.assertIn(html_assert, html)

        html = parse("""[[Inhaltsverzeichnis(10)]]
=== Stufe 3 (1) ===
text
==== Stufe 4 (1) ====
text
=== Stufe 3 (2) ===
text""").render(RenderContext(), format='html')
        html_assert = """<ol class="arabic"><li style="list-style: none"><ol class="arabic"><li style="list-style: none"><ol class="arabic"><li><a href="#Stufe-3-1" class="crosslink">Stufe 3 (1)
</a><ol class="arabic"><li><a href="#Stufe-4-1" class="crosslink">Stufe 4 (1)
</a></li></ol></li><li><a href="#Stufe-3-2" class="crosslink">Stufe 3 (2)
</a></li></ol></li></ol></li></ol>"""
        self.assertIn(html_assert, html)