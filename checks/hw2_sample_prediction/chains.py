"""The seven chains of the HW2 blind sample pass (checks/fixtures/chains/tapgrade_0_6_7_sample_pass.json), written from the code and docs of a
TapGrade snapshot and from the measured files, not from anyone using the flow.

`build(MJ, AJ, inputs)` returns (the chain document, the dataflow table).  MJ and AJ are the two measured files (invented bank of 137 chips,
and of the runbook's example size); `inputs` is docs/predictions/hw2-sample-pass.inputs.json.  Nothing measured is typed here: every number a
note quotes is read from MJ or AJ, and every `userscripts/tapgrade.user.js:A-B` is looked up in the inputs by its anchor (cites.py).

Evidence tags in a note: `file:LINES` (the snapshot's code and docs: `docs/HW2-HW3-RUNBOOK.md:LINES` is found by anchor like a line of the script), `HW1 <entry id>`,
`[measured: key]`, `[declared from code reading]`, `[carried: unstated]` (the checker's default, or a value nobody stated: P-02be), `[guess]`.
A sentence about what the docs say carries the line it rests on: the anchor's pattern holds the words the sentence relies on (cites.py).
"""
from __future__ import annotations

from .cites import CLASS_SIZE, EXAMPLE_ITEMS, EXAMPLE_QUESTIONS, FIRST_DRAFT_CLASS, SAMPLE_STUDENTS, Cites, class_shares, pct_range
from .events import CEC1BBA

yn = lambda b: "yes" if b else "no"

# labels of the memory items (the same text in `held` and in the dataflow table of the registration)
G_INSTALL = "goal: put the data script in the Userscripts folder and see it load"
X_NUMBERS = "expected: the numbers the chat gave (questions, pairs)"
P_QUEUE = "plan: open the queue, then Next pair"
W_ITEM = "what the student wrote for this part"
K_ITEM = "what the key says for this part"
C_ITEM = "which chips of this part were judged"
G_EXPORT = "goal: copy the picks and hand them to the chat"
PAIR_ID, RELOAD_ID, LOCK_ID = (f"tapgrade-0.6.7-sample-{x}" for x in ("pair", "pair-reload", "pair-lock"))


def st(op, target, note, **kw):
    d = {"op": op}
    d.update(kw)
    d["target"] = target
    d["note"] = note
    return d


