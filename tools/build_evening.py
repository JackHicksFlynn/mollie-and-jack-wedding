"""Build evening/index.html (the evening-guest version of the site) from index.html.

Run after every edit to index.html:  python3 tools/build_evening.py
Every replacement must match exactly once, so the build fails loudly if index.html changes shape.
"""
import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
s = (root / "index.html").read_text()
BASE = "https://jackhicksflynn.github.io/mollie-and-jack-wedding/"
EVENING_FORM = "https://forms.gle/XzK33dGN1kvo2ECG6"

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"build_evening: expected {count} match(es), found {n}: {old[:70]!r}")
    s = s.replace(old, new)

# --- head: title, previews, links
rep("<title>Mollie &amp; Jack's Wedding</title>", "<title>Mollie &amp; Jack's Wedding · Evening Celebration</title>")
rep('content="Mollie &amp; Jack\'s wedding · Saturday 1st May 2027 · Clapton Country Club, London E5"',
    'content="Join Mollie &amp; Jack for their evening wedding celebration · Saturday 1st May 2027 from 6pm · Clapton Country Club, London E5"')
rep('<meta property="og:title" content="Mollie &amp; Jack\'s Wedding">', '<meta property="og:title" content="Mollie &amp; Jack\'s Evening Celebration">')
rep('content="Saturday 1st May 2027 · Clapton Country Club, London E5. Kindly RSVP by 15th February 2027."',
    'content="Join us for the evening celebration · Saturday 1st May 2027 from 6pm · Clapton Country Club, London E5. Kindly RSVP by 15th February 2027."')
rep(f'<meta property="og:url" content="{BASE}">', f'<meta property="og:url" content="{BASE}evening/">')
rep(f'<link rel="canonical" href="{BASE}">', f'<link rel="canonical" href="{BASE}evening/">')
rep(f"{BASE}img/share.jpg?v=1", f"{BASE}img/share-evening.jpg?v=1", count=3)
rep('content="Mollie &amp; Jack, Saturday 1st May 2027, Clapton Country Club"', 'content="Mollie &amp; Jack, evening celebration from 6pm, Saturday 1st May 2027, Clapton Country Club"')

# --- asset paths (the page lives one folder down)
for a, b in [('src="img/', 'src="../img/'), ('url(img/', 'url(../img/'), ('url(fonts/', 'url(../fonts/'),
             ('href="img/', 'href="../img/'), ('href="favicon.ico"', 'href="../favicon.ico"'),
             ('href="apple-touch-icon.png"', 'href="../apple-touch-icon.png"')]:
    if a not in s: sys.exit(f"build_evening: path pattern missing: {a}")
    s = s.replace(a, b)

# --- nav + hero
rep('<a class="l" href="#day">The day</a>', '<a class="l" href="#day">Evening</a>')
rep('<p class="lead">WE CANNOT WAIT TO CELEBRATE WITH YOU</p>', '<p class="lead">JOIN US FOR THE EVENING CELEBRATION</p>')
rep('<p class="day">SATURDAY <span>1ST MAY 2027</span></p>', '<p class="day">SATURDAY <span>1ST MAY 2027</span></p>\n      <p class="from">FROM 6PM</p>')
rep('.hero .rule{width:min(360px', '.hero .from{font-family:var(--f-bold);font-size:clamp(22px,3vw,30px);letter-spacing:.08em;margin:10px 0 0;color:var(--ink-soft)}\n.hero .rule{width:min(360px')

# --- the evening timeline (4 stops)
rep('<h2 class="h2">The Day</h2>', '<h2 class="h2">The Evening</h2>')
rep('<p class="kicker">SATURDAY 1ST MAY 2027 · CLAPTON COUNTRY CLUB</p>', '<p class="kicker">SATURDAY 1ST MAY 2027 · FROM 6PM · CLAPTON COUNTRY CLUB</p>')
a = s.index('<ol class="sched">'); b = s.index('</ol>', a) + len('</ol>')
s = s[:a] + '''<ol class="sched">
          <li class="big"><span class="t">6:00pm</span><span class="w">Evening guests arrive</span></li>
          <li><span class="t">Then</span><span class="w">Drinks &amp; dancing</span></li>
          <li><span class="t">12:30am</span><span class="w">Last orders</span></li>
          <li class="big"><span class="t">1:00am</span><span class="w">Carriages</span></li>
        </ol>''' + s[b:]
rep('.sched{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));max-width:none}', '.sched{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));max-width:none;max-width:900px;margin-inline:auto}')
rep('.sched::before{left:10%;right:10%;', '.sched::before{left:12.5%;right:12.5%;')

# --- info cards: drop "one venue" (ceremony-specific), three across on desktop
a = s.index('          <div>\n            <h3 class="h3">ONE VENUE</h3>'); b = s.index('</div>', a) + len('</div>\n')
s = s[:a] + s[b:]
rep('@media (min-width:1100px){.cards{grid-template-columns:repeat(4,minmax(0,1fr))}}',
    '@media (min-width:640px) and (max-width:1099px){.cards > div:last-child:nth-child(odd){grid-column:1 / -1}}\n@media (min-width:1100px){.cards{grid-template-columns:repeat(3,minmax(0,1fr))}}')

# --- FAQs
a = s.index('        <details><summary>Are the ceremony and reception in the same place?</summary>'); b = s.index('</details>\n', a) + len('</details>\n')
s = s[:a] + s[b:]
rep('but we hope to enjoy cocktail hour on the cobbled decking area outside (weather permitting!).',
    'with a cobbled decking area outside for when you need some fresh air (weather permitting!).')

# --- RSVP goes to the evening form
rep('var RSVP_LINK = "https://forms.gle/1hGS7iT6AvZytamd6";', f'var RSVP_LINK = "{EVENING_FORM}";')

leftover = [w for w in ("Ceremony", "ceremony", "1:00pm", "12:15pm", "cocktail hour") if w in s]
if leftover: sys.exit(f"build_evening: day-only wording still present: {leftover}")
(root / "evening").mkdir(exist_ok=True)
(root / "evening" / "index.html").write_text(s)
print("built evening/index.html")
