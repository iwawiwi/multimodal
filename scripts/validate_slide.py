#!/usr/bin/env python3
"""
Validates the structural integrity AND design-language compliance of Reveal.js
HTML slides.

Structural checks:
  - HTML tag balancing and unclosed tags
  - Presence of required CSS and JS links
  - Broken local resource references

Design-language compliance checks (derived from references/visual-vocabulary.md):
  - Inline border-left callout anti-pattern
  - Inline color on .section-part-label
  - Undocumented --ctp-* tokens (e.g. --ctp-red)
  - Plain <ol>/<ul> on References slides
  - data-transition="zoom"
  - Spatial fragments (fade-up/-down/-left/-right)
  - cqi/vh units inside slides
  - Pill badges (.c-badge)

Usage:
    python3 validate_slide.py mgg01.html
"""

import sys
import os
import re
from html.parser import HTMLParser


# ---------------------------------------------------------------------------
# Design-language compliance constants (keep in sync with visual-vocabulary.md)
# ---------------------------------------------------------------------------

# Tokens that are part of the design system (from design-tokens.md).
# Any --ctp-* usage outside this list is flagged as undocumented.
ALLOWED_CTP_TOKENS = {
    'base', 'mantle', 'crust',
    'surface0', 'surface1', 'surface2',
    'overlay0', 'overlay1', 'overlay2',
    'text', 'subtext1', 'subtext0',
    'blue', 'sapphire', 'mauve', 'teal',
    'green', 'peach', 'maroon', 'lavender',
}

# Raw Catppuccin palette colors that are NOT part of the design system
# for SLIDE CONTENT. yellow/sky are additionally allowed in Prism .token
# rules (syntax highlighting = code data, not slide content).
FORBIDDEN_CTP_TOKENS = {
    'rosewater', 'flamingo', 'pink', 'red', 'yellow', 'sky',
}


class TagValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_tags = {'meta', 'link', 'img', 'br', 'hr', 'input'}
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.void_tags:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag not in self.void_tags:
            if not self.stack:
                self.errors.append(f"Unexpected closing tag </{tag}> with empty stack")
            elif self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.errors.append(f"Mismatched tag: expected </{self.stack[-1]}>, got </{tag}>")


def _token_used_in_prism_context(content, tok):
    """
    True if --ctp-yellow/--ctp-sky is used ONLY within a Prism .token rule
    (syntax highlighting = code data, legal per design-tokens.md note).
    """
    token_rule = re.compile(
        r'\.token\.(?:class-name|operator)\s*\{[^}]*var\(--ctp-' + re.escape(tok) + r'\)',
        re.DOTALL,
    )
    return bool(token_rule.search(content))


def _is_hands_on_doc(html_path):
    """Hands-on docs (hands-on/mggNN-hands-on.html) are code-first companion
    documents, NOT slide decks. Several slide-only rules do not apply:
    vh/vw units (floating nav + drawer), and overflow-x: auto on code/terminal."""
    base = os.path.basename(html_path)
    return ('hands-on' in html_path) or ('hands-on' in base)


