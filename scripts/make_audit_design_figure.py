"""Generate the COMPAS experimental-design figure used in the README."""

from __future__ import annotations

import argparse
from pathlib import Path

ROLE_TEMPLATES = 4
CANDIDATE_NAMES = 8
NAME_SIGNAL_GROUPS = 4
EDUCATION_PATHWAYS = 2
CAREER_GAP_CONDITIONS = 2
TEMPERATURES = 2
TRIALS_PER_RESUME_AND_TEMPERATURE = 5

MATCHED_RESUMES = (
    ROLE_TEMPLATES
    * CANDIDATE_NAMES
    * EDUCATION_PATHWAYS
    * CAREER_GAP_CONDITIONS
)
PLANNED_EVALUATIONS = (
    MATCHED_RESUMES * TEMPERATURES * TRIALS_PER_RESUME_AND_TEMPERATURE
)


def metric_card(
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    value: str,
    subtitle_lines: tuple[str, ...] = (),
    *,
    fill: str = "#F5F7FA",
    stroke: str = "#D7DEE8",
    title_color: str = "#334155",
    value_color: str = "#15324B",
    subtitle_color: str = "#64748B",
) -> str:
    """Return one rounded metric card as SVG markup."""
    subtitle = "".join(
        f'<tspan x="{x + width / 2}" dy="14">{line}</tspan>'
        for line in subtitle_lines
    )
    return f"""
    <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18"
          fill="{fill}" stroke="{stroke}" stroke-width="2"/>
    <text x="{x + width / 2}" y="{y + 39}" text-anchor="middle"
          class="card-title" fill="{title_color}">{title}</text>
    <text x="{x + width / 2}" y="{y + 78}" text-anchor="middle"
          class="card-value" fill="{value_color}">{value}</text>
    <text x="{x + width / 2}" y="{y + 84}" text-anchor="middle"
          class="card-subtitle" fill="{subtitle_color}">{subtitle}</text>
    """


def build_svg() -> str:
    """Build the complete SVG figure."""
    assert MATCHED_RESUMES == 128
    assert PLANNED_EVALUATIONS == 1280

    construction_cards = "".join(
        [
            metric_card(
                80,
                185,
                180,
                118,
                "Role templates",
                str(ROLE_TEMPLATES),
                ("2 frontline +", "2 knowledge-work"),
            ),
            metric_card(
                290,
                185,
                180,
                118,
                "Candidate names",
                str(CANDIDATE_NAMES),
                (f"{NAME_SIGNAL_GROUPS} perceived", "signal groups"),
            ),
            metric_card(
                500,
                185,
                180,
                118,
                "Education",
                str(EDUCATION_PATHWAYS),
                ("traditional /", "non-traditional"),
            ),
            metric_card(
                710,
                185,
                180,
                118,
                "Career gap",
                str(CAREER_GAP_CONDITIONS),
                ("0 months /", "12 months"),
            ),
            metric_card(
                950,
                182,
                190,
                124,
                "Matched resumes",
                f"{MATCHED_RESUMES:,}",
                ("balanced factorial sample",),
                fill="#E8F4F6",
                stroke="#88C6CF",
                value_color="#087F8C",
            ),
        ]
    )

    evaluation_cards = "".join(
        [
            metric_card(
                105,
                440,
                200,
                100,
                "Matched resumes",
                f"{MATCHED_RESUMES:,}",
                fill="#FFFFFF",
            ),
            metric_card(
                365,
                440,
                180,
                100,
                "Temperatures",
                str(TEMPERATURES),
                fill="#FFFFFF",
            ),
            metric_card(
                605,
                440,
                180,
                100,
                "Trials each",
                str(TRIALS_PER_RESUME_AND_TEMPERATURE),
                fill="#FFFFFF",
            ),
            metric_card(
                865,
                432,
                250,
                116,
                "Planned evaluations",
                f"{PLANNED_EVALUATIONS:,}",
                fill="#15324B",
                stroke="#15324B",
                title_color="#D9E5EF",
                value_color="#FFFFFF",
            ),
        ]
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680"
     viewBox="0 0 1200 680" role="img" aria-labelledby="title desc">
  <title id="title">COMPAS experimental design</title>
  <desc id="desc">Four role templates, eight candidate names, two education pathways,
  and two career-gap conditions generate 128 matched resumes. Two temperatures and
  five repeated trials produce 1,280 planned model evaluations.</desc>
  <style>
    text {{ font-family: Inter, Arial, Helvetica, sans-serif; }}
    .card-title {{ font-size: 17px; font-weight: 650; }}
    .card-value {{ font-size: 34px; font-weight: 750; }}
    .card-subtitle {{ font-size: 13px; }}
    .operator {{ font-size: 31px; font-weight: 700; fill: #8291A5; }}
  </style>
  <rect width="1200" height="680" fill="#FFFFFF"/>

  <text x="70" y="63" font-size="38" font-weight="750" fill="#12263A">
    COMPAS experimental design
  </text>
  <text x="70" y="94" font-size="18" fill="#5B6B7F">
    A balanced synthetic resume audit that isolates candidate signals while holding qualifications constant
  </text>

  <rect x="48" y="125" width="1104" height="230" rx="24"
        fill="#FBFCFE" stroke="#DCE3EB" stroke-width="2"/>
  <text x="82" y="164" font-size="21" font-weight="700" fill="#223A50">
    1. Construct qualification-matched resumes
  </text>
  {construction_cards}
  <text x="275" y="258" text-anchor="middle" class="operator">×</text>
  <text x="485" y="258" text-anchor="middle" class="operator">×</text>
  <text x="695" y="258" text-anchor="middle" class="operator">×</text>
  <text x="920" y="258" text-anchor="middle" class="operator">=</text>
  <text x="82" y="331" font-size="14" fill="#6B7788">
    Fixed within each template: experience, skills, work history, achievements, target role, and core education level.
  </text>

  <path d="M600 356 L600 391" stroke="#8EA0B5" stroke-width="2.5"/>
  <path d="M593 384 L600 395 L607 384" fill="#8EA0B5"/>

  <rect x="48" y="396" width="1104" height="190" rx="24"
        fill="#F4F8FC" stroke="#CDD8E4" stroke-width="2"/>
  <text x="82" y="430" font-size="21" font-weight="700" fill="#223A50">
    2. Repeat structured LLM screening
  </text>
  {evaluation_cards}
  <text x="335" y="504" text-anchor="middle" class="operator">×</text>
  <text x="575" y="504" text-anchor="middle" class="operator">×</text>
  <text x="825" y="504" text-anchor="middle" class="operator">=</text>

  <rect x="250" y="616" width="700" height="40" rx="10"
        fill="#FFF7E6" stroke="#F2D39B"/>
  <text x="600" y="642" text-anchor="middle" font-size="15" fill="#7A5514">
    Design scale only. This figure does not report live-model demographic bias findings.
  </text>
</svg>
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/figures/audit_design_scale.svg"),
        help="Destination SVG path.",
    )
    return parser.parse_args()


def main() -> None:
    """Write the SVG figure to disk."""
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