def build(MJ: dict, AJ: dict, inputs: dict) -> tuple[dict, dict]:
    c = Cites(inputs["citations"])
    sk = inputs["speeds_kit"]
    scr = sk["script"]
    M, SMP = MJ["predictors"], MJ["sample"]
    ALT, ASMP = AJ["predictors"], AJ["sample"]
    assert MJ["script"]["sha256"] == AJ["script"]["sha256"] == scr["sha256"], "the two measured files and the inputs are of the same script"
    assert SMP["bank"] == "large" and ASMP["bank"] == "example"

    W, PA, CH, FB, VS = M["window"], M["primary_action"], M["chips"]["at_the_default_sheet"], M["feedback_ms"], M["view_stability"]
    LD, FC, IN, EX, TP = M["loading"], M["first_contact"], M["interruption"], M["export"], M["two_pages"]
    OS = FC["outside_sample"]
    sn, npair = PA["Save and next"]["pass"], PA["Next pair"]["pass"]
    parts_per_pair = 4
    chips_per_part = CH["chips_per_part"]["mean"]
    visible_any = CH["in_view"]["mean_fully_visible_when_any"]
    look_count = max(1, round(visible_any) - 1)
    sim = CH["within_part_similarity"]["mean_of_largest_pair"]
    screens_med = W["screens_per_question"]["median"]
    A_W, A_CH = ALT["window"], ALT["chips"]["at_the_default_sheet"]
    KEY = CH["key_in_view_with_a_chip"]["share"]
    GRP = CH["part_group_height_px"]
    A_KEY, A_GRP = A_CH["key_in_view_with_a_chip"]["share"], A_CH["part_group_height_px"]
    body_h, body_toast = W["pair_view"]["body_h"], W["pair_view_with_toast"]["body_h"]
    work_h, work_pct = W["pair_view"]["work_area_above_sheet_h"], W["pair_view"]["work_area_pct"]
    big = W["pair_view_largest_sheet"]
    work_big = big["work_area_above_sheet_h"]
    lg_max = M["chips"]["at_the_largest_sheet"]["in_view"]["max_fully_visible_together"]
    lg_ident = M["chips"]["at_the_largest_sheet"]["in_view"]["identical_label_pairs_seen_together"]
    spp = TP["stale_page_save"]
    SV = OS["tap_save_and_next"]
    rts = TP["return_to_a_stale_page"]
    NM, HS, RS = VS["next_pair_message"], VS["hide_and_reopen_the_sheet"], VS["resize_the_sheet_by_dragging_its_head"]
    slack = FC["pair_title_slack_px_one_pair_per_question"]
    kept = lambda d: d["scroll_after_px"] > 1 or d["scroll_before_px"] <= 1       # a tap that rebuilds the sheet did not throw the list to the top
    NT = VS["none_tap"]
    RW, FL, PH = VS.get("rebuild_with_ticks"), VS.get("sheet_at_its_floor"), W["part_headings_at_the_first_render"]
    rebuild_text = ("a rebuild with ticks was not measured" if not RW else
                    f"with {RW['ticked_chips']} chips ticked in a part, so that its warning is above the window ({RW['warnings_above_the_window_before']} warning there), hiding the sheet and opening it leaves a chip far below at the same place against the top of the window "
                    f"(moved {RW['same_chip_shift_px']:g} px; the warning is drawn again: {yn(RW['warnings_after_the_rebuild'] >= RW['warnings_before'])}; {c('renderTallies')}; {c('tgTallies')})" if abs(RW["same_chip_shift_px"]) < 1 else
                    f"with {RW['ticked_chips']} chips ticked in a part, hiding the sheet and opening it moves a chip far below by {RW['same_chip_shift_px']:g} px against the top of the window (the warning is not drawn again)")
    floor_text = ("the sheet at its lowest height was not measured" if not FL else
                  f"a sheet pulled down to its lowest height is raised by the load message {FL['raised_by_the_message_px']:g} px" + (" and stays raised when the message has gone" if FL["stays_raised_after_it_left"] else f" and is the same height when it has gone ({FL['sheet_h_after_it_left_px']:g} px; {c('sheetFloor')}; {c('tgFloor')})"))
    none_text = ("None was not measured (no part of the invented sample has the button)" if not NT else f"a tap on None leaves the list where it was ({NT['scroll_before_px']:,.0f} px before the tap, {NT['scroll_after_px']:,.0f} px after it; {c('renderKeepScroll')})" if kept(NT)
                 else f"a tap on None throws the list to the top ({NT['scroll_before_px']:,.0f} px before the tap, {NT['scroll_after_px']:,.0f} px after it)")
    assert W["pair_view_with_toast"]["body_h"] == W["pair_view"]["body_h"], "a message takes room from the list again: re-read the notes that say it floats above the sheet (pair WAIT, install step 11, queue step 2, export step 7)"
    CS = class_shares()                                  # the share of first pages in and outside the sample, from the docs' numbers (cites.py)
    in_pct, out_pct = pct_range(CS["in_lo"], CS["in_hi"]), pct_range(CS["out_lo"], CS["out_hi"])
    class_basis = (f"{SAMPLE_STUDENTS} sampled students in the runbook's example ({c('rbStderr')}) over HW1's class of {CLASS_SIZE} ({c('rbClass')}), "
                   f"or over {FIRST_DRAFT_CLASS}, the students HW1's correction touched ({c('tgClass')}; the first draft's divisor)")

    # ---- steps shared by the pair chains ------------------------------------------------------------------------------------------------
    def s_wait_load(extra="", target="the next student's page loads (Save and next, or Next pair, replaced the page 350 ms after the tap): the sheet shows 'Student <id>', 'Loading the rubric from Canvas…', then 'Pick a student in SpeedGrader…' until the submission arrives, then the pair"):
        return st("WAIT", target,
                  f"{c('go')} go(): 350 ms, then location.assign (a full SpeedGrader load for every new student); {c('loadingRubric')} 'Loading the rubric from Canvas…'; {c('pickAStudent')} 'Pick a student in SpeedGrader. TapGrade follows the student shown in the address bar.' while the submission is read (a wrong instruction); {c('sampleFocusNotice')} and {c('sampleSaveNext')}: the message of the save that brought us here is shown once, on this page. It floats above the sheet ({c('msgCss')}): [measured: view_stability.next_pair_message] {NM['height_px']:.0f} px high, it covers {NM['over_the_page_px']:.0f} px of the {NM['work_area_h_px']:.0f} px of the student's work above the sheet ({NM['share_of_the_work_area_pct']:.0f}%) for about four seconds and takes no room from the list. "
                  f"[measured: loading] with the mock's read of one student slowed by {LD['mock_submission_read_delay_s']} s: the first sheet state carries the purpose tag 'Changes Canvas' (measured: {yn(LD['first_new_state_says_changes_canvas'])}), then {LD['seconds_in_the_pick_a_student_state']} s of 'Pick a student in SpeedGrader', a bare student number in the head, no foot, no chips; the pair is ready {LD['seconds_from_tap_to_pair_ready']} s after the tap (the mock alone: {LD['seconds_from_tap_to_pair_ready_on_the_mock_alone']} s). How long a real Canvas takes is [guess]. "
                  f"progress_visible false: the sheet's own text gives no progress in its second state. view_stable true: the bar and the page above do not move; the sheet grows upward by {LD['sheet_top_moves_px']} px while it fills in ([measured: loading.sheet_top_moves_px]), judged not to be a jump of a view the person is working in. {extra}",
                  progress_visible=False, view_stable=True)

    def s_read_header():
        return st("READ", "the pair's header: 'Sample Q3, pair 2 of 5' and the tag 'Blind: no machine proposals'; the rows of this student that are not in the sample say '–'",
                  f"{c('sampleHead')} sampleHead; {c('sampleTag')} the tag; {c('sampleTabState')} the row tabs say 'open', '✓ done' or '–'. "
                  f"[measured: first_contact.inside_sample] the header names the pair, {FC['inside_sample']['tabs_marked_outside_sample']} of this student's row tabs are marked '–' and {FC['inside_sample']['tabs_open']} is open (this pair's). "
                  f"[measured: first_contact.pair_title_slack_px_one_pair_per_question, window.pair_view.head_h] " + (
                      f"in this container's font the title is whole in all {SMP['questions']} questions (the tightest has {slack['min']} px to spare) and the head is {W['pair_view']['head_h']:.0f} px, because a stamp of 4 or more characters is set smaller ({c('stampTier')}, {c('scoreWide')}; the cec1bba build wrapped the tag at 5 characters: the head grew to {CEC1BBA['head_with_a_wrapped_tag_px']:.0f} px); "
                      f"{c('tgHeadWhole')} says a stamp of 7 characters with a two-digit pair count is still cut off by a few px (not in this sample)"
                      if slack["clipped"] == 0 else f"in this container's font the title is clipped by the stamp beside it by up to {-slack['min']} px in {slack['clipped']} of {SMP['questions']} questions ('pair 1 of…')") +
                  f"; iPhone fonts are narrower: not counted. The runbook makes the tag a stop sign: a sampled pair without 'Blind: no machine proposals' under the header means the phone is not in the blind pass ({c('rbStopPair')}). amount 1 [guess].",
                  reading="fine", amount=1)

    def s_scan_work():
        return st("SCAN", "the student's work, above the sheet: find the answer to this question",
                  f"The work is the Canvas page behind and above the sheet. [measured: window.pair_view] the sheet leaves {work_h:.0f} px = {work_pct:.0f}% of the screen at its default height, and {big['work_area_above_sheet_h']:.0f} px = {big['work_area_pct']:.0f}% at the largest height the code allows ({c('sheetMax')} SHEET_MAX 0.85). "
                  f"To read the work with more room the owner can hide the sheet (the down arrow) or pull it down; to see more chips, pull it up: [measured: view_stability.hide_and_reopen_the_sheet / view_stability.resize_the_sheet_by_dragging_its_head] " + (
                      f"either puts the list back where it was (hiding: from {HS['scroll_before_px']:.0f} px to {HS['scroll_after_px']:.0f}; resizing: from {RS['scroll_before_px']:.0f} px to {RS['scroll_after_px']:.0f}; {c('renderKeepScroll')}, {c('hiddenTop')}; {c('tgKeepsPlace')}; the cec1bba build threw it to the top) and keeps the ticks"
                      if kept(HS) and kept(RS) else f"either throws the list back to the top (from {HS['scroll_before_px']:.0f} px to {HS['scroll_after_px']:.0f}) and keeps the ticks") + f"; [measured: view_stability.rebuild_with_ticks] {rebuild_text}; [measured: view_stability.sheet_at_its_floor] {floor_text}; at the largest height the work gets {work_big:.0f} px and the sheet shows up to {lg_max} chips together, among them {lg_ident} pairs with the same label under different parts ([measured: chips.at_the_largest_sheet]). "
                  "The mock's page is a stand-in for a submission: nothing about a real submission is measured. Amount 3 (pages or screens read) is [guess]. HW1 I3 (stated, another task): finding the question, the part and the earlier error is a cost of its own. Look-alike answers on neighbouring pages: none declared [carried: unstated].",
                  anchor="text-keyword", amount=3)

    def pair_body(times):
        """the per-part body: read the part's answer, find its group in the sheet, read its key, choose among its chips"""
        return [
            st("READ", "the student's answer to one part (above the sheet)",
               f"One copy per part; {times} parts is [guess]: the invented large bank has {SMP['parts']} parts in {SMP['questions']} questions ({SMP['parts'] / SMP['questions']:.1f} per question), the example-size bank {ASMP['parts']} ({ASMP['parts'] / ASMP['questions']:.1f}); the real count is unknown. Produces the item '{W_ITEM}': the answer lives on the work's surface, the chips on the sheet's.",
               reading="fine", amount=1, times=times),
            st("SCAN", "the sheet's list: find this part's group (header, key, chips)",
               f"[measured: window] the open part of the sheet is {body_h:.0f} px ({W['pair_view']['body_pct_of_screen']:.0f}% of the screen; {body_toast:.0f} px with a message up: it floats above the sheet and takes no room, {c('msgCss')}; the cec1bba build had {CEC1BBA['window_large_px']} px in the invented large bank, {CEC1BBA['window_with_message_large_px']} px with the message up; the docs give 188 px on a pair in the audit's pages, with or without it, {c('tgScrollPart')}); the median question's list is {screens_med} screens of it in the invented large bank ({A_W['screens_per_question']['median']} in the example-size bank, whose measurement is docs/predictions/hw2-sample-pass.measured-example-bank.json), and no chip is on the first screen in either ([measured: window.first_screen_shows_a_chip] answer: {yn(W['first_screen_shows_a_chip'])}). Sticky headers are off at this height ({c('measureBars')} measureBars, nofreeze: [measured: window.sticky_headers_off_at_this_height] answer: {yn(W['sticky_headers_off_at_this_height'])}). Amount 2 is [guess]. HW1 A3: a coarse read through look-alike text.",
               anchor="text-keyword", amount=2, times=times),
            st("READ", "the part's key, under its header ('Key: …', two lines)",
               f"{c('gkeyLine')} the key line, tap to show all; {c('gkeyCss')} clamped to two lines. [measured: chips.at_the_default_sheet.key_clamped_to_two_lines] {CH['key_clamped_to_two_lines']['clamped']} of {CH['key_clamped_to_two_lines']['keys']} keys of the invented sample (lengths as a real homework's: median 40 characters) are clamped; opening one pushes what is below down {VS['clamped_key_opened_by_a_tap']['content_below_pushed_down_px']} px. "
               f"The key sits above its chips in the same group. [measured: chips.at_the_default_sheet.key_in_view_with_a_chip] the key of a part is in view in {100 * KEY:.0f}% of the views in which one of its chips is ({100 * A_KEY:.0f}% in the example-size bank), and [measured: chips.at_the_default_sheet.part_group_height_px] only {100 * GRP['share_that_fit_in_the_open_body']:.0f}% of part groups (header, key, chips) fit the {body_h:.0f} px open part whole ({100 * A_GRP['share_that_fit_in_the_open_body']:.0f}% in the example-size bank; mean group {GRP['mean']:.0f} px, {A_GRP['mean']:.0f} px). So the key is often out of view while the later chips of its part are read: the item '{K_ITEM}' is held until the chips are judged [declared from these measurements; it is held less of the time in a small bank, and the registration's events P1 and P2 say so]. ",
               reading="fine", amount=1, times=times),
            st("DISCRIMINATE", "the part's chips: which of them applies to what the student wrote",
               f"{c('sampleChip')} sampleChip; {c('chipCodeCss')} the code under a chip is hidden in grouped view; the chip text is the reason's generic label, the same under every part of every question ({c('bankChipText')} of the snapshot). "
               f"[measured: chips.at_the_default_sheet] {chips_per_part} chips per part; where any chip is fully visible {visible_any} are, on average (largest {CH['in_view']['max_fully_visible_together']}), so {look_count} look-alike beside the target; the largest label×shape similarity inside a part averages {sim} (largest pair in the sample {CH['within_part_similarity']['largest_pair']}); "
               f"{' and '.join(CH['stripe_colour']['reasons_sharing_a_colour'])} share a stripe colour. Rule used here, fixed before the verifiers ran: count = round(mean visible) − 1; similarity = the mean over parts of the largest pair. The tail (a part with a pair at or above 0.5) is an event in the registration, not this step. "
               f"HW1 G4 (stated): chips are read one by one, the unrelated groups first; anchor text-keyword. amount = chips per part ({chips_per_part} here; {A_CH['chips_per_part']['mean']} in the example-size bank). The chips judged and passed while scrolling are the item '{C_ITEM}'.",
               confusables=[look_count, sim], anchor="text-keyword", reading="fine", amount=chips_per_part, times=times),
        ]

    def s_tap(times):
        return st("TAP", "tick the chips that apply (about three per pair)",
                  f"[measured: feedback_ms.chip] {FB['chip']['ms']} ms to the first change; the chip turns on, the part's tally, the head stamp and the foot line update in place ({c('sampleSoft')} sampleSoft). "
                  f"[measured: view_stability.chip_tap] no chip moves more than {VS['chip_tap']['max_chip_shift_px']} px; a second chip in the same part adds a warning line under that part and pushes everything below down {VS['second_chip_in_a_part']['content_below_pushed_down_px']} px ([measured: view_stability.second_chip_in_a_part]; {c('sampleTally')} sampleTally). Three taps per pair is [guess].",
                  feedback="immediate", times=times)

    def s_commit():
        return st("COMMIT", "Save and next: the pick is recorded on this phone and the next pair opens",
                  f"{c('sampleSave')} sampleSave: merges the pick into what the phone holds now, not into this page's own copy ({c('sampleSaveMerge')}), writes it and reads it back ({c('lsSetChecked')} lsSetChecked, {c('sampleSaveReadBack')}) and says 'Recorded on this phone. Nothing was sent to Canvas.' ({c('sampleSaveRecorded')}); sample code never calls Canvas ({c('rulesLocal')}). "
                  f"[measured: two_pages.stale_page_save] a save from a page that does not know of another page's pick keeps both: {spp['picks_after_the_other_page_saved']} pick after the other page saved, {spp['picks_after_this_page_saved']} after this page did (the other page's pick kept: {yn(spp['the_other_pages_pick_is_kept'])}). "
                  f"reversibility reversible: reopen from the queue, change, save again, the pick is replaced and the history keeps both saves ({c('sampleSaveRec')}, {c('sampleSaveLog')}; {c('tgFlow7')}, 'The flow, as a chain' row 7: yes, reopen, change, save: the pick is replaced). A re-save of the same draft changes nothing, so 'idempotent' would also be arguable: it would silence commit_correctness; the stricter label is used. "
                  f"preview_before true: the part tallies, the head stamp and the foot line say what will be recorded (the parts say 'full' from the first render, as after a tap: {PH['saying_full']} of {PH['parts']} on the first pair, each part heading {PH['heading_h_px']:g} px high, [measured: window.part_headings_at_the_first_render]). everything_on_screen false [judgment, as for Apply in tapgrade-0.6.6]: the picks are spread over a list of {W['screens_per_question']['min']}-{W['screens_per_question']['max']} screens of {body_h:.0f} px ({A_W['screens_per_question']['min']}-{A_W['screens_per_question']['max']} in the example-size bank; [measured: window.screens_per_question]); only the head stamp totals them. "
                  f"verify_after consistency: the read-back; nothing reports whether the pick is right. "
                  f"anchor fixed-position [measured: primary_action.Save and next]: over {sn['states']} states of the pass (no verdict, ticked, many ticked with warnings, scrolled to the end, half point, saved, changed) its right and bottom edges move {sn['edge_move_px']} px; it sits {sn['distance_to_right_edge_px']} px from the right edge and {sn['distance_to_bottom_edge_px']} px from the bottom; it is the same place as Next pair in the queue (edges equal, {PA['queue_next_pair_vs_pair_save_and_next']['width_delta_px']} px wider). "
                  f"Neighbour: Save, {PA['gap_between_save_and_save_and_next_px']} px to its left ({PA['tap_target_px']['Save'][0]}x{PA['tap_target_px']['Save'][1]} px against {PA['tap_target_px']['Save and next'][0]}x{PA['tap_target_px']['Save and next'][1]}), label×shape similarity {PA['save_vs_save_and_next_similarity']} ([measured: primary_action.save_vs_save_and_next_similarity]). Its red fill is shared with the bar's Update Canvas ([measured: primary_action.buttons_with_the_same_fill_on_a_pair]). "
                  f"Not in this chain: None (a part not attempted), a half point and a note. [measured: view_stability.none_tap] {none_text}; P5 in the registration is the event for it. A half point alone, even one the row's limits hid (+½ at full marks), is recorded and exported as one signed deduction on the whole question ({c('halfPointSigned')}). single_path: not declared (Next pair and Save and next both open the next pair, but only one records) [carried: unstated].",
                  anchor="fixed-position", confusables=[1, PA["save_vs_save_and_next_similarity"]], reversibility="reversible", preview_before=True, everything_on_screen=False,
                  verify_after="consistency", feedback="immediate", intent="record-pick", view="pair")

    def pair_steps(times_parts=parts_per_pair, with_wait=True, taps=3):
        out = []
        if with_wait:
            out.append(s_wait_load())
        out += [s_read_header(), s_scan_work()] + pair_body(times_parts) + [s_tap(taps), s_commit()]
        return out

    # ---- the chains ---------------------------------------------------------------------------------------------------------------------
    install = [
        st("READ", "the coordinating session's message in the chat: the data script is ready, which file, what it holds",
           f"{c('rbMakeFile')} the coordinating session makes the file first; {c('rbStderr')} the command prints, on stderr, a line with the sample's numbers (questions, pairs, students, bank items), and the runbook says they are an example. "
           "That the session passes the numbers on in its message, with the file's name and what it holds, is [guess]; so are the wording and length of the message, and amount 3. Produces the two items the later steps hold: the goal, and the numbers to compare with (the toast says its own numbers; a check needs something to check against).",
           reading="fine", amount=3),
        st("ANCHOR", "open the file's card in the chat",
           "HW1 A1 (stated): fixed position, one card among text, no look-alike ('无混淆项'); a wrong card costs one overwrite ('幂等'). That this session's file reaches the phone as a card like HW1's is [carried: unstated].",
           anchor="unique-visual"),
        st("ANCHOR", "the three dots, top right",
           "HW1 A2 (stated): fixed position, the screen's physical edge as the anchor, a shape unlike any text, no look-alike.", anchor="edge"),
        st("SCAN", "'Save to Files' in the menu, below the fold, among look-alike lines",
           "HW1 A3 (stated): the item needs a scroll and sits among look-alike text; a coarse read of the lines (O(m)) then a fine read of one (O(1)). Count 5 and similarity 0.8 are [carried: unstated] placeholders, the same as hw1-usual-save-cards step 3.",
           anchor="text-keyword", confusables=[5, 0.8]),
        st("READ", "the one item found: Save to Files", "HW1 A3 (stated): the O(1) fine read.", reading="fine", amount=1),
        st("VERIFY", "the destination folder on the save sheet",
           f"HW1 A4 (stated): the last folder is remembered, marginal cost 0 (need 0, no reading). The file must go to the Userscripts folder next to TapGrade ({c('rbFolder')}); whether the remembered folder is that one is [carried: unstated], and nothing on the save sheet says which folder is right [guess].",
           kind="consistency", need=0, reading="none"),
        st("ANCHOR", "Save, top right",
           "HW1 A5 (stated): fixed position, the screen's physical edge, one step. The save is idempotent (HW1 A1, '幂等').", anchor="edge"),
        st("NAVIGATE", f"back to Safari, the SpeedGrader tab of any HW2 student (a sampled student in about {in_pct}% of the cases, a student outside the sample in about {out_pct}%)",
           f"{c('rbOpen')} ('Open SpeedGrader for any HW2 student'). The shares are a guess from the docs' numbers: {class_basis}. HW1 E4 (stated): coming back to Safari the page stood as it was left (position). Goal and partial [carried: unstated]; no TapGrade partial work exists yet.",
           restores=["position", "goal", "partial"]),
        st("REFRESH", "reload the page so that the data script runs",
           f"Needed: the data script is a userscript that runs at document-start on a page load ({c('asUserscriptRunAt')}); TapGrade runs under the Userscripts app on an iPhone ({c('tgUserscripts')}), the file goes in its folder and is imported once ({c('tgImportOnce')}); it hands the file over in the entry tapgrade:sampleauto:<course>:<assignment>, not the machine's tapgrade:autoload:... ({c('asUserscriptStore')}; the body, {c('asUserscriptBody')}, acts only on the page of its own assignment). "
           f"A reload of a SpeedGrader address returns the same student ({c('readCtx')} readCtx), TapGrade's own state lives in localStorage, and nothing partial exists yet, so position, goal and partial are all there afterwards (nothing lost counts as restored). "
           f"HW1 B2 (the narrator's doubt whether a refresh took effect, and a second refresh) is an OUTCOME: it is not an input of this chain, it is a base rate in the registration (event I3). Whether the Userscripts extension needs more than a page load to pick up a new file is [carried: unstated]; nobody has tried this path on a phone ({c('tgLimitsPhone')}).",
           restores=["position", "goal", "partial"], feedback="immediate"),
        s_wait_load(f"On this first load after a new file the page imports it once ({c('autoloadFrom')}: the same file is never imported twice; {c('autoloadData')}: the sample's own entry is read first, and the machine's entry cannot replace it) and says so in a toast.",
                    target="the reloaded SpeedGrader page loads: Canvas first, then the sheet ('Student <id>', 'Loading the rubric from Canvas…', 'Pick a student in SpeedGrader…' until the submission arrives)"),
        st("READ", "the toast: 'Loaded the blind sample: 45 pairs on 9 questions.' (the numbers are the file's)",
           f"{c('importSampleToast')} the message (one short line); {c('flash')} flash: it leaves after 4200 ms by itself ({c('flashTimeout')}; [measured: first_contact.load_toast_seconds_on_screen] {FC['load_toast_seconds_on_screen']} s from when it was first seen). It floats above the sheet, out of the flow ({c('msgCss')}; {c('tgMessage')}); its element is still built in the sheet ({c('renderMsg')}), and its timer takes it away without rebuilding the sheet ({c('flashTimeout')}). [measured: window.pair_view_with_toast] on a pair the open body is {body_toast:.0f} px with it up and {body_h:.0f} px after (the cec1bba build: {CEC1BBA['window_with_message_large_px']} and {CEC1BBA['window_large_px']}), and it covers {W['pair_view_with_toast']['msg_over_page_px']:.0f} px of the page above the sheet. "
           f"Other signs that the sample loaded stay on the page: a note on a student outside the sample ({c('sampleTopNotice')}), 'Sample Q…' on a student inside it, a 'Blind sample' row under Files, Loaded ({c('sampleLoadedRows')}). "
           f"Two sentences that stay on the phone are for cases outside this chain: the browser would not keep the file ('No sample: the browser would not keep it.', {c('sampleNotices')}), and a machine data file for the same assignment refused while the sample is stored ({c('machineRefusedBySample')}, an error message that waits for the next message, over the page, {c('tgErrorOver')}). "
           f"The runbook says to leave the machine's script out of the folder for a quiet pass ({c('rbFolder')}); the chain assumes that was done [guess], so neither sentence is expected here. The runbook's rule for a load that did not happen is three signs, and one missing means stop ({c('rbStop')}): no 'Loaded the blind sample' message on the first load ({c('rbStopLoad')}); no 'Blind: no machine proposals' under the header of a sampled pair ({c('rbStopPair')}); no 'A blind sample is loaded' as the first line of a student outside the sample ({c('rbStopOther')}). This step checks the first sign.",
           reading="fine", amount=1),
        st("VERIFY", "compare the toast's numbers with the numbers the chat gave",
           f"{c('rbStderr')} ('Expect ... the numbers are an example'); the kind (consistency) is [carried: unstated]. This is where the two held items are used.",
           kind="consistency"),
    ]

    queue = [
        st("READ", "the Grade view of a student outside the sample: 'A blind sample is loaded (45 of 45 pairs not recorded). This student is not in it, so this is normal grading: Save writes to Canvas.' and a button 'Open the sample queue'",
           f"{c('sampleTop')} the note and its button ({c('sampleTopNotice')}), put first in the body ({c('renderGradeTop')}: before the purpose line, which says 'Changes Canvas', {c('purposeLine')}). "
           f"[measured: first_contact.outside_sample.notice] the note is the first element of the open body (its index {OS['notice']['index_in_body']}, the purpose line's {OS['notice']['purpose_line_index']}; before the purpose line: {yn(OS['notice']['before_the_purpose_line'])}) and says that Save writes to Canvas (answer: {yn(OS['notice']['says_save_writes_to_canvas'])}). "
           "origin_stated false: the note does not say which file the sample came from; exclusions_stated true: it says this student is not in it [declared from code reading; a semantic judgment]. "
           f"Path chosen: a student outside the sample (about {out_pct}% of first pages: {class_basis}). A student inside the sample opens straight on a pair; the way from there to the queue is a button named 'Queue' at the end of its page ({c('queueButton')}), and the Grade view shows no Sample tab either ({c('subTabsElse')}, {c('sampleSubs')}: This student and Sample are drawn only inside the queue). "
           f"The runbook names both routes, and says the Sample tab is not in the Grade view and exists only inside the queue ({c('rbRoute')}): from a page outside the sample, 'Open the sample queue' then 'Next pair' (2 taps, no scroll; {c('rbRouteOutside')}); from a pair, scroll to the end, 'Queue' (the last row), then 'Next pair' (2 taps and one long scroll; {c('rbRouteSampled')}). docs/TAPGRADE.md has the same two routes ({c('tgRoute')}). This chain is the first route. The first line of this page is also the runbook's third stop sign: without it the phone is not in the blind pass ({c('rbStopOther')}). "
           f"[measured: first_contact.outside_sample] on this page the normal foot is there too: Save and next is there (measured: {yn(OS['save_and_next_present'])}) and disabled (measured: {yn(OS['save_and_next_disabled'])}) until 'Mark rest full' is tapped ({c('footMarkRest')}). Save writes to Canvas, but while a sample is loaded it asks once first ({c('saveAsks')} in {c('save')} save; {c('sampleSaveAsk')}): "
           f"[measured: first_contact.outside_sample.tap_save_and_next] after Mark rest full, Save and next asks (answer: {yn(SV['asks_first'])}), the question names the blind pass ({yn(SV['names_the_blind_pass'])}) and says it writes to Canvas ({yn(SV['says_it_writes_to_canvas'])}); Cancel sends {SV['writes_after_cancel']} requests that write, OK sends {SV['writes_after_ok']}.",
           reading="fine", amount=1, origin_stated=False, exclusions_stated=True),
        st("SCAN", "the open part of the sheet for the button 'Open the sample queue'",
           f"[measured: first_contact.outside_sample] the button is {int(100 * OS['hint_button_visible_fraction_with_toast'])}% inside the open body while the load message is up and {int(100 * OS['hint_button_visible_fraction_without_toast'])}% after it has gone: the message floats above the sheet ({c('msgCss')}), so it neither covers nor pushes the button. A sampled student's pair has the same way to the queue, a button named 'Queue' at the end of its list ({c('queueButton')}): [measured: window.queue_button_from_pair] {W['queue_button_from_pair']['screens_down']} screens down (its offset from the top of the list, in heights of the open body; {A_W['queue_button_from_pair']['screens_down']} in the example-size bank). Three names for one view (the button 'Open the sample queue', the button 'Queue', the tab 'Sample'); the runbook names the first two and says the tab exists only inside the queue ({c('rbRoute')}, {c('rbRouteOutside')}, {c('rbRouteSampled')}). "
           "Amount 2 [guess]: the toast, then the note with its button; look-alikes none declared [carried: unstated].",
           anchor="text-keyword", amount=2),
        st("TAP", "Open the sample queue",
           f"{c('enterView')} enterView renders at once; [measured: feedback_ms.check_on_the_bar] {FB['check_on_the_bar']['ms']} ms for the same mechanism (a bar tap).", feedback="immediate"),
        st("READ", "the queue: one line per question ('Q1 0 of 5 recorded') and the sentence under them",
           f"{c('renderSampleQueue')} renderSampleQueue, {c('sampleLines')} sampleLines, {c('sampleLeftText')} sampleLeftText. [measured: primary_action.queue_sheet] all nine lines and the sentence fit on the sheet without scrolling (measured: {yn(PA['queue_sheet']['fits_without_scrolling'])}; the sheet is taller here, {PA['queue_sheet']['sheet_h']:.0f} px, {c('sheetTall')} .tall). "
           f"The tab strip here is This student | Sample: the Bank tab is closed while a sample is loaded ({c('sampleSubs')}, {c('enterViewBank')}). "
           f"origin_stated false: no file name, date or homework on this view (they are under Files, Loaded, {c('sampleLoadedRows')}) [declared from code reading]; exclusions_stated true: 'N of 45 pairs are not recorded yet.' Amount 10 (nine lines and the sentence) read coarsely.",
           reading="coarse", amount=10, origin_stated=False, exclusions_stated=True),
        st("ANCHOR", "Next pair, the red button at the bottom right of the foot ('Next: Q1, pair 1 of 5' beside it)",
           f"{c('sampleQueueFoot')} sampleQueueFoot. [measured: primary_action.Next pair] edges move {npair['edge_move_px']} px over {npair['states']} states of the pass; {npair['distance_to_right_edge_px']} px from the right edge, {npair['distance_to_bottom_edge_px']} px from the bottom; the same right and bottom edge as Save and next on a pair, {PA['queue_next_pair_vs_pair_save_and_next']['width_delta_px']} px narrower, inside it. Its red fill is shared with the bar's Update Canvas ([measured: primary_action.buttons_with_the_same_fill_in_the_queue]), so not unique-visual. The bar below has four labels no two alike ([measured: primary_action.bar_buttons.largest_label_x_shape_similarity] {PA['bar_buttons']['largest_label_x_shape_similarity']}).",
           anchor="fixed-position"),
        st("TAP", "Next pair",
           f"{c('sampleOpen')} sampleOpen: a toast 'Opening Q1, pair 1 of 5.' and, 350 ms later ({c('go')}), the page is replaced. The load is the first step of the pair chain.", feedback="immediate"),
    ]

    export = [
        st("ANCHOR", "Check, the right-most button of the bar",
           f"[measured: primary_action.bar_buttons] {PA['bar_buttons']['distance_to_bottom_edge_px']} px from the bottom edge and {PA['bar_buttons']['distance_to_right_edge_px']} px from the right (the safe-area inset is 0 px in this browser; {c('sheetPad')} pads the sheet by it, so on an iPhone the bar sits higher by the inset: not measured); four labels, the largest pair similarity {PA['bar_buttons']['largest_label_x_shape_similarity']}; {c('groups')} the four groups, in fixed places.",
           anchor="edge"),
        st("SCAN", "the five tabs of Check for 'Sample picks'",
           f"Check opens on the tab last used, Review by default ([measured: export.check_opens_on_a_tab_other_than_sample_picks] answer: {yn(EX['check_opens_on_a_tab_other_than_sample_picks'])}; {c('pane')}, {c('viewGroup')}, {c('sampleSubsCheck')}); Sample picks is the fifth. [measured: export.check_sub_tabs] all five fit without scrolling (answer: {yn(EX['check_sub_tabs']['all_fit_without_scrolling'])}), in {EX['check_sub_tabs']['font_px']} px type; the largest label×shape similarity among the five is {EX['check_sub_tabs']['largest_label_x_shape_similarity']} (label alone {EX['check_sub_tabs']['largest_label_similarity_alone']}; the line the checker draws is 0.5). Amount 5 is the tabs. "
           f"The view Check opens on starts a read-only scan of the class on arrival ({c('scanReview')}, GET only: 'Reading the class from Canvas…') and leaves the students of the blind sample out of what it compares ({c('renderReviewSkip')}; {c('reviewLeftOut')}); neither blocks a tap on Sample picks.",
           anchor="text-keyword", confusables=[4, EX["check_sub_tabs"]["largest_label_x_shape_similarity"]], amount=5),
        st("TAP", "Sample picks", f"[measured: feedback_ms.sample_picks_tab] {FB['sample_picks_tab']['ms']} ms to the first change.", feedback="immediate"),
        st("READ", "the view: one line per question, and while pairs are missing 'N of 45 pairs are not recorded; reconcile will call the sample incomplete.'",
           f"{c('renderSamplePicks')} renderSamplePicks; {c('sampleLeftText')} the warning; {c('samplepicksPurpose')} the purpose line ('Your recorded blind picks, as the file the kit reads. Nothing is sent to Canvas.'). origin_stated true (the purpose line says what these are); exclusions_stated true (the warning says what is missing; when all are recorded the line says so) [declared from code reading]. [measured: export.missing_pairs_warning_shown] the warning shows while pairs are missing (answer: {yn(EX['missing_pairs_warning_shown'])}). Amount 10 read coarsely.",
           reading="coarse", amount=10, origin_stated=True, exclusions_stated=True),
        st("SCAN", "the open part of the sheet for 'Copy as JSON' (below the nine lines)",
           f"[measured: export.sample_picks_view] this view has no foot: Copy as JSON is in the body, {EX['sample_picks_view']['copy_as_json_below_the_open_body_px']} px below the open part ({EX['sample_picks_view']['body_h']} px open of {EX['sample_picks_view']['scroll_h']} px), so it is not at a fixed place and needs a scroll ({c('copyButtons')}). Its red fill is shared with the bar's Update Canvas ([measured: export.buttons_with_the_same_fill_as_copy_as_json]: {' and '.join(x.rstrip('0123456789') for x in EX['buttons_with_the_same_fill_as_copy_as_json'])}); 'Download' beside it, label×shape similarity {EX['copy_as_json_vs_download_similarity']} ([measured: export.copy_as_json_vs_download_similarity]). Amount 3 [guess].",
           anchor="text-keyword", confusables=[1, EX["copy_as_json_vs_download_similarity"]], amount=3),
        st("COMMIT", "Copy as JSON",
           f"{c('copyButton')}: copy({{the speedkit-picks/1 file}}); {c('copy')} copy: if the browser refuses the clipboard the page says 'Copy blocked here. The text is selected below; use Copy from the menu.' (an event in the registration: nobody has tried it on an iPhone, {c('tgLimitsPhone')}). "
           f"reversibility idempotent: a copy changes nothing ({c('tgFlow10')}, 'The flow, as a chain' row 10: yes, a copy changes nothing). preview_before false (the file's text is not shown; it is not required of an idempotent commit); everything_on_screen true: the counts and the warning sit directly above the button; verify_after consistency: the toast repeats the count and the missing-pairs warning ([measured: export.copy_as_json] the toast says copied: {yn(EX['copy_as_json']['toast_says_copied'])}, copy blocked: {yn(EX['copy_as_json']['toast_says_copy_blocked'])}, warning repeated: {yn(EX['copy_as_json']['toast_mentions_missing_pairs'])}; the copy holds {EX['copy_as_json']['picks']} picks in {EX['copy_as_json']['chars']} characters and {EX['copy_as_json']['lines']} lines). "
           f"A pair whose only pick is a half point, even one the row's limits hid (+½ at full marks), is in the copy as one signed deduction on the whole question, not as 'No deductions' ({c('halfPointSigned')}). "
           f"[measured: export.complete_export_estimate] a complete export is about {EX['complete_export_estimate']['chars']:,} characters in about {EX['complete_export_estimate']['lines']} lines (estimated from the {EX['copy_as_json']['picks']}-pick copy).",
           anchor="text-keyword", reversibility="idempotent", preview_before=False, everything_on_screen=True, verify_after="consistency", feedback="immediate"),
        st("VERIFY", "the toast: 'Copied 45 picks as JSON.' and, if pairs are missing, the warning again",
           f"{c('copyButton')}; {c('flashTimeout')} it stays 4200 ms. kind consistency (the count against the 45 the queue says). [measured: view_stability.refusal_toast / view_stability.load_toast] a message floats above the sheet ({c('msgCss')}): the load message is {W['pair_view_with_toast']['msg_h']:.0f} px high and the refusal message {VS['refusal_toast']['height_px']:.0f} px, and neither takes room from the sheet or moves what is under it ({VS['load_toast']['content_moves_when_it_goes_px']:.0f} px when the first goes, {VS['refusal_toast']['content_moves_when_it_comes_px']:.0f} px when the second comes; the cec1bba build moved it {CEC1BBA['message_shift_px']:.0f} px). An error message stays until the next message, now over the page ({c('tgErrorOver')}).",
           kind="consistency"),
    ]

    handback = [
        st("NAVIGATE", "to the chat app (the JSON is on the clipboard)",
           "Off TapGrade. HW1 E3 (stated): 'open the chat app, find the conversation, locate the line' is how the narrator reached a chat; HW1 E4 (stated): the Safari page stood as it was left when the narrator came back. What the chat app shows on arrival is [carried: unstated]; restores position/goal/partial are [carried: unstated].",
           restores=["position", "goal", "partial"]),
        st("RE-ORIENT", "find the coordinating session's conversation and the place to answer",
           "HW1 E3 (stated, another purpose): finding the conversation and the line; amount 5 [guess]. The number of conversations and how alike their titles are is [carried: unstated].",
           reading="coarse", amount=5),
        st("ANCHOR", "the message box at the bottom of the chat",
           "Off TapGrade, nothing stated in HW1 [guess]: fixed place at the bottom edge.", anchor="edge"),
        st("SCAN", "the menu that opens on a long press for 'Paste'",
           "Off TapGrade [guess]: the iOS menu has a few items; amount 4; look-alikes none declared [carried: unstated].", anchor="text-keyword", amount=4),
        st("VERIFY", f"the box now holds the pasted text (about {EX['complete_export_estimate']['chars']:,} characters in about {EX['complete_export_estimate']['lines']} lines)",
           f"[measured: export.complete_export_estimate] the size of a complete export, estimated from the copy of {EX['copy_as_json']['picks']} picks ({EX['copy_as_json']['chars']} characters, {EX['copy_as_json']['lines']} lines) scaled to 45 picks, in an invented sample. Off TapGrade [guess]: whether the app shows it in full, shortens it or turns it into an attachment is [carried: unstated]; the kind is consistency [carried: unstated].",
           kind="consistency"),
        st("COMMIT", "Send",
           "Off TapGrade. A sent message cannot be unsent: irreversible [guess]. preview_before true (the box shows the text or an attachment); everything_on_screen false: hundreds of lines cannot all be on screen [guess]; verify_after none: the chat app shows 'sent', not whether the file is whole or valid (the coordinating session's reply says that, later: not part of this chain, waiting for a person).",
           anchor="edge", reversibility="irreversible", preview_before=True, everything_on_screen=False, verify_after="none", feedback="immediate"),
    ]

    pair = {"id": PAIR_ID,
            "task": "One sampled pair on a new student's page, nothing goes wrong: from the tap on Save and next (or on Next pair) to the next Save and next. The pass is 45 of these.",
            "setup": "The sample is loaded; the student is in it; the owner reads the work above the sheet and the key and chips in it.",
            "notes": "How the 45 repeats are counted. This chain is ONE pair. `times` is used only for what repeats inside a pair: the per-part body (4 parts) and the chip taps (3). It is not used for the 45 pairs, because the 45 are not copies: parts, chips and keys differ per pair, and the interrupted pairs (the next two chains) are different chains. "
                     "The pass's load is about 45 times this chain's load, plus the extra each interrupted pair adds (compare the three pair chains); the registration ranks the load of ONE instance of each segment. Memory items are listed in the registration's dataflow table; `held` is derived from it (an item is held from the step after it is produced to the step that last needs it).",
            "steps": pair_steps()}

    reload_steps = [s_wait_load(), s_read_header(), s_scan_work()] + pair_body(2) + [s_tap(2)]
    reload_steps += [
        st("REFRESH", "the page reloads in the middle of the pair (a refresh when something seems stuck, or Safari discarding the page while the phone was locked or another app was in front)",
           f"[measured: interruption.reload_with_a_half_picked_pair] with {IN['reload_with_a_half_picked_pair']['ticked_before']} chip ticked and a note typed before the reload, {IN['reload_with_a_half_picked_pair']['ticked_after']} are ticked after it and the note is {'kept' if IN['reload_with_a_half_picked_pair']['note_kept'] else 'gone'}; the foot says 'Pick a deduction, or No deductions.' (answer: {yn(IN['reload_with_a_half_picked_pair']['foot_says_nothing_is_picked'])}); the same pair comes back (answer: {yn(IN['reload_with_a_half_picked_pair']['same_pair_shown_again'])}; the student's first open row, {c('sampleFocus')} sampleFocus). "
           f"[measured: interruption.reload_with_the_queue_open / interruption.reload_with_the_export_open] the view is not stored: a reload with the queue open, or with Sample picks open, lands on the pair (answers: pair {yn(IN['reload_with_the_queue_open']['head_is_a_pair'])}, queue still open {yn(IN['reload_with_the_queue_open']['queue_open'])}; pair {yn(IN['reload_with_the_export_open']['head_is_a_pair'])}, export still open {yn(IN['reload_with_the_export_open']['export_open'])}). "
           f"By design: {c('rulesHalfPicked')} 'A pair left half-picked is not kept', {c('sampleDraft')} the draft is memory only. restores position and goal (the header names the pair) but not partial. Recorded pairs and the queue survive ([measured: interruption.reload_after_a_save] pair comes back recorded: {yn(IN['reload_after_a_save']['pair_comes_back_recorded'])}). "
           "Whether and how often a reload happens is the registration's event R1 (HW1 had refreshes at E6, G3 and H on 2026-10-03: a base rate, not an input).",
           restores=["position", "goal"], feedback="immediate"),
        s_wait_load(),
        st("RE-ORIENT", "which pair is this, what was done, where was I in the work and in the list",
           "HW1 G4 (stated): after a refresh the narrator re-found the place by reading the chips again one by one, the unrelated groups first. Amount 6 [guess]. The ticks that would answer 'what did I already pick' are gone, so this is a re-read of the work, not of the sheet.",
           reading="coarse", amount=6),
        s_scan_work(),
    ] + pair_body(4) + [s_tap(3), s_commit()]

    reload_chain = {"id": RELOAD_ID,
                    "task": "The same pair, but the page reloads after two of its four parts are picked: the picks are gone and the pair is done again from the work",
                    "setup": "One reload per pair at the half-way point [guess]; the owner redoes all four parts.",
                    "notes": "Compare with tapgrade-0.6.7-sample-pair: the same last four steps, plus the first half-pair that was lost, the reload, a second page load and a RE-ORIENT.",
                    "steps": reload_steps}

    lock_steps = [
        st("NAVIGATE", "unlock the phone and come back to the SpeedGrader tab, still on the pair that was open when the phone locked (between pairs)",
           f"[measured: interruption.app_switch_without_reload] with the page told it was hidden and shown again, the chips ticked before are still ticked (answer: {yn(IN['app_switch_without_reload']['draft_kept'])}). "
           f"Three lifecycle handlers: {c('pagehide')} and {c('pageshow')} concern an update that is running (pageshow also reads the picks again when the page comes back from the back/forward cache), and {c('visibilitychange')} reads the picks from the phone again when the page is shown ({c('sampleRefresh')}): a draft nobody touched is drawn again from what the phone holds, one that was typed in stays. "
           f"[measured: two_pages.return_to_a_stale_page] a page put away while another page recorded a pair shows the new count when it is shown again, with no reload (the queue line '{rts['queue_line_for_the_pair_the_other_page_recorded']['before']}' becomes '{rts['queue_line_for_the_pair_the_other_page_recorded']['after']}'; with no reload: {yn(rts['sees_it_without_a_reload'])}). "
           "HW1 E4 (stated): the page stood as it was left. A page that Safari discarded while locked reloads instead: that is the previous chain. Whether Canvas asks for a new login after a long lock is [carried: unstated] (HW1 E5 states a worry about it). Face ID or passcode is not modelled.",
           restores=["position", "goal", "partial"]),
        st("RE-ORIENT", "what was I doing: which pair, which student's work, where in it",
           "HW1 G4 (stated, after a refresh): the narrator rebuilt 'where was I' by reading again. Amount 4 [guess]; smaller than after a reload because nothing was lost and the header names the pair.",
           reading="coarse", amount=4),
    ] + pair_steps(with_wait=False)
    lock_chain = {"id": LOCK_ID,
                  "task": "The first pair after the phone locked between two pairs: the page is where it was; the owner has to find the thread again",
                  "setup": "The lock itself (minutes to hours) is not part of the chain and not part of its duration.",
                  "notes": "Compare with tapgrade-0.6.7-sample-pair: the same steps minus the page load, plus the unlock and a RE-ORIENT.",
                  "steps": lock_steps}

    short = sk["commit"][:7]
    doc = {
        "format": "emu-chain/1",
        "budget": 3,
        "provenance": {
            "source": "designed", "date": inputs["drafted"][:10],
            "who": f"worker E5 (a coding-agent session), from the code and docs of the TapGrade snapshot (speeds-kit commit {sk['commit']}, userscripts/tapgrade.user.js sha256 {scr['sha256']}, {scr['lines']} lines) and from docs/evidence/hw1-correction-2026-10-03/; nobody has used this flow on a phone",
            "note": "Written BEFORE the owner's HW2 blind sample pass, from the code and docs of the snapshot commit and from measurements on a mock Canvas in headless Chromium at 390x844 touch (checks/measure_sample_predictors.py, output docs/predictions/hw2-sample-pass.measured.json), not from anyone using it. Seven segments of the pass, one chain each so that each has its own load; the registration is docs/predictions/hw2-sample-pass.md. "
                    f"Evidence in every step's note: userscripts/tapgrade.user.js:LINES (lines of the snapshot, {short}; each is found by an anchor, listed with the text of its first line in docs/predictions/hw2-sample-pass.inputs.json, so that a new snapshot moves them by a rebuild and not by hand), docs (docs/TAPGRADE.md 'Blind sample mode' and docs/HW2-HW3-RUNBOOK.md steps 7-8, cited as docs/<file>.md:LINES and found by anchor like the code; the few lines cited from other sections are in the same table), HW1 <id> (an entry id of docs/evidence/hw1-correction-2026-10-03/transcription.jsonl), [measured: <key>] (a key of the measured JSON), [declared from code reading] (a judgment about what the screen says), [carried: unstated] (the checker's default, or a value nobody stated: P-02be), [guess]. "
                    "HW1's OUTCOMES (uncertainty about a refresh, a full memory, a lost goal) are never inputs of these chains (theory/RECORD-THEORY.md section 3): they are base rates in the registration. HW1's stated PROPERTIES of the save-from-chat steps (anchors, look-alikes, reading) are reused in tapgrade-0.6.7-sample-install steps 2-7, as hw1-usual-save-cards has them. "
                    f"Judgments that decide a finding: (1) the load WAIT says progress_visible false because the sheet's second loading state tells the owner to pick a student; (2) the pair's COMMIT says everything_on_screen false because the picks are spread over {W['screens_per_question']['min']:.0f}-{W['screens_per_question']['max']:.0f} screens ({A_W['screens_per_question']['min']:.0f}-{A_W['screens_per_question']['max']:.0f} with a bank of the runbook's example size) of a {body_h:.0f} px window, and reversible (not idempotent) with consistency as its only check, so colocation and commit_correctness fire on it; (3) the install REFRESH restores everything because nothing partial exists yet; (4) the reload chain's REFRESH loses partial work because the code drops a half-picked pair on purpose; (5) the queue and the export view are declared to say what they are (origin) only where the code's text does; (6) the chips' look-alike rule (count = round(mean visible) - 1, similarity = mean over parts of the largest pair) was fixed before the verifiers ran. Amounts (pages read, parts per pair, taps per pair) are guesses. "
                    f"BANK SIZE: the measured layout is for an INVENTED bank of {SMP['chips']} chips ({SMP['parts']} parts in {SMP['questions']} questions, {SMP['chips'] / SMP['questions']:.0f} chips per question), a stress sample. The runbook's example output says {EXAMPLE_ITEMS} bank items ({c('rbStderr')}): {EXAMPLE_ITEMS} chips in all, {EXAMPLE_ITEMS / EXAMPLE_QUESTIONS:.1f} per question; nothing says which size is nearer to HW2. docs/predictions/hw2-sample-pass.measured-example-bank.json is the same measurement with {ASMP['chips']} chips in {ASMP['parts']} parts: lists are {A_W['screens_per_question']['median']} screens instead of {screens_med}, a part's key is in view with one of its chips in {100 * A_KEY:.0f}% of the views instead of {100 * KEY:.0f}%, and the declarations here hold at both sizes. The events that depend on the size say so. "
                    f"IN THIS SNAPSHOT: the sample fixer's follow-up (Save for a student outside the sample asks once; Add deduction and Add credit item hidden and the shared bank page not pushed while a sample is loaded; Remove older summary comments asks with the blind-pass sentence; the runbook and docs/TAPGRADE.md naming the route to the queue as it is: {c('rbRoute')}, {c('tgRoute')}) and its third round (the list is put back where it was when the sheet is rebuilt, {c('tgKeepsPlace')}; a message floats above the sheet and takes no room, {c('tgMessage')}; the head names its pair whole and keeps its height, {c('tgHeadWhole')}; the stop rule is three signs, {c('rbStop')}) and its fourth round (a rebuild of a sampled pair draws its part tallies and warnings, so the restored position lands on the same chip, {c('tgTallies')}; the sheet's lowest height does not count the floating message, {c('tgFloor')}; the docs say which doors write during the pass, {c('tgWriteDoors')}). A further review round may change the code again: before this file is pushed a new snapshot is taken in by `python3 -m checks.hw2_sample_prediction rebuild` (docs/predictions/hw2-sample-pass.md says how); once it is pushed, a change is a NEW dated registration: do not edit this one."},
        "chains": [
            {"id": "tapgrade-0.6.7-sample-install",
             "task": "Install: from 'the data script is ready' in the chat to the first SpeedGrader load that says the sample loaded",
             "setup": f"The coordinating session has made hw2-sample.user.js (python3 -m speedkit.tapgrade_sample <hw> --userscript) and told the owner so (assumed: the runbook says only that the session makes the file first, {c('rbMakeFile')}). The file reaches the phone as HW1's chat files did (assumed), is saved into the Userscripts folder next to TapGrade ({c('rbFolder')}), and a SpeedGrader page of an HW2 student is reloaded.",
             "notes": "Waiting for the session's message, and any time the owner spends before first touching it, are not part of the segment. Two items are held from the first step to the last: the goal and the numbers the chat gave.",
             "steps": install},
            {"id": "tapgrade-0.6.7-sample-queue",
             "task": "Read the queue: from the first SpeedGrader page with the sample loaded to the tap on Next pair",
             "setup": f"The first page is a student outside the sample: the route the runbook gives for that page, 'Open the sample queue' then 'Next pair' ({c('rbRouteOutside')}). A first page inside the sample is a pair already: the owner may start on it, or take the longer route the runbook also gives (scroll to the end, 'Queue', 'Next pair'; {c('rbRouteSampled')}); this chain models neither (events Q2 and Q1).",
             "notes": f"One item is held: the plan the runbook gives for a page outside the sample ({c('rbRouteOutside')}): open the queue, then Next pair.",
             "steps": queue},
            pair, reload_chain, lock_chain,
            {"id": "tapgrade-0.6.7-sample-export",
             "task": "Export: Check, Sample picks, read the counts and the warning, Copy as JSON",
             "setup": "Done once, when the owner thinks the pass is over (or earlier, to try it: then the warning about missing pairs shows).",
             "notes": "One item is held: the goal.",
             "steps": export},
            {"id": "tapgrade-0.6.7-sample-handback",
             "task": "Hand-back: paste the copied JSON into the chat with the coordinating session and send it",
             "setup": "Off TapGrade. Waiting for the session's answer is not part of the segment.",
             "notes": "Almost everything here is carried or guessed: HW1 states only that the narrator switched apps and found a conversation.",
             "steps": handback},
        ],
    }

    # ---- the dataflow table: what is produced on one surface and needed on another (theory/RECORD-THEORY.md section 5) -------------------
    # held(step s) = the items produced before s and last needed at or after s; the chains' `held` lists are DERIVED from this table, never typed by hand.
    SH, WK, MIND = "TapGrade sheet", "the student's work (the Canvas page above the sheet)", "the person (the plan made earlier)"
    chip_flow = lambda a, b, d: [
        dict(item=W_ITEM, produced_at=a, produced_on=WK, needed_at=[a + 3], needed_on=SH + " (the chips)"),
        dict(item=K_ITEM, produced_at=b, produced_on=SH + " (the key)", needed_at=[b + 1], needed_on=SH + " (the chips)"),
        dict(item=C_ITEM, produced_at=b + 1, produced_on=SH + " (the chip list, scrolled)", needed_at=[d], needed_on=SH + " (the taps)")]
    dataflow = {
        "tapgrade-0.6.7-sample-install": [
            dict(item=G_INSTALL, produced_at=1, produced_on="the chat", needed_at=[12], needed_on="Safari (the SpeedGrader page)"),
            dict(item=X_NUMBERS, produced_at=1, produced_on="the chat", needed_at=[12], needed_on="Safari (the toast)")],
        "tapgrade-0.6.7-sample-queue": [
            dict(item=P_QUEUE, produced_at=1, produced_on=f"the first screen, with the runbook's plan ({c('rbRouteOutside')})", needed_at=[5], needed_on=SH)],
        PAIR_ID: chip_flow(4, 6, 8),
        RELOAD_ID: chip_flow(4, 6, 8) + chip_flow(13, 15, 17),
        LOCK_ID: chip_flow(5, 7, 9),
        "tapgrade-0.6.7-sample-export": [
            dict(item=G_EXPORT, produced_at=0, produced_on=MIND, needed_at=[7], needed_on=SH + " (the toast)")],
        "tapgrade-0.6.7-sample-handback": [
            dict(item=G_EXPORT, produced_at=0, produced_on=MIND, needed_at=[6], needed_on="the chat (Send)")],
    }
    for ch in doc["chains"]:
        flows = dataflow[ch["id"]]
        for i, stp in enumerate(ch["steps"], 1):
            stp["held"] = [d["item"] for d in flows if d["produced_at"] < i <= max(d["needed_at"])]
        for d in flows:                                  # the table must point at steps that exist
            assert 0 <= d["produced_at"] <= len(ch["steps"]) and all(1 <= n <= len(ch["steps"]) for n in d["needed_at"]), (ch["id"], d)
    return doc, dataflow
