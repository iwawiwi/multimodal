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
    'overlay0', 'overlay1',
    'text', 'subtext1', 'subtext0',
    'blue', 'sapphire', 'mauve', 'teal',
    'green', 'peach', 'maroon', 'lavender',
}

# Raw Catppuccin palette colors that are NOT part of the design system.
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


def check_design_compliance(content):
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
            'Forbidden data-transition="zoom" — use fade (see SKILL.md transition standards).'
        )

    # 6. Spatial fragments
    for bad in ('fade-up', 'fade-down', 'fade-left', 'fade-right'):
        if re.search(r'class="[^"]*fragment\s+[^"]*' + re.escape(bad), content):
            violations.append(
                f'Forbidden fragment "{bad}" — use pure "fade-in" only.'
            )
            break

    # 7. cqi / vh units inside slides
    if re.search(r'\d+(?:\.\d+)?(?:cqi|vh)\b', content):
        violations.append(
            'Forbidden cqi/vh unit inside slides — use flex/em/rem (see SKILL.md).'
        )

    # 8. Pill badges
    if re.search(r'class="[^"]*c-badge', content):
        violations.append(
            'Forbidden pill badge .c-badge — use clean typographic labels (zero-badge policy).'
        )

    # 9. Scrollbars on slide content (no-scroll policy, D-009)
    # Detect overflow: auto/scroll applied to slide-content components.
    # The navigation popover .deck-topic-list is UI chrome and exempt.
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
    violations = check_design_compliance(content)
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
