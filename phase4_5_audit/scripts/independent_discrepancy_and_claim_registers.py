import os
import pandas as pd

AUDIT_DIR = r"c:\Users\siddu\Downloads\rr hackathon\phase4_5_audit"
DISC_CSV = os.path.join(AUDIT_DIR, "phase4_5_discrepancies.csv")
CLAIM_CSV = os.path.join(AUDIT_DIR, "phase4_5_claim_evidence_register.csv")

# 1. DISCREPANCY REGISTER
discrepancies = [
    {
        'finding_id': 'DISC-01',
        'severity': 'MAJOR',
        'title': 'Volume Ablation Ranking Shift Contradiction',
        'affected_components': 'Phase 4 Executive Summary vs phase4_model_audit.md',
        'root_cause': 'The Phase 4 executive summary claimed that removing volume caused only 1-2 slots of movement and 90% overlap for batters. However, the model audit table and independent recomputation prove that batting Top 10 overlap drops to 50% (5 players drop out: Stubbs, Miller, Tilak, Jadeja, Dhoni) with shifts up to +13 ranks.',
        'proposed_correction': 'Retract the 90% batting overlap claim. Formally report true batting overlap as 50% and bowling overlap as 90%, documenting that volume weighting explicitly stabilizes the middle-order finisher cohort.',
        'actual_correction': 'Recomputed exact No-Volume rankings in phase4_5_ranking_reconciliation.csv. Explicitly documented the 50% batting vs 90% bowling overlap.',
        'status': 'RESOLVED'
    },
    {
        'finding_id': 'DISC-02',
        'severity': 'MAJOR',
        'title': 'Unsupported Statistical Significance Claim (p < 0.001)',
        'affected_components': 'Phase 4 Executive Summary & phase4_model_audit.md',
        'root_cause': 'Reported p < 0.001 against league average without accounting for intra-match cluster correlation or multiple testing across the 153 eligible batters.',
        'proposed_correction': 'Run 10,000-iteration Match-Cluster Bootstrap. Apply Bonferroni correction for multiple comparisons (m = 153 for batters, m = 133 for bowlers). Report exact cluster-robust p-values.',
        'actual_correction': 'Executed 10,000-iteration bootstrap in phase4_5_statistical_validation.csv. Corrected p-values: Rinku (Bonferroni p = 0.026), Tim David (p = 0.0066), Abrar Ahmed (p < 1e-15), Narine (p = 1e-5), Nawaz (p = 0.0001). Removed claims of p < 0.001 for non-significant batters.',
        'status': 'RESOLVED'
    },
    {
        'finding_id': 'DISC-03',
        'severity': 'MAJOR',
        'title': 'Narrative Context Hallucination in Abrar Ahmed Case Study',
        'affected_components': 'phase4_player_case_studies.md (Case Study 6)',
        'root_cause': 'Prose narrative stated Pakistan defended 117 and Australia needed <6 RPO. This was an imported external memory artifact that conflicted with the actual dataset.',
        'proposed_correction': 'Audit Match 48915 ball-by-ball records directly. Reconcile pre-delivery match state, required run rate, and actual bowling figures.',
        'actual_correction': 'Verified directly against ball_by_ball.csv and matches.csv: Match 48915 was Pakistan vs Australia (2026-01-29), Pakistan defended 147+, Australia required 11.60 to 20.31 RPO in overs 16-18, and Abrar bowled 12 legal balls under pressure conceding only 6 runs (Econ 3.00 RPO). Narrative fully corrected in audit report.',
        'status': 'RESOLVED'
    },
    {
        'finding_id': 'DISC-04',
        'severity': 'MAJOR',
        'title': 'Bowling Pressure Semantics Ambiguity',
        'affected_components': 'Phase 2 & Phase 3 Methodology Reports',
        'root_cause': 'Pressure model P in 2nd innings is parameterized primarily on batting chase stress (high RRR, low balls remaining, wickets down). In high-RRR situations, the bowling side enjoys a win-expectancy advantage, but faces high aggression/boundary risk.',
        'proposed_correction': 'Define explicit semantic boundaries: Batting Pressure measures "Execution Demand", whereas Bowling Pressure measures "Defensive Containment under Extreme Batter Aggression / High Leverage".',
        'actual_correction': 'Documented precise dual-perspective interpretation in phase4_5_independent_audit.md. Bowling metrics are explicitly defined as containment and strike capability under peak match leverage.',
        'status': 'RESOLVED'
    },
    {
        'finding_id': 'DISC-05',
        'severity': 'MINOR',
        'title': 'Presentation Transcription Errors in Phase 4 Markdown Tables',
        'affected_components': 'Phase 4 Executive Summary response text',
        'root_cause': 'Assistant prose response manually transcribed secondary percentages (Dot %, Bdry %, Out %) with inverted/incorrect figures (e.g. Rinku Dot% 27.27% vs CSV 33.99%; Buttler Dot% 36.36% vs CSV 23.64%), even though all underlying CSV files were mathematically correct.',
        'proposed_correction': 'Reconcile every metric for all 20 players directly against phase4_5_recomputed_player_metrics.csv. Never use manual transcription.',
        'actual_correction': 'Full programmatic reconciliation completed in phase4_5_recomputed_player_metrics.csv. Every published table is verified to match the raw delivery sums.',
        'status': 'RESOLVED'
    },
    {
        'finding_id': 'DISC-06',
        'severity': 'MINOR',
        'title': 'Pace vs Spin Aggregate Clarification',
        'affected_components': 'Phase 4 Context Analysis vs Scratch scripts',
        'root_cause': 'Discrepant reported economy rates (5.87 vs 6.95 RPO for spin; 8.69 vs 8.28 RPO for pace) stemmed from differing subsets: all legal deliveries (Spin 6.95, Pace 8.28) vs death overs only (Spin 7.44, Pace 8.85) vs Top 10 bowler aggregates (~5.4 RPO).',
        'proposed_correction': 'Explicitly define scope, denominator, and subsets for all aggregate comparisons.',
        'actual_correction': 'Tabulated exact breakdown across All Pressure, Phases (PP, Mid, Death), and Competitions in phase4_5_independent_audit.md.',
        'status': 'RESOLVED'
    },
    {
        'finding_id': 'DISC-07',
        'severity': 'CRITICAL',
        'title': 'Phase 2 Discontinuity & Unclipped Score Bounds (Historical Audit)',
        'affected_components': 'src/pressure_model.py, src/match_state.py (Audited in Phase 3)',
        'root_cause': 'Phase 2 initial formulas allowed chase pressure to exceed 100 and introduced a step discontinuity at 36 balls remaining.',
        'proposed_correction': 'Clip continuous pressure to [0, 100] and replace piecewise leverage ramp with continuous quadratic function.',
        'actual_correction': 'Corrected in src/pressure_model.py and verified across all 200,999 deliveries in Phase 3 pre-ranking audit. Regenerated deliveries_with_pressure.csv cleanly.',
        'status': 'RESOLVED'
    }
]

