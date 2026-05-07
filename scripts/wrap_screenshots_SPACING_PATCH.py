"""
PATCH for wrap_screenshots.py — fixes the May 2026 Puzzle2048 audit
finding that subtitle text sits too close to the headline (descender
of "EVERY RUN" almost touches the subtitle in screenshot 06).

Root cause: the `y += h2 + int(H * 0.020)` line uses 2% of canvas
height as the gap, which on 2400px tall captures = 48px. With heavy
display fonts at ~140-180px size, the descenders push into that gap.
Bumping to 4% (96px) gives the subtitle proper breathing room.

ALSO: subtitle-to-block-bottom spacing should grow proportionally
because tightly-packed subtitle to next element (the device frame)
also reads as cramped.

Find this block in draw_header() (around line 195-205 currently):

    draw.text((x2, y), line2, font=line_font, fill=theme["text_primary"])
    y += h2 + int(H * 0.020)        # ← BEFORE: 2% gap (too tight)

    # Subtitle — subtle color, shrink-to-fit then 2-line wrap if still too wide.
    ...

Replace the gap-calculation line with:

    draw.text((x2, y), line2, font=line_font, fill=theme["text_primary"])
    # Headline-to-subtitle gap: 4% of canvas height (was 2%, too tight —
    # heavy display-font descenders crowded the subtitle on Puzzle2048
    # May 2026 audit). 4% gives the subtitle clear breathing room.
    y += h2 + int(H * 0.040)

ALSO update draw_header()'s caller in wrap_image() to add spacing AFTER
the header before the device mockup. Find:

    end_y = draw_header(img, headline_obj, theme)
    # ... device mockup placement immediately follows

And insert a buffer:

    end_y = draw_header(img, headline_obj, theme)
    end_y += int(H * 0.025)  # subtitle-to-device gap
    # ... device mockup placement immediately follows


SAME FIX REQUIRED in wrap_tablet_screenshots.py — see line ~155 region:

    y += int(h * 0.018)  # ← BEFORE: 1.8% (too tight on 2560 canvas)

Replace with:

    y += int(h * 0.035)  # 3.5% — proportional to canvas height
"""
