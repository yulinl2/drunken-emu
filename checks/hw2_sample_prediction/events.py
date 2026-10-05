"""The hand-written part of the registration: the segments, the events with their probabilities and what each rests on, and the predictor table.

Every number that comes from a measurement is read from the measured files here (nothing measured is typed); the probabilities, and the numbers
taken from the docs or from HW1, are typed and say where they come from.  A probability is a belief, set by judgment before the pass; none is fitted.
"""
from __future__ import annotations

from .cites import CLASS_SIZE, EXAMPLE_ITEMS, FIRST_DRAFT_CLASS, SAMPLE_STUDENTS, Cites, class_shares, mix_range, pct_range

SEG = [  # short id, chain id suffix, name, comparable by duration?, why not / the limit
    ("S1", "install", "install", False, "starts when a person (the coordinating session) says the file is ready, and runs through Files, Safari and Canvas pages whose state is unknown; only the part after the owner's first touch could be dated, and a screenshot of it may not exist"),
    ("S2", "queue", "read the queue", True, "under a minute: below the one-minute resolution of a screenshot clock, so it ties with any other short segment"),
    ("S3", "pair", "one pair", True, ""),
    ("S4", "pair-reload", "pair with a reload", True, "a reload is only dated if the narration or a screenshot says when it happened"),
    ("S5", "pair-lock", "pair after a lock", True, "the lock itself (minutes to hours) is outside the segment: measured from the unlock to the next Save and next"),
    ("S6", "export", "export", True, ""),
    ("S7", "handback", "hand-back", True, "ends at Send; the session's answer is outside the segment (waiting for a person)"),
]
PREFIX = "tapgrade-0.6.7-sample-"
ALLOWED_BASES = ("measured", "declared", "carried-from-HW1", "guess")