def check_design_compliance(content, doc_type='slide', filename=''):
    """Return a list of design-language violation strings (empty = compliant)."""
    violations = []

    # 1. Inline border-left callout anti-pattern
    if re.search(r'style="[^"]*border-left\s*:\s*4px\s+solid', content):
        violations.append(
            "Anti-pattern: inline 'border-left: 4px solid' found — use "
            ".c-callout + .c-callout-info/-warning/-success with a semantic icon."
        )

    # 2. Inline color on .section-part-label
    if re.search(r'class="section-part-label"\s+style="[^"]*color', content):
        violations.append(
            "Anti-pattern: inline color on .section-part-label — use the class "
            "modifier .section-part-blue/-mauve/-teal/-peach/-green."
        )

    # 3. Undocumented --ctp-* tokens
    used_tokens = set(re.findall(r'--ctp-([a-z0-9]+)', content))
    for tok in sorted(used_tokens):
        if tok in FORBIDDEN_CTP_TOKENS:
            # Exception: yellow/sky are legal ONLY inside Prism .token rules
            # (syntax highlighting is code data, not slide content).
            if tok in ('yellow', 'sky') and _token_used_in_prism_context(content, tok):
                continue
            violations.append(
                f"Undocumented token --ctp-{tok} — not part of the design system. "
                f"Use a documented token (see design-tokens.md)."
            )
        elif tok not in ALLOWED_CTP_TOKENS:
            violations.append(
                f"Unknown token --ctp-{tok} — not listed in design-tokens.md."
            )

    # 4. Plain <ol>/<ul> on References slides
    # Detect a slide whose heading contains 'Referensi' and check for plain lists.
    ref_slide = re.search(
        r'<section[^>]*>.*?<h2[^>]*>([^<]*Referensi[^<]*)</h2>.*?</section>',
        content, re.DOTALL,
    )
    if ref_slide:
        slide_body = ref_slide.group(0)
        # A styled reference list uses 'counter-reset: ref' and grid layout.
        if re.search(r'<ol[^>]*>', slide_body) and 'counter-reset' not in slide_body:
            violations.append(
                "References slide uses a plain <ol>/<ul> — use the styled citation "
                "list (monospace [n] + grid + hairline divider, see D-002)."
            )

    # 5. data-transition="zoom"
    if re.search(r'data-transition="zoom"', content):
        violations.append(
            'Forbidden data-transition="zoom" — use the global slide transition (see SKILL.md).'
        )

    # 6. Spatial fragments
    for bad in ('fade-up', 'fade-down', 'fade-left', 'fade-right'):
        if re.search(r'class="[^"]*fragment\s+[^"]*' + re.escape(bad), content):
            violations.append(
                f'Forbidden fragment "{bad}" — use pure "fade-in" only.'
            )
            break

    # 7. cqi / vh units inside slides (slide-only rule)
    if doc_type == 'slide' and re.search(r'\d+(?:\.\d+)?(?:cqi|vh)\b', content):
        violations.append(
            'Forbidden cqi/vh unit inside slides — use flex/em/rem (see SKILL.md).'
        )

    # 8. Pill badges
    if re.search(r'class="[^"]*c-badge', content):
        violations.append(
            'Forbidden pill badge .c-badge — use clean typographic labels (zero-badge policy).'
        )

    # 9. Scrollbars on slide content (no-scroll policy, D-009)
    # Slide-only: hands-on docs legitimately use overflow-x: auto on code
    # windows/terminal bodies (code may exceed the column width).
    if doc_type == 'slide':
        overflow_patterns = [
            r'overflow(?:-x|-y)?\s*:\s*(auto|scroll)',
        ]
        # Find CSS rules targeting slide components with overflow
        # (in-file <style> blocks) — skip .deck-topic-list which is UI chrome.
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
        for block in style_blocks:
            for rule_match in re.finditer(
                r'([^{}]+)\{([^}]*overflow[^}]*)\}', block, re.DOTALL
            ):
                selector = rule_match.group(1)
                body = rule_match.group(2)
                if re.search(r'overflow(?:-x|-y)?\s*:\s*(auto|scroll)', body):
                    # Exempt UI chrome: deck-topic-list, and any .deck-* navigation
                    if re.search(r'deck-topic-list|deck-\w*(?:menu|popover|overlay|dropdown|search)', selector):
                        continue
                    violations.append(
                        'No-scroll policy (D-009): overflow auto/scroll on slide content '
                        f'({selector.strip()}). Content must fit without scrolling — split the slide instead.'
                    )

    # 10. Literal math notation drawn as SVG <text> (D-029)
    # Symbols inside a diagram must be KaTeX in a <foreignObject>; a literal
    # <text>x_A</text> shows a raw underscore and drifts from the formula slides.
    _math_in_text = re.compile(
        r'<text\b[^>]*>([^<]*)</text>'
    )
    _looks_like_math = re.compile(
        r'[A-Za-z]_[A-Za-z0-9]'      # x_A, f_B, p_A
        r'|[_^]\{'                    # subscript/hat braces
        r'|[\u03a3\u2211\u0177]'      # Sigma, sum, y-hat
    )
    # Decks still awaiting conversion get a grace period so the gate stays green.
    # (Currently empty: mgg02–mgg06 are all converted to foreignObject + KaTeX.)
    MATH_TEXT_GRANDFATHERED = set()
    for svg_match in re.finditer(r'<svg\b.*?</svg>', content, re.DOTALL):
        svg_body = svg_match.group(0)
        bad_texts = [
            t.strip()
            for t in _math_in_text.findall(svg_body)
            if _looks_like_math.search(t)
        ]
        if bad_texts and filename not in MATH_TEXT_GRANDFATHERED:
            violations.append(
                'Literal math in SVG <text>: '
                + ', '.join(repr(b) for b in bad_texts[:4])
                + ' — render symbols with KaTeX inside a <foreignObject> (see D-029).'
            )
            break

    # 11. KaTeX delimiters placed directly in SVG <text> (renders invisibly, D-029)
    for text_match in re.finditer(r'<text\b[^>]*>([^<]*)</text>', content):
        if '\\(' in text_match.group(1) or '$$' in text_match.group(1):
            violations.append(
                'KaTeX delimiters inside SVG <text> render with a 0x0 box (invisible) — '
                'wrap in <foreignObject> instead (see D-029).'
            )
            break

    # 12. Bridge slide for hands-on weeks (D-030)
    # A deck whose week ships a hands-on document must point to it from a
    # "Latihan Terbimbing" slide placed BEFORE the summary slide, so the lecturer
    # has something to show in class and the summary still closes the session.
    if doc_type == 'slide':
        _week = re.search(r'mgg(\d{2})', os.path.basename(filename))
        if _week:
            _hs = os.path.join(os.path.dirname(os.path.abspath(filename)),
                               'hands-on', f'mgg{_week.group(1)}-hands-on.html')
            if os.path.exists(_hs):
                _heads = [
                    re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    for m in re.finditer(r'<h[12][^>]*>(.*?)</h[12]>', content, re.DOTALL)
                ]
                _bridge = [i for i, h in enumerate(_heads) if 'Latihan Terbimbing' in h]
                _summary = [i for i, h in enumerate(_heads) if 'Rangkuman' in h]
                if not _bridge:
                    violations.append(
                        f'This week ships hands-on/mgg{_week.group(1)}-hands-on.html but the deck '
                        'has no "Latihan Terbimbing" bridge slide — add one pointing to the lab (see D-030).'
                    )
                elif _summary and _bridge[0] > _summary[0]:
                    violations.append(
                        'The "Latihan Terbimbing" bridge slide must come BEFORE the Rangkuman slide, '
                        'so the summary closes the session (see D-030).'
                    )

    # 13. Bridge slide must use the 2x2 grid, not a 4-column .pipeline-flow (D-030)
    # Four 100+ char descriptions in narrow columns produced ~220px-tall cards
    # and made links stretch oddly; .bridge-grid keeps them readable.
    for sec_match in re.finditer(r'<section\b.*?</section>', content, re.DOTALL):
        sec = sec_match.group(0)
        head = re.search(r'<h[12][^>]*>(.*?)</h[12]>', sec, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', head.group(1)) if head else ''
        if 'Latihan Terbimbing' in title and 'pipeline-flow' in sec:
            violations.append(
                'Bridge slide uses the 4-column .pipeline-flow; use the 2×2 .bridge-grid '
                'with .slide-btn links instead (see D-030).'
            )
            break

    return violations


def validate_file(html_path):
    if not os.path.exists(html_path):
        print(f"Error: File not found: {html_path}")
        return False

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = TagValidator()
    parser.feed(content)

    print(f"=== Validating {html_path} ===")
    has_error = False

    if parser.errors:
        has_error = True
        print("❌ Tag Mismatches:")
        for err in parser.errors:
            print(f"   - {err}")

    if parser.stack:
        has_error = True
        print(f"❌ Unclosed tags remaining: {parser.stack}")

    # Check local links
    links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', content)
    base_dir = os.path.dirname(os.path.abspath(html_path))
    broken_links = []

    for link in set(links):
        clean_link = link.split('#')[0].split('?')[0]
        if clean_link and not clean_link.startswith(('http://', 'https://', 'data:', 'mailto:')):
            full_path = os.path.join(base_dir, clean_link)
            if not os.path.exists(full_path):
                broken_links.append(link)

    if broken_links:
        has_error = True
        print("❌ Broken Local Links:")
        for bl in broken_links:
            print(f"   - {bl}")

    # Design-language compliance
    doc_type = 'hands-on' if _is_hands_on_doc(html_path) else 'slide'
    violations = check_design_compliance(
        content, doc_type=doc_type, filename=os.path.basename(html_path)
    )
    if violations:
        has_error = True
        print("❌ Design-Language Violations:")
        for v in violations:
            print(f"   - {v}")

    if not has_error:
        print("✅ Validation PASSED! No unclosed tags, syntax errors, broken links, or design violations.")
        return True
    return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "mgg01.html"
    success = validate_file(target)
    sys.exit(0 if success else 1)