df_disc = pd.DataFrame(discrepancies)
df_disc.to_csv(DISC_CSV, index=False)
print(f"Generated phase4_5_discrepancies.csv with {len(df_disc)} findings.")

# 2. CLAIM & EVIDENCE REGISTER
claims = [
    {
        'claim_id': 'CLM-01',
        'claim_text': 'Rinku Singh scored 45 runs off 17 pressure balls in Match 20193 including 5 consecutive sixes in the 20th over.',
        'claim_type': 'Direct raw-data fact',
        'evidence_source': 'data/raw/ball_by_ball.csv (match_id 20193, over 19.7-20.6)',
        'underlying_columns': 'match_id, overid, over_ball_num, runs, is_six',
        'verification_status': 'VERIFIED',
        'required_correction': 'None. 100% verified against raw records.'
    },
    {
        'claim_id': 'CLM-02',
        'claim_text': 'Jos Buttler scored 107* off 60 balls total, with 70 runs off 33 pressure balls (SR 212.12) in Match 31250.',
        'claim_type': 'Direct raw-data fact',
        'evidence_source': 'data/raw/ball_by_ball.csv & deliveries_with_pressure.csv (match_id 31250)',
        'underlying_columns': 'match_id, striker_id 813, runs, is_pressure_delivery',
        'verification_status': 'VERIFIED',
        'required_correction': 'None. 100% verified.'
    },
    {
        'claim_id': 'CLM-03',
        'claim_text': 'Tim David hit 3 consecutive sixes off Jason Holder in the 20th over of Match 20222 to win the match.',
        'claim_type': 'Direct raw-data fact',
        'evidence_source': 'data/raw/ball_by_ball.csv (match_id 20222, balls 20.1, 20.2, 20.3)',
        'underlying_columns': 'match_id, overid 20, over_ball_num 1-3, runs 6, 6, 6',
        'verification_status': 'VERIFIED',
        'required_correction': 'None. 100% verified.'
    },
    {
        'claim_id': 'CLM-04',
        'claim_text': 'Rashid Khan took a hat-trick in the 17th over of Match 20193 under pressure.',
        'claim_type': 'Direct raw-data fact',
        'evidence_source': 'data/raw/ball_by_ball.csv (match_id 20193, balls 17.1, 17.2, 17.3)',
        'underlying_columns': 'match_id, overid 17, bowler_id 4722, is_wicket True',
        'verification_status': 'VERIFIED',
        'required_correction': 'Clarify that ball 17.1 had pre-pressure 43.15 (Moderate) and balls 17.2-17.3 had P >= 45 (High).'
    },
    {
        'claim_id': 'CLM-05',
        'claim_text': 'Kuldeep Yadav took 5/17 in 2.5 overs in Match 28047, taking 4 wickets in 11 pressure balls.',
        'claim_type': 'Direct raw-data fact',
        'evidence_source': 'data/raw/ball_by_ball.csv & matches.csv (match_id 28047)',
        'underlying_columns': 'match_id, bowler_id 3644, bowler_runs_conceded, is_bowler_wicket',
        'verification_status': 'VERIFIED',
        'required_correction': 'None. 100% verified.'
    },
    {
        'claim_id': 'CLM-06',
        'claim_text': 'Rinku Singh and Tim David are statistically distinct from league-average finishers with p < 0.001.',
        'claim_type': 'Statistical inference',
        'evidence_source': 'Cluster bootstrap Wald test against mu_0 = 136.07',
        'underlying_columns': 'p_strike_rate, match_id clustering, n_boot = 10,000',
        'verification_status': 'RETRACTED_AND_CORRECTED',
        'required_correction': 'Retracted p < 0.001. Under cluster-robust match sampling with Bonferroni correction for 153 tests, Rinku p = 0.026 and Tim David p = 0.0066 (significant at alpha = 0.05 and 0.01, but not 0.001).'
    },
    {
        'claim_id': 'CLM-07',
        'claim_text': 'Abrar Ahmed possesses elite mystery spin with carrom ball and googly variations that batters cannot read.',
        'claim_type': 'Unsupported claim',
        'evidence_source': 'None in dataset (delivery dataset does not record physical grip/biomechanics/perception)',
        'underlying_columns': 'bowling_type (recorded merely as spin/leg-spin)',
        'verification_status': 'RETRACTED_AND_REPLACED',
        'required_correction': 'Replace subjective technical descriptions with empirical facts: Abrar demonstrates unprecedented dot-ball percentage (55.32%) and boundary suppression (4.26% boundary balls conceded).'
    },
    {
        'claim_id': 'CLM-08',
        'claim_text': 'Top finishers demonstrate elite psychological composure under pressure.',
        'claim_type': 'Unsupported claim',
        'evidence_source': 'None in dataset (psychometrics not measured)',
        'underlying_columns': 'None',
        'verification_status': 'RETRACTED_AND_REPLACED',
        'required_correction': 'Replace psychological speculation with statistical consistency: e.g., Tim David maintains strike rate >= 140 in 80.0% of pressure appearances.'
    },
    {
        'claim_id': 'CLM-09',
        'claim_text': 'Removing volume weighting causes only 1-2 slots of ranking movement and maintains 90% top 10 overlap.',
        'claim_type': 'Calculated statistic (Erroneous)',
        'evidence_source': 'Phase 4 Executive Summary text',
        'underlying_columns': 'BPRI_Model1_Balanced vs bpri_no_vol',
        'verification_status': 'RETRACTED_AND_CORRECTED',
        'required_correction': 'Corrected to exact recomputed values: Batting overlap is 50% (5 of 10), with shifts up to +13 slots. Bowling overlap is 90% (9 of 10).'
    },
    {
        'claim_id': 'CLM-10',
        'claim_text': 'Pace pressure bowling is concentrated at the death (72% of pace pressure deliveries in overs 16-20).',
        'claim_type': 'Direct raw-data fact',
        'evidence_source': 'data/processed/deliveries_with_pressure.csv (12,268 / 17,027 balls)',
        'underlying_columns': 'pace_or_spin, overid, is_pressure_delivery, is_legal',
        'verification_status': 'VERIFIED',
        'required_correction': 'None. 100% verified.'
    }
]

df_claims = pd.DataFrame(claims)
df_claims.to_csv(CLAIM_CSV, index=False)
print(f"Generated phase4_5_claim_evidence_register.csv with {len(df_claims)} claims.")