def events(MJ: dict, AJ: dict, inputs: dict) -> list[dict]:
    """The event table.  MJ is the measured file (invented large bank), AJ the same measurement with a bank of the runbook's example size."""
    c = Cites(inputs["citations"])
    M, A = MJ["predictors"], AJ["predictors"]
    A_scr = A["window"]["screens_per_question"]
    key_out, a_key_out = 1 - M["chips"]["at_the_default_sheet"]["key_in_view_with_a_chip"]["share"], 1 - A["chips"]["at_the_default_sheet"]["key_in_view_with_a_chip"]["share"]
    a_parts_per_pair = AJ["sample"]["parts"] / AJ["sample"]["questions"]
    a_share_part = A["chips"]["reason_labels"]["share_of_parts_with_such_a_pair_simulated"]
    a_share_pair = 1 - (1 - a_share_part) ** a_parts_per_pair
    W, PA, VS, LD, FC, EX, IN, TP = M["window"], M["primary_action"], M["view_stability"], M["loading"], M["first_contact"], M["export"], M["interruption"], M["two_pages"]
    CH = M["chips"]
    pv, pvt = W["pair_view"], W["pair_view_with_toast"]
    scr = W["screens_per_question"]
    parts_per_pair = MJ["sample"]["parts"] / MJ["sample"]["questions"]
    share_part = CH["reason_labels"]["share_of_parts_with_such_a_pair_simulated"]
    share_pair = 1 - (1 - share_part) ** parts_per_pair
    look = CH["reason_labels"]
    OS = FC["outside_sample"]
    SV = OS["tap_save_and_next"]
    hint_in_view = round(100 * OS["hint_button_visible_fraction_with_toast"])
    est = EX["complete_export_estimate"]
    CS = class_shares()
    in_pct, out_pct = pct_range(CS["in_lo"], CS["in_hi"]), pct_range(CS["out_lo"], CS["out_hi"])
    assert abs(0.58 - CS["in_hi"]) < 0.005, "Q2 (p 0.58) keeps the upper end of the share of first pages in the sample: the docs' numbers moved, so set its p again"
    save, sn = PA["tap_target_px"]["Save"], PA["tap_target_px"]["Save and next"]
    spp, rts = TP["stale_page_save"], TP["return_to_a_stale_page"]
    ev = [
        # --- S1 install
        dict(id="I1", steps=[("install", 6)], event="the file does not reach the Userscripts folder on the first try (wrong folder, unsure which one, or saved again)",
             observable="the narration says the file went to another folder, had to be moved or saved again, or that the folder was a worry", p=0.25, basis="guess",
             rests_on="HW1 A4 says the remembered folder costs nothing, for another destination; nothing on the save sheet says which folder is right"),
        dict(id="I2", steps=[("install", 4)], event="the owner hesitates between two similarly named files (a .user.js and a .json, or an older data script)",
             observable="the narration names two similar file names and a choice between them", p=0.15, basis="carried-from-HW1",
             rests_on=f"HW1 E3d: a look-alike script file existed and was NOT confused with the wanted one (stated); the runbook makes one file ({c('rbMakeFile')}), so a second one is not certain"),
        dict(id="I3", steps=[("install", 9)], event="the owner refreshes more than once, or says they are unsure the page refreshed",
             observable="two or more refreshes, or a stated doubt, in the narration or the screenshots", p=0.5, basis="carried-from-HW1",
             rests_on="HW1 B2 (the usual pattern: refresh, hesitate, refresh) and H3 (a doubt whether the page was refreshed); outcomes, used as base rates only: the chain declares one plain refresh"),
        dict(id="I4", steps=[("install", 11)], event="the load toast is missed (it is on screen about four seconds) and the owner checks the load another way",
             observable="the narration says the message vanished or was missed, or shows a check under Files, Loaded or in the queue", p=0.4, basis="declared",
             rests_on=f"code: the toast leaves after 4200 ms by itself; [measured: view_stability.load_toast, first_contact.load_toast_seconds_on_screen] {VS['load_toast']['seconds_on_screen']} s and {FC['load_toast_seconds_on_screen']} s on screen in two runs"),
        dict(id="I5", steps=[("install", 10), ("install", 11)], event="the sample does not show on the first load after the file is placed, and a second route is needed (reload, save again, Load a file)",
             observable="the narration says nothing appeared, or the first screenshot after the file shows no sample", p=0.35, basis="guess",
             rests_on=f"nobody has run the data-script route on an iPhone ({c('tgLimitsPhone')}); if the browser would not keep the file the page says so in the head and at the top of Grade ({c('tgNoKeep')}), which makes this event easier to code, not less likely"),
        dict(id="I6", steps=[("install", 4)], event="friction at 'Save to Files' (reading the menu for it)",
             observable="the narration says the menu item was hard to find", p=0.1, basis="carried-from-HW1",
             rests_on="HW1 A3 (a scroll, and a coarse then a fine read: about two steps in all, A) and A6 (nothing was missed this way); the chain's anchoring finding rests on carried placeholders"),
        dict(id="I7", steps=[("install", 12)], event="the owner goes back to the chat to re-read what to do during the install (a RELOAD)",
             observable="an app switch to the chat in the narration that is not the first read or the last hand-back", p=0.2, basis="declared",
             rests_on="the dataflow items stay within B=3 (peak 3): the model predicts no loss here; HW1's base rate (E3: a RELOAD from the chat) would say more, and that disagreement is the test"),
        # --- S2 queue
        dict(id="Q1", steps=[("queue", 2)], event="cannot find the way to the first pair at first, or it takes several tries (the queue: 'Open the sample queue' on a page outside the sample; 'Queue' at the end of a pair's page)",
             observable="the narration says the queue, the Sample tab or Next pair was not found, or took several tries", p=0.15, basis="declared",
             rests_on=f"The runbook says the Sample tab is not in the Grade view ({c('rbRoute')}) and names the route: from a page outside the sample, Open the sample queue, then Next pair, 2 taps and no scroll ({c('rbRouteOutside')}); from a pair, scroll to the end, Queue, then Next pair, 2 taps and one long scroll ({c('rbRouteSampled')}). "
                     f"[measured: first_contact.outside_sample, window.queue_button_from_pair] on a student outside the sample the 'Open the sample queue' button is the first note of the page and {hint_in_view}% in view under the toast; from a pair the Queue button is {W['queue_button_from_pair']['screens_down']} screens down ({A['window']['queue_button_from_pair']['screens_down']} in the example-size bank). "
                     f"p is a judgment from two guessed terms: about {out_pct}% of first pages are outside the sample ({SAMPLE_STUDENTS} sampled students in the runbook's example, {c('rbStderr')}, over HW1's class of {CLASS_SIZE}, {c('rbClass')}, or over {FIRST_DRAFT_CLASS}, the first draft's divisor; trouble about 0.10: the button is first, in view, and named) "
                     f"and about {in_pct}% inside it (trouble about 0.20: the runbook says where Queue is, but it is a long scroll): {mix_range(0.10, 0.20)} at either end of the range, set at 0.15"),
        dict(id="Q2", steps=[("queue", 1)], event="the first page after the load is a student inside the sample (a pair header, no queue note), so the owner starts on a pair",
             observable="the first screenshot or sentence after the toast shows 'Sample Qn, pair k of 5'", p=0.58, basis="declared",
             rests_on=f"{SAMPLE_STUDENTS} sampled students in the runbook's example ({c('rbStderr')}) over HW1's class of {CLASS_SIZE} ({c('rbClass')}) is {round(100 * CS['in_lo'])}% of first pages; over {FIRST_DRAFT_CLASS}, the first draft's divisor (the students HW1's correction touched, {c('tgClass')}), {round(100 * CS['in_hi'])}%. p keeps the upper end. A path prediction, not a friction; the real numbers will differ"),
        dict(id="Q3", steps=[("queue", 1), ("queue", 4)], event="unsure which sample or file is loaded, or whether it is the current one",
             observable="the narration questions where the list came from or whether it is the right sample", p=0.1, basis="declared",
             rests_on="two causal findings: neither the note nor the queue says where the sample came from"),
        dict(id="Q4", steps=[("queue", 6)], event="Next pair does not open Q1, pair 1, or the owner is surprised by where it goes",
             observable="the narration says it opened something unexpected", p=0.05, basis="declared",
             rests_on=f"code: sampleNext opens the first pair not recorded ({c('sampleNext')}), by question then by user id ({c('samplePairs')}); a nothing-goes-wrong prediction"),
        dict(id="Q5", steps=[("queue", 1)], event="the owner is confused by 'Changes Canvas' and a Save and next on a student outside the sample (normal grading)",
             observable="the narration mentions the normal grading page, its Save and next, or fear of writing to Canvas", p=0.12, basis="measured",
             rests_on=f"[measured: first_contact.outside_sample, primary_action] purpose tag '{OS['purpose_tag']}' and a Save and next with the same label, {PA['Save and next']['with_normal_grading']['edge_move_px']:.0f} px from where the pass-mode one sits; the note that says what the page is ('Save writes to Canvas') is the first thing in the body, before the purpose line (index {OS['notice']['index_in_body']} against {OS['notice']['purpose_line_index']}), and its button is {hint_in_view}% in view under the toast. "
                     "p is a judgment, lower than it would be with the note out of view or after the purpose line. A question that names Canvas stands before the write; it comes only after Mark rest full and Save and next, so p is not lowered for it"),
        # --- S3 pair
        dict(id="P1", steps=[("pair", 7), ("pair-reload", 7), ("pair-reload", 16), ("pair-lock", 8)],
             event="within a pair the owner forgets what the work or the key said while choosing chips, and goes back to re-read (a loss at the chip decision)",
             observable="the narration says they forgot, lost, or had to go back to the work or the key inside one question", p=0.55, basis="declared",
             rests_on=f"dataflow: working set 4 > B=3 at the chip decision (the step needs 2, two items are held); [measured: chips.at_the_default_sheet.key_in_view_with_a_chip] the key is out of view while a chip of its part is in view in {100 * key_out:.0f}% of the views in the invented large bank and {100 * a_key_out:.0f}% in the example-size bank, so p is between 0.65 (large) and about 0.45 (small); HW1 B5 and B6 state the same shape for chips (hold the conclusions, forget one, scroll back)"),
        dict(id="P2", steps=[("pair", 5), ("pair", 6)], event="the small chip window (scrolling, no chip on the first screen) is reported as slow or tiring, or the owner resizes or hides the sheet",
             observable="the narration mentions the size of the sheet, the scrolling in it, dragging it, or hiding it", p=0.7, basis="measured",
             rests_on=f"[measured: window] {pv['body_h']:.0f} px open ({pv['body_pct_of_screen']:.0f}% of the screen; {pvt['body_h']:.0f} px while a toast is up), median {scr['median']} screens per question in the invented large bank and {A_scr['median']} in the example-size bank, no chip on the first screen in either; p is between 0.8 (large) and about 0.6 (small)"),
        dict(id="P3", steps=[("pair", 3)], event="finding the answer to the question inside the student's submission is described as the slow part of a pair",
             observable="the narration says finding the question, the part or the page in the student's work takes the time", p=0.6, basis="guess",
             rests_on="outside TapGrade and unmeasured; HW1 I3 names the same kind of cost in another task"),
        dict(id="P4", steps=[("pair", 8)], event="a tap lands on the wrong chip, or content moves under the finger (the toast leaving, a warning line appearing)",
             observable="the narration says something moved, jumped, or a wrong chip was tapped", p=0.3, basis="measured",
             rests_on=f"[measured: view_stability] the toast leaving moves the list {VS['load_toast']['content_moves_when_it_goes_px']:.0f} px after about four seconds; a second chip in a part pushes everything below down {VS['second_chip_in_a_part']['content_below_pushed_down_px']:.0f} px"),
        dict(id="P5", steps=[("pair", 8)], event="the owner uses None (a part not attempted) and the sheet jumps to the top, and says so",
             observable="the narration says the list jumped back to the top after a tap", p=0.2, basis="measured",
             rests_on=f"[measured: view_stability.none_tap] None jumps the sheet from {VS['none_tap']['scroll_before_px']:,.0f} px down to the top; whether None is used at all is a guess (about one in two)"),
        dict(id="P6", steps=[("pair", 1), ("pair-reload", 1), ("pair-reload", 10), ("install", 10)],
             event="the owner reports a wrong or confusing message while a page loads ('Pick a student in SpeedGrader', 'Changes Canvas', a bare student number)",
             observable="the narration or a screenshot shows and mentions one of those messages", p=0.2, basis="measured",
             rests_on=f"[measured: loading] with the mock's read of one student slowed by {LD['mock_submission_read_delay_s']} s, the sheet says 'Pick a student' for {LD['seconds_in_the_pick_a_student_state']} s and 'Changes Canvas' first; their length on a real Canvas is unknown"),
        dict(id="P7", steps=[("pair", 1)], event="the wait between pairs is reported as slow or stuck at least once",
             observable="the narration says loading was slow or stuck, or a refresh was made because of it", p=0.55, basis="declared",
             rests_on=f"code: every pair is a full SpeedGrader page load; [measured: loading] the mock alone needs {LD['seconds_from_tap_to_pair_ready_on_the_mock_alone']} s; HW1 reports 'stuck' three times (E5, G1, G7)"),
        dict(id="P8", steps=[("pair", 9), ("pair-reload", 18), ("pair-lock", 10)], event="before saving, the owner scrolls back through the list to check what was picked, or is unsure every part was done",
             observable="the narration says they checked or re-scrolled before Save, or doubted completeness", p=0.3, basis="declared",
             rests_on=f"colocation finding: the picks are spread over {scr['min']:.0f} to {scr['max']:.0f} screens in the invented large bank, {A_scr['min']:.0f} to {A_scr['max']:.0f} in the example-size one ([measured: window.screens_per_question]); only the head stamp totals them; p is between 0.4 (large) and about 0.25 (small)"),
        dict(id="P9", steps=[("pair", 9), ("pair-reload", 18), ("pair-lock", 10)], event="the owner doubts a save registered, or reopens a recorded pair to check",
             observable="the narration says they were unsure it saved, or a screenshot shows a reopened pair", p=0.25, basis="declared",
             rests_on="commit_correctness finding: the only check is the read-back; HW1 H3 states a doubt of this kind (is the display wrong because I did not refresh)"),
        dict(id="P10", steps=[("pair", 9)], event="the owner taps Save instead of Save and next (or the reverse)",
             observable="the narration says the wrong one of the two was tapped", p=0.1, basis="measured",
             rests_on=f"[measured: primary_action] {PA['gap_between_save_and_save_and_next_px']:.0f} px apart, {save[0]:.0f} and {sn[0]:.0f} px wide, label x shape similarity {PA['save_vs_save_and_next_similarity']}"),
        dict(id="P11", steps=[("pair", 9)], event="the owner saves a student outside the sample in normal mode (a write to Canvas)",
             observable="the narration or the Canvas gradebook shows a grade written for a student not in the sample", p=0.01, basis="measured",
             rests_on=f"[measured: first_contact.outside_sample.tap_save_and_next, first_contact.outside_sample.save_and_next_disabled] Save and next is disabled until 'Mark rest full' is tapped, and after it Save and next asks first (answer: {'yes' if SV['asks_first'] else 'no'}); the question names the blind pass ({'yes' if SV['names_the_blind_pass'] else 'no'}) and says it writes to Canvas ({'yes' if SV['says_it_writes_to_canvas'] else 'no'}); Cancel sends {SV['writes_after_cancel']} requests that write, OK sends {SV['writes_after_ok']}. "
                     f"A write through Save and next takes at least three taps (Mark rest full, Save and next, OK), the last on a question that says what it does (a nothing-goes-wrong prediction; the question is asked in save(), {c('saveAsks')}, so a plain Save asks too: code). p is a judgment, lower than it was when the first draft's script let Save and next write with no question (the section on what changed in TapGrade lists the values)"),
        dict(id="P12", steps=[("pair", 7)], event="the owner dithers between look-alike chips (two similarly worded reasons in one part)",
             observable="the narration says two chips looked alike or the right one was hard to tell", p=0.2, basis="measured",
             rests_on=f"[measured: chips.reason_labels] {len(look['pairs_at_or_above_0.5'])} of {look['pairs']} reason pairs score 0.5 or more ({', '.join(look['pairs_at_or_above_0.5'])}); about {100 * share_part:.0f}% of parts and {100 * share_pair:.0f}% of pairs (at {parts_per_pair:.1f} parts per pair) hold one in the invented large bank, {100 * a_share_part:.0f}% and {100 * a_share_pair:.0f}% in the example-size one (about two chips per part); p is a guess between the two, low because few pairs of labels look alike"),
        dict(id="P13", steps=[("pair", 9), ("pair-lock", 1)], event="a pick recorded on one page is lost, or a page shows an old count, after the owner goes back to an earlier page (the back swipe) or opens a second tab",
             observable="the narration says a recorded pair showed as not recorded, a count went back, or a pick was gone after going back or switching tabs", p=0.05, basis="measured",
             rests_on=f"[measured: two_pages] a save from a page that did not know of another page's pick kept both ({spp['picks_after_the_other_page_saved']} pick, then {spp['picks_after_this_page_saved']}: none lost, {c('sampleSaveMerge')}), and a page that came back showed the other page's save with no reload (the queue line '{rts['queue_line_for_the_pair_the_other_page_recorded']['before']}' became '{rts['queue_line_for_the_pair_the_other_page_recorded']['after']}', {c('visibilitychange')}, {c('pageshow')}); "
                     "every Save and next is a full page load (go(), location.assign), so a back swipe does return to the previous student's page [declared from code]. Headless Chromium on a mock, not Safari's back/forward cache: not tried. A nothing-goes-wrong prediction: the first-draft script lost the other page's pick in this same test"),
        # --- S4 pair-reload
        dict(id="R1", steps=[("pair-reload", 9)], event="a reload (a refresh, or a page the phone discarded) happens in the middle of a pair at least once",
             observable="the narration or a screenshot shows a reload while a pair was half picked", p=0.55, basis="carried-from-HW1",
             rests_on="HW1: refreshes at E6, G3 and H on 2026-10-03 (and B2, the usual pattern); here 45 page loads give 45 chances"),
        dict(id="R2", steps=[("pair-reload", 9)], event="after a reload the half-picked pair is found empty and the owner says the picks were lost",
             observable="the narration says the ticks or the note were gone after a reload", p=0.4, basis="declared",
             rests_on=f"code: a half-picked pair is not kept on purpose; [measured: interruption] ticked {IN['reload_with_a_half_picked_pair']['ticked_before']} before and {IN['reload_with_a_half_picked_pair']['ticked_after']} after, the note gone, the foot says nothing is picked"),
        dict(id="R3", steps=[("pair-reload", 11)], event="after a reload or a return the owner says they did not know where they were (which part, which pair)",
             observable="the narration says they had to find the place again", p=0.35, basis="carried-from-HW1",
             rests_on="HW1 G4: after a refresh the narrator found the place by reading the chips again"),
        # --- S5 pair-lock
        dict(id="L1", steps=[("pair-lock", 1)], event="the phone locks between pairs at least once and the owner says so",
             observable="the narration says the phone locked or the owner left and came back", p=0.35, basis="guess",
             rests_on="auto-lock is a setting nobody has stated; a long pass makes a lock likely, a mention less so"),
        dict(id="L2", steps=[("pair-lock", 1)], event="picks are lost across a lock or an app switch that did not reload the page",
             observable="the narration says picks were gone after a lock or app switch with no reload", p=0.1, basis="measured",
             rests_on="[measured: interruption.app_switch_without_reload] ticks kept when the page is hidden and shown again; the handler that reads the picks again on a visible page drops only a draft nobody touched (a nothing-goes-wrong prediction; a page the phone discarded is S4)"),
        dict(id="L3", steps=[("pair-lock", 1)], event="Canvas asks for a new login after a lock or a long pause",
             observable="the narration or a screenshot shows a login page mid-pass", p=0.12, basis="carried-from-HW1",
             rests_on="HW1 E5 states the worry that the login had timed out"),
        dict(id="L4", steps=[("pair-lock", 2)], event="after a lock the owner says they had to find the thread again",
             observable="the narration says they re-found the pair, the student or the place in the work", p=0.4, basis="carried-from-HW1",
             rests_on="HW1 G4; the header names the pair, which makes it easier than after a reload"),
        # --- S6 export
        dict(id="E1", steps=[("export", 2)], event="cannot find Sample picks at first",
             observable="the narration says the tab was hard to find", p=0.25, basis="measured",
             rests_on=f"[measured: export.check_sub_tabs] Check opens on Review; Sample picks is the fifth of {EX['check_sub_tabs']['count']} tabs in {EX['check_sub_tabs']['font_px']} px type (all fit without scrolling)"),
        dict(id="E2", steps=[("export", 5)], event="Copy as JSON is not in view when the tab opens and the owner scrolls looking for it",
             observable="the narration says the button was below or hidden", p=0.4, basis="measured",
             rests_on=f"[measured: export.sample_picks_view] {EX['sample_picks_view']['copy_as_json_below_the_open_body_px']:.0f} px below the open part of a {EX['sample_picks_view']['body_h']} px body; the view has no foot"),
        dict(id="E3", steps=[("export", 6)], event="'Copy blocked here' appears (the clipboard is refused)",
             observable="a screenshot or the narration shows that message or a manual copy", p=0.25, basis="guess",
             rests_on="the clipboard in an iPhone userscript extension has not been tried"),
        dict(id="E4", steps=[("export", 4)], event="the export is made while pairs are still missing (the warning is on screen)",
             observable="a screenshot shows 'N of 45 pairs are not recorded', N above 0", p=0.3, basis="guess",
             rests_on="the owner may test the export early; nothing forces it"),
        dict(id="E5", steps=[("export", 1), ("export", 7)], event="the export is done with no narrated difficulty",
             observable="the export is narrated and no difficulty is stated in it", p=0.25, basis="measured",
             rests_on="no verifier fires on this chain, but two measured frictions (E1, E2) make a clean run unlikely: a nothing-goes-wrong prediction at p=0.25, so friction is predicted at 75%"),
        # --- S7 hand-back
        dict(id="H1", steps=[("handback", 5)], event="the long paste is shortened, becomes an attachment, or needs a second try",
             observable="the narration says the paste failed, was cut, or was done twice", p=0.3, basis="guess",
             rests_on=f"[measured: export.complete_export_estimate] about {est['chars']:,} characters in about {est['lines']} lines (estimated from a {EX['copy_as_json']['picks']}-pick copy); what the chat app does with that is not known"),
        dict(id="H2", steps=[("handback", 2)], event="the owner has to search for the coordinating session's conversation",
             observable="the narration says they looked for the chat", p=0.4, basis="carried-from-HW1",
             rests_on="HW1 E3: open the chat app, find the conversation, locate the line"),
        dict(id="H3", steps=[("handback", 6)], event="the owner is unsure the paste arrived whole until the session answers",
             observable="the narration says they were unsure it went through intact", p=0.3, basis="declared",
             rests_on="commit_correctness finding: the chat app offers no check after Send"),
    ]
    return ev


