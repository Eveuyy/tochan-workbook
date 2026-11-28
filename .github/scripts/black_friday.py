#!/usr/bin/env python3
"""Black Friday switch for ai-preview/index.html (Eve's AI course sales page).

  python3 black_friday.py on  <course_link> <bundle_link> <end_iso>   # sale prices, countdown, discounted Morning links
  python3 black_friday.py off                                          # full prices, countdown hidden, full-price Morning links

Runs from the repo root. Idempotent: 'off' on an already-off page changes nothing.
"""
import re, sys, pathlib

PAGE = pathlib.Path("ai-preview/index.html")
FULL_COURSE = "https://mrng.to/XeGb9OUChG"
FULL_BUNDLE = "https://mrng.to/ZrmjqmJK3M"
FULL_COURSE_PRICE = "890 ₪"
FULL_BUNDLE_PRICE = "1,120 ₪"
SALE_COURSE_PRICE = "756 ₪"
SALE_BUNDLE_PRICE = "952 ₪"
LABEL_ON = "בלאק פריידיי: 15% הנחה נגמרת בעוד"
LABEL_OFF = "מחיר ההשקה נגמר בעוד"
SUB_ON = "15% הנחה לבלאק פריידיי. אחרי זה המחיר חוזר ל-890 ₪."
SUB_OFF = "מחיר השקה. אחריו המחיר עולה."


def sub1(pattern, repl, text, what):
    new, n = re.subn(pattern, repl, text, count=1, flags=re.S)
    if n != 1:
        sys.exit(f"black_friday: could not find {what}")
    return new


def switch(mode, course_link=None, bundle_link=None, end_iso=None):
    t = PAGE.read_text(encoding="utf-8")
    on = mode == "on"
    # countdown box
    t = sub1(r'<div class="cd glass" id="cd"( hidden)? data-end="[^"]*"',
             '<div class="cd glass" id="cd"%s data-end="%s"' % ("" if on else " hidden", end_iso if on else "2026-11-06T22:00:00+02:00"),
             t, "countdown box")
    t = sub1(r'<p class="cd-label">[^<]*</p>', '<p class="cd-label">%s</p>' % (LABEL_ON if on else LABEL_OFF), t, "countdown label")
    t = sub1(r'<p class="sub" id="cdSub"( hidden)?>[^<]*</p>',
             '<p class="sub" id="cdSub"%s>%s</p>' % ("" if on else " hidden", SUB_ON if on else SUB_OFF), t, "countdown sub")
    # prices (the .was span is what the page's own JS uses to restore the full price client-side)
    course_amt = '<div class="amount">%s <span class="was">%s</span></div>' % (SALE_COURSE_PRICE, FULL_COURSE_PRICE) if on else '<div class="amount">%s</div>' % FULL_COURSE_PRICE
    bundle_amt = '<div class="amount">%s <span class="was">%s</span></div>' % (SALE_BUNDLE_PRICE, FULL_BUNDLE_PRICE) if on else '<div class="amount">%s</div>' % FULL_BUNDLE_PRICE
    t = sub1(r'(<div class="ticket led rec" id="tCourse">.*?)<div class="amount">[^<]*(?:<span class="was">[^<]*</span>)?</div>', lambda m: m.group(1) + course_amt, t, "course amount")
    t = sub1(r'(<div class="ticket led" id="tBundle">.*?)<div class="amount">[^<]*(?:<span class="was">[^<]*</span>)?</div>', lambda m: m.group(1) + bundle_amt, t, "bundle amount")
    # buy links
    t = sub1(r'(<div class="ticket led rec" id="tCourse">.*?<a class="btn" href=")[^"]*(")', lambda m: m.group(1) + (course_link if on else FULL_COURSE) + m.group(2), t, "course button")
    t = sub1(r'(<div class="ticket led" id="tBundle">.*?<a class="btn" href=")[^"]*(")', lambda m: m.group(1) + (bundle_link if on else FULL_BUNDLE) + m.group(2), t, "bundle button")
    PAGE.write_text(t, encoding="utf-8")
    print("black_friday:", mode, "done")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["on"] and len(a) == 4:
        switch("on", a[1], a[2], a[3])
    elif a == ["off"]:
        switch("off")
    else:
        sys.exit(__doc__)
