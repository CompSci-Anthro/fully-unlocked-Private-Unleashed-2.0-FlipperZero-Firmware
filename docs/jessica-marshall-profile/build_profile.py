"""Builds Jessica_Marshall_Profile.pdf from publicly available information.

Run: python3 build_profile.py   (requires reportlab)
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).with_name("Jessica_Marshall_Profile.pdf")
COMPILED = "October 2, 2026"

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/liberation"
for name, file in [
    ("Sans", "LiberationSans-Regular.ttf"),
    ("Sans-Bold", "LiberationSans-Bold.ttf"),
    ("Sans-Italic", "LiberationSans-Italic.ttf"),
    ("Sans-BoldItalic", "LiberationSans-BoldItalic.ttf"),
    ("Serif", "LiberationSerif-Regular.ttf"),
    ("Serif-Bold", "LiberationSerif-Bold.ttf"),
    ("Serif-Italic", "LiberationSerif-Italic.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, f"{FONT_DIR}/{file}"))
pdfmetrics.registerFontFamily(
    "Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Italic", boldItalic="Sans-BoldItalic"
)

# ---------------------------------------------------------------- palette
INK = colors.HexColor("#1F1B18")
MUTED = colors.HexColor("#5E554D")
CLAY = colors.HexColor("#8A3F1F")      # primary accent (terracotta)
SAND = colors.HexColor("#F4ECE1")      # soft panel fill
SAND_DARK = colors.HexColor("#E3D3BE")  # rules / borders
TEAL = colors.HexColor("#2F5D62")      # secondary accent

# ---------------------------------------------------------------- styles
body = ParagraphStyle("body", fontName="Sans", fontSize=9.6, leading=13.3, textColor=INK, spaceAfter=5)
small = ParagraphStyle("small", parent=body, fontSize=8.6, leading=11.6, textColor=MUTED, spaceAfter=0)
cell = ParagraphStyle("cell", parent=body, fontSize=8.9, leading=11.8, spaceAfter=0)
cell_b = ParagraphStyle("cell_b", parent=cell, fontName="Sans-Bold")
cell_head = ParagraphStyle("cell_head", parent=cell, fontName="Sans-Bold", textColor=colors.white, fontSize=8.8)
h1 = ParagraphStyle("h1", fontName="Serif-Bold", fontSize=14, leading=18, textColor=CLAY, spaceBefore=11, spaceAfter=5)
h2 = ParagraphStyle("h2", fontName="Sans-Bold", fontSize=10.5, leading=14, textColor=TEAL, spaceBefore=6, spaceAfter=2)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=3)
callout = ParagraphStyle("callout", parent=body, fontSize=9.4, leading=13.2, spaceAfter=0)
src = ParagraphStyle("src", parent=small, fontSize=8.2, leading=11, leftIndent=16, firstLineIndent=-16, spaceAfter=3, alignment=TA_LEFT)

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN
HEADER_H = 1.95 * inch


def P(text, style=body):
    return Paragraph(text, style)


def bullets(items, style=bullet):
    return [Paragraph(t, style, bulletText="•") for t in items]


def section(title):
    return [P(title, h1), _rule()]


def _rule():
    t = Table([[""]], colWidths=[CONTENT_W], rowHeights=[2])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 1.2, SAND_DARK)]))
    return t


def panel(flowables, fill=SAND, border=SAND_DARK, pad=10):
    t = Table([[flowables]], colWidths=[CONTENT_W])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), fill),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("LEFTPADDING", (0, 0), (-1, -1), pad),
                ("RIGHTPADDING", (0, 0), (-1, -1), pad),
                ("TOPPADDING", (0, 0), (-1, -1), pad - 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
            ]
        )
    )
    return t


def data_table(header, rows, widths, zebra=True):
    data = [[P(h, cell_head) for h in header]]
    for r in rows:
        data.append([P(c, cell_b if i == 0 else cell) for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), CLAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, SAND_DARK),
    ]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), SAND))
    t.setStyle(TableStyle(style))
    return t


def kv_table(rows, key_w=1.55 * inch):
    data = [[P(k, cell_b), P(v, cell)] for k, v in rows]
    t = Table(data, colWidths=[key_w, CONTENT_W - key_w - 20])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, SAND_DARK),
            ]
        )
    )
    return t


def timeline(rows):
    data = [[P(f'<font color="#8A3F1F"><b>{when}</b></font>', cell), P(what, cell)] for when, what in rows]
    t = Table(data, colWidths=[1.25 * inch, CONTENT_W - 1.25 * inch])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("LEFTPADDING", (1, 0), (1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBEFORE", (1, 0), (1, -1), 2, CLAY),
            ]
        )
    )
    return t


# ---------------------------------------------------------------- page decoration
def first_page(c, doc):
    c.saveState()
    c.setFillColor(CLAY)
    c.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.rect(0, PAGE_H - HEADER_H - 5, PAGE_W, 5, stroke=0, fill=1)

    c.setFillColor(colors.HexColor("#F3D9C6"))
    c.setFont("Sans-Bold", 8.5)
    c.drawString(MARGIN, PAGE_H - 0.58 * inch, "PROFESSIONAL PROFILE  ·  ANTHROPOLOGY FACULTY")

    c.setFillColor(colors.white)
    c.setFont("Serif-Bold", 32)
    c.drawString(MARGIN, PAGE_H - 1.06 * inch, "Jessica Marshall")

    c.setFont("Sans", 11)
    c.drawString(MARGIN, PAGE_H - 1.37 * inch, "Adjunct Anthropology Instructor, Sacramento City College")
    c.drawString(MARGIN, PAGE_H - 1.57 * inch, "Professor of Anthropology, Cañada College")

    c.setFillColor(colors.HexColor("#F3D9C6"))
    c.setFont("Sans-Italic", 8.5)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.57 * inch, f"Compiled {COMPILED} from public sources")
    c.restoreState()
    footer(c, doc)


def later_pages(c, doc):
    c.saveState()
    c.setStrokeColor(CLAY)
    c.setLineWidth(2)
    c.line(MARGIN, PAGE_H - 0.5 * inch, PAGE_W - MARGIN, PAGE_H - 0.5 * inch)
    c.setFillColor(MUTED)
    c.setFont("Sans-Bold", 8)
    c.drawString(MARGIN, PAGE_H - 0.42 * inch, "JESSICA MARSHALL  ·  PROFESSIONAL PROFILE")
    c.restoreState()
    footer(c, doc)


def footer(c, doc):
    c.saveState()
    c.setStrokeColor(SAND_DARK)
    c.setLineWidth(0.6)
    c.line(MARGIN, 0.6 * inch, PAGE_W - MARGIN, 0.6 * inch)
    c.setFillColor(MUTED)
    c.setFont("Sans", 7.8)
    c.drawString(MARGIN, 0.42 * inch, "Compiled from publicly available sources; see Sources and Verification Notes.")
    c.drawRightString(PAGE_W - MARGIN, 0.42 * inch, f"Page {doc.page}")
    c.restoreState()


# ---------------------------------------------------------------- content
def build_story():
    s = []

    # -- At a glance
    s.append(Spacer(1, 4))
    s.append(
        panel(
            [
                P("<b>AT A GLANCE</b>", ParagraphStyle("k", parent=small, textColor=CLAY, fontName="Sans-Bold", spaceAfter=4)),
                kv_table(
                    [
                        ("Discipline", "Anthropology, with a graduate specialty in <b>visual anthropology</b> "
                                       "(photography and ethnographic film)"),
                        ("Current roles", "Adjunct (part-time) anthropology instructor, <b>Sacramento City College</b> "
                                          "(Los Rios Community College District)<br/>"
                                          "Professor of Anthropology, <b>Cañada College</b>, Redwood City "
                                          "(San Mateo County Community College District)"),
                        ("Degrees", "B.A. Anthropology, B.A. Photography, B.A. Journalism — California State "
                                    "University, Sacramento<br/>M.A. Visual Anthropology — University of Kent, England"),
                        ("Teaches", "Cultural Anthropology, Biological (Physical) Anthropology, Archaeology, "
                                    "Ethnographic Film"),
                        ("Experience", "About 21 years of college teaching; on the Cañada College faculty since 2007"),
                        ("Known for", "Leading faculty-led study-abroad programs in Egypt, Italy, Australia, Belize "
                                      "and Japan"),
                    ]
                ),
            ]
        )
    )

    # -- Overview
    s += section("Overview")
    s.append(
        P(
            "Jessica Marshall is a community-college anthropologist whose career centers on teaching "
            "introductory anthropology across its subfields and on taking students abroad to study culture "
            "first-hand. She is a full Professor of Anthropology at Cañada College in Redwood City and also "
            "teaches anthropology at Sacramento City College (SCC), where she appears in the college’s "
            "employee directory under the Anthropology department."
        )
    )
    s.append(
        P(
            "Her academic training is unusually visual. Alongside an undergraduate anthropology degree she earned "
            "separate bachelor’s degrees in photography and journalism, then completed a master’s in "
            "<b>visual anthropology</b> in England — the branch of the discipline that uses photography and "
            "film both to record cultural life and to analyze how cultures represent themselves. That thread "
            "runs straight through to her current teaching, which includes a course in ethnographic film."
        )
    )

    # -- Education
    edu = section("Education")
    edu.append(
        data_table(
            ["Degree", "Field", "Institution"],
            [
                ["M.A.", "Visual Anthropology", "University of Kent, Canterbury, England"],
                ["B.A.", "Anthropology", "California State University, Sacramento"],
                ["B.A.", "Photography", "California State University, Sacramento"],
                ["B.A.", "Journalism", "California State University, Sacramento"],
            ],
            [0.9 * inch, 2.0 * inch, CONTENT_W - 2.9 * inch],
        )
    )
    s.append(KeepTogether(edu))
    s.append(Spacer(1, 6))
    s += bullets(
        [
            "As an undergraduate she studied abroad in <b>Florence, Italy</b> — an experience she cites as the "
            "origin of her commitment to study-abroad teaching.",
            "No doctorate was found in public sources. A master’s degree is the standard minimum "
            "qualification for anthropology faculty in the California Community Colleges system.",
        ]
    )

    # -- Focus & interests
    s += section("Anthropological Focus & Research Interests")
    s.append(P("Visual anthropology (trained specialty)", h2))
    s.append(
        P(
            "Her M.A. specialization and her degrees in photography and journalism point to a core interest in "
            "documenting and interpreting culture through images. She teaches <b>ANTH 200: Ethnographic Film</b>, "
            "which examines how filmmakers and anthropologists portray other ways of life, and she has taught it "
            "on location abroad (Florence 2024; Japan 2026)."
        )
    )
    s.append(P("Four-field generalist teaching", h2))
    s.append(
        P(
            "Her course load spans the major subfields of American anthropology: cultural anthropology, "
            "biological/physical anthropology (human evolution, genetics, primates, the fossil record), and "
            "archaeology."
        )
    )
    s.append(P("Experiential, place-based learning", h2))
    s.append(
        P(
            "For the 2026 Japan program she described plans to “tie place into” her anthropology class so "
            "students can apply course concepts directly to their experiences abroad. She has argued that studying "
            "abroad allows deeper understanding of other cultures, sharper critical thinking about the world, and a "
            "better sense of one’s own place in it."
        )
    )
    s.append(P("Culture and environment", h2))
    s.append(
        P(
            "With Cañada biology professor Carol Rhodes she co-led <i>Sustainable Life in Belize: Culture and "
            "Ecosystems</i>, an interdisciplinary program pairing anthropology with ecology."
        )
    )
    s.append(
        panel(
            [
                P(
                    "<b>Note on research activity.</b> Her public footprint is teaching-centered. No funded research "
                    "program, ongoing fieldwork project, or research lab was found in public sources; her applied "
                    "ethnographic and visual work appears to be channeled mainly into teaching and study-abroad "
                    "programs. This is typical of California community-college faculty, whose positions are "
                    "teaching-focused.",
                    callout,
                )
            ]
        )
    )

    # -- Courses
    courses = section("Courses Taught")
    courses.append(
        data_table(
            ["Course", "Where", "What it covers"],
            [
                ["ANTH 300 — Biological Anthropology",
                 "Sacramento City College (offered online)",
                 "The science of biological anthropology: the scientific method, genetics and inheritance, natural "
                 "selection and evolution, modern human variation, living primates, and fossil evidence for human "
                 "evolution."],
                ["ANTH 310 — Cultural Anthropology",
                 "Sacramento City College (offered online)",
                 "Comparative study of human cultures; a core requirement of SCC’s Anthropology associate degree."],
                ["Introduction to Cultural Anthropology",
                 "Cañada College",
                 "Introductory cultural anthropology; also taught abroad (Florence)."],
                ["Introduction to Physical / Biological Anthropology",
                 "Cañada College",
                 "Human evolution and biology; also taught abroad (Florence)."],
                ["Archaeology",
                 "Cañada College",
                 "Methods and findings of archaeology and the study of past societies."],
                ["ANTH 200 — Ethnographic Film",
                 "Cañada College / SMCCD study abroad",
                 "Film as a tool and object of anthropological study; taught in Florence (2024) and Japan (2026)."],
            ],
            [1.95 * inch, 1.6 * inch, CONTENT_W - 3.55 * inch],
        )
    )
    s.append(KeepTogether(courses))
    s.append(Spacer(1, 4))
    s.append(
        P(
            "SCC course numbers are confirmed through student reviews and SCC’s catalog. Cañada course "
            "titles come from a Skyline College news profile; exact Cañada course numbers other than ANTH 200 "
            "were not confirmed.",
            small,
        )
    )

    # -- Study abroad
    s += section("Study Abroad & Global Teaching")
    s.append(
        timeline(
            [
                ("College years", "Studied abroad in Florence, Italy, as an undergraduate."),
                ("2011", "Led a group of Cañada College students on an intensive two-week study-abroad program "
                         "in <b>Egypt</b>."),
                ("Spring 2017", "San Mateo County Community College District faculty lead for the Northern California "
                                "Study Abroad Consortium (NCSAC) semester in <b>Florence, Italy</b>."),
                ("Undated", "Has taught anthropology in <b>Australia</b>, and co-led <i>Sustainable Life in Belize: "
                            "Culture and Ecosystems</i> in <b>Belize</b> with biologist Carol Rhodes."),
                ("Spring 2024", "Faculty member for the NCSAC semester in <b>Florence</b>, teaching Cultural "
                                "Anthropology, Biological Anthropology and Ethnographic Film. The program’s "
                                "course list also included Italian Life and Culture."),
                ("Summer 2026", "Faculty leader for the SMCCD <b>Japan</b> program (June 12–27, 2026), teaching "
                                "ANTH 200 Ethnographic Film alongside an Interaction Design course (MART 393)."),
            ]
        )
    )

    # -- Publications
    s += section("Publications & Scholarly Output")
    s.append(
        P(
            "<b>No published papers were found.</b> Targeted web searches, including ones aimed at ResearchGate, "
            "Academia.edu and Google Scholar listings, did not turn up any peer-reviewed articles, books, book "
            "chapters, or conference papers by this Jessica Marshall. Her M.A. at Kent would have required a "
            "dissertation or project, but it does not appear to be available online."
        )
    )
    s.append(
        P(
            "Her documented professional output is instead pedagogical: course design (including ethnographic film), "
            "the study-abroad programs listed above, and a listing in the American Anthropological "
            "Association’s <i>AnthroGuide</i> directory of anthropology programs and faculty."
        )
    )
    s.append(
        KeepTogether(
            [
                P("Watch out for name mix-ups", h2),
                panel(
                    [
                        P(
                            "Several other people with similar names publish in nearby fields. Their work should "
                            "<b>not</b> be attributed to her:",
                            callout,
                        ),
                        Spacer(1, 3),
                        *bullets(
                            [
                                "<b>Jessica Marshall, Ph.D.</b> — learning-sciences scholar (Northwestern "
                                "University; National Academy of Education/Spencer fellow) who wrote on teaching "
                                "about reparations.",
                                "<b>Jessica Marshall</b> — faculty member at Parsons School of Design, The New "
                                "School.",
                                "<b>Jessica Marshall</b> — science journalist who writes for <i>Discover</i> "
                                "magazine.",
                                "<b>John Marshall</b> and <b>Lorna Marshall</b> — the visual-anthropology "
                                "filmmaker and ethnographer known for work with the Ju/’hoansi of southern "
                                "Africa. They come up constantly in visual-anthropology searches; no source links "
                                "them to her.",
                                "<b>Fiona Marshall</b> — archaeologist at Washington University in St. Louis.",
                            ],
                            ParagraphStyle("cb", parent=callout, leftIndent=14, bulletIndent=3, spaceAfter=2),
                        ),
                    ]
                ),
            ]
        )
    )

    # -- Student perspectives
    s += section("Student Perspectives")
    s.append(
        P(
            "Student reviews on RateMyProfessors are mixed and come from a small, self-selected group. For her SCC "
            "listing (about 10 ratings when this was compiled, averaging roughly 2.5 out of 5), reviewers describe "
            "the online ANTH 300 and ANTH 310 coursework as manageable, with practice quizzes and extra-credit "
            "opportunities. Some also report slow email replies and a strict attendance or drop policy in online "
            "sections. Separate listings exist for her Cañada College teaching."
        )
    )

    # -- Contact
    s.append(KeepTogether(section("Professional Contact") + [
        kv_table(
            [
                ("Cañada College", "marshallj@smccd.edu  ·  (650) 306-3311  ·  Building 13, Room 313<br/>"
                                        "4200 Farm Hill Blvd., Redwood City, CA"),
                ("Sacramento City College", "Listed in the SCC employee directory (Anthropology); "
                                            "scc.losrios.edu/about-us/contact-us/employee-directory"),
            ],
            key_w=1.75 * inch,
        )
    ]))

    # -- Verification notes
    s += section("Verification Notes")
    s += bullets(
        [
            "The SCC employee directory and the Cañada College faculty page could not be opened directly from "
            "the research environment. Details from those pages come from search-engine extracts of them.",
            "Her <b>adjunct</b> status at SCC comes from the request for this profile. Public sources confirm she "
            "is listed with SCC’s Anthropology department and holds a full professorship at Cañada.",
            "“About 21 years” of teaching comes from the SMCCD Japan 2026 program page. The 2007 start date "
            "at Cañada comes from the college catalog’s faculty listing.",
            "No dates were found for the Australia and Belize programs.",
            "A RateMyProfessors listing also exists for a “Jessica Marshall” in anthropology at Sierra "
            "College (Nevada County campus). It may be the same person, but this could not be confirmed.",
        ]
    )

    # -- Sources
    s += section("Sources")
    sources = [
        "Sacramento City College — Employee Directory: Jessica Marshall. "
        "scc.losrios.edu/about-us/contact-us/employee-directory/employee?id=1091054",
        "Cañada College — Anthropology, Meet the Faculty: Jessica Marshall (Professor). "
        "canadacollege.edu/anthropology/meetthefaculty.php",
        "Cañada College Catalog — Faculty and Other Academic Personnel. "
        "catalog.canadacollege.edu/current/campus-directory/faculty.php",
        "San Mateo County CCD Study Abroad — Japan: Summer 2026. smccd.edu/studyabroad/programs/shortterm/japan.php",
        "Skyline College — “Students Prepare to Study Abroad in Florence, Italy in Spring 2024.” "
        "skylineshines.skylinecollege.edu",
        "The Skyline View — “Expand your global knowledge” (April 25, 2016). "
        "theskylineview.com/news/2016/04/25/expand-your-global-knowledge/",
        "American Anthropological Association — AnthroGuide: Jessica Marshall. guide.americananthro.org/74937/Jessica-Marshall",
        "Sacramento City College — Anthropology program and ANTH 300/310 course information. "
        "scc.losrios.edu/academics/programs-and-majors/anthropology",
        "RateMyProfessors — Jessica Marshall at Sacramento City College (ratemyprofessors.com/professor/2292151) "
        "and at Cañada College (ratemyprofessors.com/professor/2063898).",
        "Northern California Study Abroad Consortium — Florence program materials (AIFS / Santa Rosa JC / "
        "American River College).",
    ]
    for i, t in enumerate(sources, 1):
        s.append(P(f"{i}.&nbsp;&nbsp;{t}", src))

    return s


def main():
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=0.85 * inch,
        title="Jessica Marshall — Professional Profile",
        author="Compiled from public sources",
        subject="Anthropology faculty profile: Sacramento City College / Cañada College",
    )
    first_frame = Frame(
        MARGIN, 0.85 * inch, CONTENT_W, PAGE_H - HEADER_H - 0.85 * inch - 0.3 * inch, id="first",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    later_frame = Frame(
        MARGIN, 0.85 * inch, CONTENT_W, PAGE_H - 0.85 * inch - 0.75 * inch, id="later",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="First", frames=[first_frame], onPage=first_page, autoNextPageTemplate="Later"),
            PageTemplate(id="Later", frames=[later_frame], onPage=later_pages),
        ]
    )
    doc.build(build_story())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