def predictors(MJ: dict, AJ: dict, inputs: dict) -> list[dict]:
    """Section 3 of the registration: what was measured on the artifact (content-blind, theory section 9), what was declared from reading the code, what is carried, what is guessed."""
    c = Cites(inputs["citations"])
    M, A = MJ["predictors"], AJ["predictors"]
    W, PA, CHP, FB, VS, LD, FC, EX, IN, TP = M["window"], M["primary_action"], M["chips"], M["feedback_ms"], M["view_stability"], M["loading"], M["first_contact"], M["export"], M["interruption"], M["two_pages"]
    ch, rl = CHP["at_the_default_sheet"], CHP["reason_labels"]
    sn, npair = PA["Save and next"], PA["Next pair"]
    OS = FC["outside_sample"]
    fb = [v["ms"] for v in FB.values()]
    pv, pvt, big = W["pair_view"], W["pair_view_with_toast"], W["pair_view_largest_sheet"]
    scr = W["screens_per_question"]
    spp, rts = TP["stale_page_save"], TP["return_to_a_stale_page"]
    rows = [
        # measured
        dict(family="anchor", what="Save and next across the states of a pair (toast, nothing picked, one chip, many chips, scrolled to the end, half point, saved, changed after saving)",
             value=f"edges move {sn['pass']['edge_move_px']:.0f} px over {sn['pass']['states']} states: fixed-position. With normal grading present (a student outside the sample) it sits {sn['with_normal_grading']['edge_move_px']:.0f} px higher",
             used_at="S3:9; S4:18; S5:10", label="measured", key="primary_action.Save and next"),
        dict(family="anchor", what="Next pair against Save and next (same place for two jobs)",
             value=f"Next pair moves {npair['pass']['edge_move_px']:.0f} px over {npair['pass']['states']} states; right and bottom edges are {PA['queue_next_pair_vs_pair_save_and_next']['right_edge_delta_px']:.0f} px from where Save and next sits, the overlap is {100 * PA['queue_next_pair_vs_pair_save_and_next']['overlap_fraction_of_smaller']:.0f}% of the smaller button",
             used_at="S2:5", label="measured", key="primary_action.Next pair"),
        dict(family="anchor", what="the bar's four buttons: distance to a screen edge",
             value=f"{PA['bar_buttons']['distance_to_bottom_edge_px']:.0f} px from the bottom, {PA['bar_buttons']['distance_to_left_edge_px']:.0f} px from the sides (inset 0 px in this browser)",
             used_at="S6:1", label="measured", key="primary_action.bar_buttons"),
        dict(family="confusables", what="chips of one part: how many, how alike (label x shape similarity, 0 to 1)",
             value=f"{ch['chips_per_part']['mean']} chips per part ({ch['chips_per_part']['min']}-{ch['chips_per_part']['max']}); at most {ch['in_view']['max_fully_visible_together']} fully in view together at the default sheet (mean {ch['in_view']['mean_fully_visible']}); mean of the largest pair in a part {ch['within_part_similarity']['mean_of_largest_pair']}; "
                   f"{ch['within_part_similarity']['parts_with_a_pair_at_or_above_0.5']} of {ch['within_part_similarity']['parts_compared']} parts hold a pair at 0.5 or more; at the largest sheet {CHP['at_the_largest_sheet']['in_view']['identical_label_pairs_seen_together']} same-label pairs are in view together",
             used_at="S3:7; S4:7, 16; S5:8", label="measured", key="chips.at_the_default_sheet"),
        dict(family="confusables", what="the twelve reason labels, in the simulated frequency of the sample",
             value=f"{len(rl['pairs_at_or_above_0.5'])} of {rl['pairs']} label pairs score 0.5 or more ({', '.join(rl['pairs_at_or_above_0.5'])}); {100 * rl['share_of_parts_with_such_a_pair_simulated']:.0f}% of simulated parts hold such a pair",
             used_at="S3:7 (P12)", label="measured", key="chips.reason_labels"),
        dict(family="confusables", what="Save against Save and next; the five Check tabs",
             value=f"{PA['save_vs_save_and_next_similarity']} ({PA['save_vs_save_and_next_label_similarity']} by label alone), {PA['gap_between_save_and_save_and_next_px']:.0f} px apart; tabs: largest pair {EX['check_sub_tabs']['largest_label_x_shape_similarity']}",
             used_at="S3:9; S6:2", label="measured", key="primary_action, export.check_sub_tabs"),
        dict(family="co-location", what="the key of a part against its chips: is the key in view while a chip of the part is?",
             value=f"in {100 * ch['key_in_view_with_a_chip']['share']:.0f}% of the views in which a chip is in view ({100 * A['chips']['at_the_default_sheet']['key_in_view_with_a_chip']['share']:.0f}% in the example-size bank); {100 * ch['part_group_height_px']['share_that_fit_in_the_open_body']:.0f}% of part groups (header, key, chips) fit the open body whole ({100 * A['chips']['at_the_default_sheet']['part_group_height_px']['share_that_fit_in_the_open_body']:.0f}%); mean group {ch['part_group_height_px']['mean']:.0f} px ({A['chips']['at_the_default_sheet']['part_group_height_px']['mean']:.0f} px)",
             used_at="S3:6, 7; S4:6, 7, 15, 16; S5:7, 8", label="measured", key="chips.at_the_default_sheet.key_in_view_with_a_chip"),
        dict(family="feedback", what="DOM change after each tap (chip, half point, No deductions, Save, Save and next, Check, Sample picks, Copy as JSON)",
             value=f"{min(fb):.0f}-{max(fb):.0f} ms in every case in headless Chromium (immediate means under 300 ms); a phone is slower: not measured",
             used_at="S3:8, 9; S6:3, 6", label="measured", key="feedback_ms"),
        dict(family="view stability", what="what moves under the finger",
             value=f"the load toast leaving moves the content {VS['load_toast']['content_moves_when_it_goes_px']:.0f} px after about four seconds; a second chip in a part pushes the content below down {VS['second_chip_in_a_part']['content_below_pushed_down_px']:.0f} px; a chip tap moves it {VS['chip_tap']['max_chip_shift_px']:.0f} px; "
                   f"None, No deductions, the Grade button, hiding and resizing the sheet all throw the list back to the top (None from {VS['none_tap']['scroll_before_px']:,.0f} px) and keep the ticks",
             used_at="S3:3, 5, 8", label="measured", key="view_stability"),
        dict(family="window", what="the sheet on a 390x844 screen",
             value=f"sheet {pv['sheet_h']:.0f} px ({pv['sheet_pct']:.0f}% of the screen); its one scroller {pv['body_h']:.0f} px ({pv['body_pct_of_screen']:.0f}%; {A['window']['pair_view']['body_h']:.0f} px in the example-size bank), {pvt['body_h']:.0f} px while a toast is up; no chip on the first screen in either bank; {scr['median']} screens per question (median; {scr['min']}-{scr['max']}), {A['window']['screens_per_question']['median']} in the example-size bank ({A['window']['screens_per_question']['min']}-{A['window']['screens_per_question']['max']}); "
                   f"pulled to its largest the sheet leaves the work {big['work_area_above_sheet_h']:.0f} px ({big['work_area_pct']:.0f}%); the Queue button is {W['queue_button_from_pair']['screens_down']} screens down from a pair ({A['window']['queue_button_from_pair']['screens_down']} in the example-size bank)",
             used_at="S3:3, 5, 6; S2:2", label="measured", key="window"),
        dict(family="first contact", what=f"the first page for a student outside the sample (about {pct_range(class_shares()['out_lo'], class_shares()['out_hi'])}% of first pages)",
             value=f"the note 'Save writes to Canvas' is the first element of the open body (index {OS['notice']['index_in_body']}; the purpose line, 'Changes Canvas', is {OS['notice']['purpose_line_index']}); its 'Open the sample queue' button is {100 * OS['hint_button_visible_fraction_with_toast']:.0f}% inside the open part with the load toast up and {100 * OS['hint_button_visible_fraction_without_toast']:.0f}% without it; "
                   f"the normal foot is there too (Save and next present: {'yes' if OS['save_and_next_present'] else 'no'}, disabled until Mark rest full: {'yes' if OS['save_and_next_disabled'] else 'no'}); no sub tabs",
             used_at="S2:1, 2", label="measured", key="first_contact.outside_sample"),
        dict(family="page load", what="the sheet's states while the next student's page loads (the mock's read slowed by 1.2 s)",
             value=f"{len(LD['states'])} states: 'Changes Canvas' with a bare student number, then 'Pick a student in SpeedGrader' for {LD['seconds_in_the_pick_a_student_state']} s, then the pair; {LD['seconds_from_tap_to_pair_ready']} s from the tap to a ready pair ({LD['seconds_from_tap_to_pair_ready_on_the_mock_alone']} s on the mock alone); the save's toast shows on the next page",
             used_at="S3:1; S4:1, 10; S1:10", label="measured", key="loading"),
        dict(family="interruption", what="reload and app switch in the middle of a pair",
             value=f"a reload with one chip ticked leaves {IN['reload_with_a_half_picked_pair']['ticked_after']} ticked and no note, the same pair shown again; an app switch without a reload keeps the {IN['app_switch_without_reload']['ticked_after']} tick; a saved pair comes back recorded",
             used_at="S4:9; S5:1", label="measured", key="interruption"),
        dict(family="two pages", what="two pages of one phone (a stale page saves; a page is put away and comes back)",
             value=f"a save from a page that did not know of another page's pick keeps both ({spp['picks_after_the_other_page_saved']} pick, then {spp['picks_after_this_page_saved']}); a page that comes back shows the other page's save with no reload (the queue line '{rts['queue_line_for_the_pair_the_other_page_recorded']['before']}' becomes '{rts['queue_line_for_the_pair_the_other_page_recorded']['after']}'). The first-draft script lost the other page's pick in the same test",
             used_at="S3:9; S5:1", label="measured", key="two_pages"),
        dict(family="export", what="the Sample picks view and the copy",
             value=f"Check opens on another tab; Sample picks is the fifth of {EX['check_sub_tabs']['count']}; Copy as JSON sits {EX['sample_picks_view']['copy_as_json_below_the_open_body_px']:.0f} px below the open {EX['sample_picks_view']['body_h']} px body (no foot); the missing-pairs warning shows; "
                   f"a complete export is about {EX['complete_export_estimate']['chars']:,} characters in {EX['complete_export_estimate']['lines']} lines",
             used_at="S6:2-7; S7:5", label="measured", key="export"),
        # declared from reading the code, and the judgments the verifiers read
        dict(family="progress", what="whether the sheet shows progress while a page loads", value="the second loading state tells the owner to pick a student: progress_visible false", used_at="S3:1; S4:1, 10; S1:10", label="declared", key=""),
        dict(family="commit", what="what Save and next leaves on the screen",
             value=f"the picks are spread over {scr['min']:.0f}-{scr['max']:.0f} screens of a {pv['body_h']:.0f} px window: everything_on_screen false; the save can be changed afterwards (reversible, not idempotent); the only check is the foot's 'Recorded HH:MM' and the head's tally (consistency)",
             used_at="S3:9; S4:18; S5:10", label="declared", key=""),
        dict(family="origin", what="whether the queue and the note say where the sample came from", value="neither does (origin_stated false)", used_at="S2:1, 4", label="declared", key=""),
        dict(family="interruption", what="what a reload keeps", value=f"position (the same student) and the recorded pairs; not a half-picked pair (dropped on purpose, {c('rulesHalfPicked')})", used_at="S4:9", label="declared", key=""),
        dict(family="memory", what="the dataflow items (section 2) and the held lists derived from them", value="at most 2 items held across a step; the chip decision needs 2 and holds 2: working set 4", used_at="all chains", label="declared", key=""),
        # carried and guessed
        dict(family="install", what="the save-from-chat steps (card, three dots, Save to Files, folder, Save)", value="HW1's stated properties: fixed or edge anchors, no look-alike on the card, a scroll and a two-part read for the menu item, the remembered folder costs nothing", used_at="S1:2-7", label="carried-from-HW1", key=""),
        dict(family="amounts", what="the real bank's size, parts per pair (4), taps per pair (3), pages read per pair, the chat steps, the paste, the clipboard", value=f"not measured and not stated by anyone. The invented bank has {MJ['sample']['chips']} chips in {MJ['sample']['parts']} parts; the runbook's example output says {EXAMPLE_ITEMS} bank items ({c('rbStderr')}), {EXAMPLE_ITEMS} chips in all, so a bank of that size ({AJ['sample']['chips']} chips in {AJ['sample']['parts']} parts) was measured too (section 3b)", used_at="S3:3-8; S7; S6:6", label="guess", key=""),
    ]
    return rows
