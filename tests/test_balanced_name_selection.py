import pandas as pd
import pytest

from compas_audit.balanced_name_selection import (
    panel_diagnostics,
    select_balanced_panel,
)


def _candidate_frame() -> pd.DataFrame:
    rows = []
    offsets = {
        "signal_a": 0.00,
        "signal_b": 0.05,
        "signal_c": 0.10,
        "signal_d": 0.15,
    }
    for group, offset in offsets.items():
        for slot in range(3):
            rows.append(
                {
                    "candidate_id": f"{group}_{slot}",
                    "signal_group": group,
                    "full_name": f"{group} candidate {slot}",
                    "valid_respondents": 40,
                    "group_agreement": 0.80 + 0.02 * slot,
                    "gender_agreement": 0.90,
                    "median_confidence": 4,
                    "mean_familiarity": 3.0 + offset + 0.02 * slot,
                    "mean_socioeconomic_status": 3.2 + offset + 0.01 * slot,
                    "mean_unusual": 2.5 + offset + 0.03 * slot,
                }
            )
    return pd.DataFrame(rows)


def test_balanced_panel_selector_returns_two_names_per_group():
    selected, diagnostics = select_balanced_panel(_candidate_frame())
    assert len(selected) == 8
    assert selected.groupby("signal_group").size().eq(2).all()
    assert diagnostics["pass"].all()


def test_panel_diagnostics_enforces_locked_range():
    frame = _candidate_frame()
    frame.loc[frame["signal_group"].eq("signal_d"), "mean_unusual"] = 5.0
    selected = frame.groupby("signal_group", as_index=False).head(2)
    diagnostics = panel_diagnostics(selected)
    unusual = diagnostics.loc[diagnostics["metric"].eq("mean_unusual")].iloc[0]
    assert not bool(unusual["pass"])


def test_selector_rejects_group_with_too_few_eligible_names():
    frame = _candidate_frame()
    frame.loc[
        frame["signal_group"].eq("signal_c"),
        "group_agreement",
    ] = 0.50
    with pytest.raises(ValueError, match="signal_c"):
        select_balanced_panel(frame)
