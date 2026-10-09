import re
import unicodedata

from markupsafe import Markup, escape

from odoo import api, models
from odoo.tools import html2plaintext

SEARCH_LIMIT = 5000
SNIPPET_RADIUS = 90


def fold(text):
    """Lowercase without accents, one character for one: indexes stay valid."""
    folded = []
    for char in text:
        base = "".join(
            c for c in unicodedata.normalize("NFD", char) if not unicodedata.combining(c)
        )
        folded.append((base or char)[0].lower())
    return "".join(folded)


def terms_of(query):
    return [term for term in fold(query or "").split() if len(term) > 1]


def highlight(text, terms):
    """Escaped text with every term occurrence wrapped in <mark>."""
    folded = fold(text)
    spans = []
    for term in terms:
        spans += [(m.start(), m.end()) for m in re.finditer(re.escape(term), folded)]
    spans.sort()
    parts, position = [], 0
    for start, end in spans:
        if start < position:
            continue
        parts.append(escape(text[position:start]))
        parts.append(Markup("<mark>%s</mark>") % text[start:end])
        position = end
    parts.append(escape(text[position:]))
    return Markup("").join(parts)


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model
    def maison_search(self, query, limit=30):
        """Pages whose title or current content holds every word of the query.

        Accents and case are ignored. Title matches rank first, then the
        number of occurrences, then the most recent pages.
        """
        terms = terms_of(query)
        if not terms:
            return []
        pages = self.search([("type", "=", "content")], limit=SEARCH_LIMIT)
        results = []
        for page in pages:
            title = page.name or ""
            text = " ".join(
                html2plaintext(page.content or "", include_references=False).split()
            )
            folded_title, folded_text = fold(title), fold(text)
            if not all(t in folded_title or t in folded_text for t in terms):
                continue
            score = sum(
                10 * folded_title.count(t) + folded_text.count(t) for t in terms
            )
            if fold(" ".join(query.split())) in folded_title:
                score += 50
            results.append((score, page.write_date, page, title, text, folded_text))
        results.sort(key=lambda r: (r[0], r[1]), reverse=True)
        return [
            {
                "id": page.id,
                "title": title,
                "name": highlight(title, terms),
                "category": page.parent_id.name or "",
                "snippet": self._maison_snippet(text, folded_text, terms),
                "write_date": page.write_date,
            }
            for _score, _date, page, title, text, folded_text in results[:limit]
        ]

    @api.model
    def _maison_snippet(self, text, folded_text, terms):
        """Excerpt around the first matching word of the content."""
        hits = [folded_text.find(t) for t in terms if t in folded_text]
        if not hits:
            excerpt = text[: 2 * SNIPPET_RADIUS]
            return highlight(excerpt, terms) + ("…" if len(text) > len(excerpt) else "")
        first = min(hits)
        start = max(0, first - SNIPPET_RADIUS)
        end = min(len(text), first + SNIPPET_RADIUS)
        # Cut on word boundaries.
        if start > 0:
            space = text.find(" ", start)
            start = space + 1 if 0 <= space < first else start
        if end < len(text):
            space = text.rfind(" ", first, end)
            end = space if space > first else end
        excerpt = highlight(text[start:end], terms)
        return (
            ("…" if start > 0 else "")
            + excerpt
            + ("…" if end < len(text) else "")
        )
