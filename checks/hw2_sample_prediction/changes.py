"""What changed in TapGrade since an earlier set of numbers, and what each change moved.  Two comparisons are made:

  first_draft  the first draft, written against speeds-kit ca80695 and never registered or pushed (docs/predictions/first-draft-ca80695/)
  replaced     the registration this one supersedes, built against an earlier head of speeds-kit (docs/predictions/replaced-<commit>/; at most one folder)

Each baseline keeps its numbers as data: its two measured files, the declared properties of its fixture (no notes), a summary of its registration
(loads, findings, onsets, ranks, every event's p, and the commit that registered it when there was one) and, in new-keys.json, measurements that did not
exist when it was made, taken on its own script by the current measurement script.  `compute` compares each with this build and lists EVERY difference; a
difference that no entry of the comparison's CHANGES claims stops the build ("attribute this change"), and so does a claim that nothing moved where
something did.  So a section cannot leave out a number that moved and cannot be tuned afterwards.  The reasons (CHANGES, WHY) are hand-written and carry
no numbers: the numbers come from the two sides.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from pathlib import Path

from .cites import Cites

BASELINE_FILES = ("measured.json", "measured-example-bank.json", "declared.json", "summary.json", "new-keys.json")
BASELINE_DIR = "docs/predictions/first-draft-ca80695"
FIRST_DRAFT_COMMIT = "ca80695"

# measured keys that are timings of a run (they differ from run to run) or about the run itself: not a change of the artifact
NOISY = ("feedback_ms.", "loading.", "first_contact.load_toast_seconds_on_screen", "view_stability.load_toast.seconds_on_screen")

# Each entry: what TapGrade changed (the sample fixer's list, as told), which differences it explains (`moved`: patterns over the keys below), the places where it
# is claimed that NOTHING moved (`nothing_moved_in`: checked, so the claim cannot go stale), and what it did to the chains.
# The texts may hold {placeholders}: {this} is the snapshot's short commit, and every key of cites.ANCHORS is the line it cites ({rbRoute}: 'docs/HW2-HW3-RUNBOOK.md:146'),
# so a sentence about what the docs say carries the line it rests on and stops the build when the docs say something else.  A placeholder that names nothing stops it too.
# Keys: measured:<bank-independent path> | declared:<chain suffix>:<step>:<property> | number:<chain suffix>:<what> | event:<id>:<p|basis|kind|steps|added|removed>

# The sample fixer's third round (speeds-kit cec1bba to be4e324) and fourth round (be4e324 to 66eee2a).  The first-draft script and the cec1bba script behaved alike in each respect the third round's
# entries describe (the current measurement tool was run on both, and the values before are the same).  Where one number moved in both rounds the first-draft list has ONE entry for it
# (`pair-view-layout`) and says in each Why which round moved it; the list against the registration that was replaced holds the fourth round only.
UNMOVED_CHAINS = ["declared:install:*", "declared:pair*:*", "declared:export:*", "declared:handback:*", "number:install:*", "number:pair*:*", "number:export:*", "number:handback:*", "number:ranking:*"]
NO_CHAIN_MOVED = "no declared property, load or finding of the install, pair, reload, lock, export or hand-back chain moved"

MESSAGE_FLOATS = dict(
    id="message-floats",
    change="A message (the load message, a refusal, 'Recorded on this phone ...', an error) floats above the sheet instead of sitting in it: it takes no room from the open part, moves no chip when it comes or goes, lets a tap through to the page, and its timer takes it away without rebuilding the sheet; a long one is cut off at the room above the sheet",
    moved=["measured:view_stability.load_toast.*", "measured:view_stability.refusal_toast.*", "measured:view_stability.next_pair_message.*", "measured:view_stability.load_toast_leaves_with_the_list_scrolled.*",
           "measured:window.pair_view_with_toast.body_h", "measured:window.pair_view_with_toast.msg_over_page_px", "event:P4:p", "event:P14:added"],
    nothing_moved_in=["measured:view_stability.second_chip_in_a_part.*", "measured:view_stability.clamped_key_opened_by_a_tap.*", "measured:view_stability.load_toast.height_px", "measured:view_stability.refusal_toast.height_px",
                      "measured:window.pair_view_with_toast.msg_h", "measured:window.pair_view_with_toast.sheet_h", "measured:window.pair_view_with_toast.tabs_h", "measured:window.pair_view_with_toast.foot_h",
                      "measured:window.pair_view_with_toast.bar_h", *UNMOVED_CHAINS],
    effect="At {this} the message is out of the flow ({msgCss}; {tgMessage}): the content under it does not move when it comes or goes, and the open part of the sheet is the same with the message up as without it. "
           "Before, it sat in the sheet, took its height from the list while it showed, and moved every chip when it came and again when it went. The notes of the steps that wait for a message or read around it say so "
           "(the page load, the load message, the button under it, the export's message). One cost goes and one appears. A message can no longer push a chip from under the finger. It now covers the top of the student's work "
           "for the seconds it shows, so a new event, P14, predicts that. P4 loses its message part, and its p falls by judgment: the same author set the earlier value and has now seen the change; the value it had is in the table. "
           "Checked: the message's own height, the warning line that a second chip pushes down, the foot and the bar are as they were; " + NO_CHAIN_MOVED + ".")

LIST_KEEPS_ITS_PLACE = dict(
    id="list-keeps-its-place",
    change="A rebuild of the sheet puts the list back where it was when the view, the row and (in Grade) the student are the same, as the last step of the rebuild, and hiding the sheet remembers where the list was: a tap on None or on No deductions, hiding and opening the sheet, a resize drag and the bar's Grade button no longer throw the list to the top; another student or another row starts at the top; and (the fourth round) the rebuild draws a sampled pair's part tallies and warnings too, so with ticks in a part the list lands on the same chip",
    moved=["measured:view_stability.none_tap.scroll_after_px", "measured:view_stability.none_tap.jumps_to_the_top", "measured:view_stability.no_deductions_tap.scroll_after_px", "measured:view_stability.grade_button_on_a_pair.scroll_after_px",
           "measured:view_stability.hide_and_reopen_the_sheet.scroll_after_px", "measured:view_stability.resize_the_sheet_by_dragging_its_head.scroll_after_px",
           "measured:view_stability.rebuild_with_ticks.scroll_after_px", "measured:view_stability.rebuild_with_ticks.same_chip_shift_px", "measured:view_stability.rebuild_with_ticks.warnings_after_the_rebuild", "event:P5:p", "event:P5:kind"],
    nothing_moved_in=["measured:view_stability.chip_tap.the_chip_is_ticked", "measured:view_stability.hide_and_reopen_the_sheet.ticked_*",
                      "measured:view_stability.resize_the_sheet_by_dragging_its_head.ticked_after", "measured:view_stability.resize_the_sheet_by_dragging_its_head.sheet_h_*",
                      "measured:view_stability.rebuild_with_ticks.ticked_*", "measured:view_stability.rebuild_with_ticks.warnings_before", "measured:view_stability.rebuild_with_ticks.warnings_above_the_window_before",
                      "measured:view_stability.rebuild_with_ticks.stamp_bumps_right_after_the_rebuild", *UNMOVED_CHAINS],
    effect="{renderKeepScroll}; {tgKeepsPlace}. At {this} the list stays where the reader had it after each of those taps. Before, every one of them threw it to the top and the reader had to find the part again. "
           "The notes of the steps where the owner scrolls, hides or resizes the sheet say so. P5, the event that predicted the jump, loses its reason on the mock: its p falls by judgment (the same author, who has now seen the change), "
           "it becomes a prediction that nothing goes wrong, and it now tests whether the fix holds on a phone. "
           "The fourth round finished what the third began. The third round put the list back at the same pixels, but only a tap drew a pair's part tallies and warnings, so a rebuild blanked them and, with two ticks in a part, "
           "the same pixels showed another chip (the sample reviewer's S-1). At {this} the rebuild draws them ({renderTallies}; {tgTallies}) and the list lands on the same chip. "
           "The tool's new probe ticks two chips in a part and rebuilds (`view_stability.rebuild_with_ticks`): on the first draft's script the list goes to the top, and the table gives how far a chip far below the top of the window moved. "
           "Checked: the ticks stay, the sheet is as high after a resize as before, the stamp does not bump on a rebuild; " + NO_CHAIN_MOVED + ".")

PAIR_VIEW_LAYOUT = dict(
    id="pair-view-layout",
    change="The head of a pair names it whole at 390 px and keeps its height whatever the points (a stamp of four or more characters is set smaller, so the tag stays on one line and the title is not cut off), and (the fourth round) a rebuild draws a pair's part tallies, so each part heading holds its tally from the first render",
    moved=["measured:window.pair_view.*", "measured:window.pair_view_largest_sheet.*", "measured:window.pair_view_with_toast.head_h", "measured:window.part_headings_at_the_first_render.*", "measured:window.per_question.*",
           "measured:window.screens_per_question.*", "measured:window.queue_button_from_pair.*", "measured:chips.*", "measured:first_contact.pair_title_slack_px_one_pair_per_question.*", "measured:view_stability.chip_tap.*",
           "measured:view_stability.none_tap.scroll_before_px", "measured:view_stability.no_deductions_tap.scroll_before_px", "measured:view_stability.hide_and_reopen_the_sheet.scroll_before_px",
           "measured:view_stability.resize_the_sheet_by_dragging_its_head.scroll_before_px", "measured:view_stability.rebuild_with_ticks.scroll_before_px"],
    nothing_moved_in=["measured:window.pair_view.sheet_h", "measured:window.pair_view.tabs_h", "measured:window.pair_view.foot_h", "measured:window.pair_view.bar_h", "measured:window.pair_view.work_area_above_sheet_h",
                      "measured:window.pair_view_largest_sheet.work_area_above_sheet_h", "measured:window.first_screen_shows_a_chip", "measured:window.sticky_headers_off_at_this_height", "measured:chips.reason_labels.*", *UNMOVED_CHAINS],
    effect="{stampTier}; {scoreWide}; {tgHeadWhole}. At {this} the head is one height whatever the points. Before, a stamp of five characters made the tag wrap, the head grew a line, and every row under it moved by that growth; "
           "with a longer stamp the title was cut off. The open part of the sheet is taller by what the wrapped head took. That moves the numbers of the large invented bank, whose questions carry stamps long enough to wrap. "
           "In the example-size bank the window was already this tall, so only the large bank's window numbers are in the table; what moves in the example-size bank is a chip tap: the shift it measured before is the head growing as the points changed. "
           "The fourth round adds a smaller step the other way. A rebuild draws a pair's part tallies ({renderTallies}; {tgTallies}), so the parts say `full` from the first render, and a heading that holds a tally is taller than one that held none. "
           "Each part is longer by that, so each list is longer, the Queue button is further down it, and the first tap in a part no longer grows a heading under the finger: a chip tap moves nothing now, in either bank. "
           "The step shows in both banks; the Why column says, for each number, which round moved it. "
           "A taller window shows more chips at once and makes each list a little shorter in screens. It does not remove the scrolling: no chip is on the first screen in either bank, and P2, which follows the rule at the top of events.py, "
           "keeps its p. " + NO_CHAIN_MOVED[0].upper() + NO_CHAIN_MOVED[1:] + ".")

# the fourth round, against the registration that was replaced (be4e324): what the fixer's S-1 changed, in one entry
TALLIES_ON_REBUILD = dict(
    id="tallies-on-rebuild",
    change="A rebuild of the sheet draws a sampled pair's part tallies and warnings, as a tap does, so the parts say `full` from the first render and the position put back lands on the same chip when parts have ticks (the sample reviewer's S-1); the stamp does not bump on a rebuild",
    moved=["measured:window.part_headings_at_the_first_render.*", "measured:view_stability.rebuild_with_ticks.*", "measured:window.per_question.*", "measured:window.screens_per_question.*", "measured:window.queue_button_from_pair.*", "measured:chips.*",
           "measured:view_stability.chip_tap.*", "measured:view_stability.none_tap.*", "measured:view_stability.hide_and_reopen_the_sheet.*", "measured:view_stability.resize_the_sheet_by_dragging_its_head.*",
           "measured:view_stability.load_toast_leaves_with_the_list_scrolled.*"],
    nothing_moved_in=["measured:window.pair_view.*", "measured:window.pair_view_largest_sheet.*", "measured:window.pair_view_with_toast.*", "measured:window.first_screen_shows_a_chip", "measured:window.sticky_headers_off_at_this_height",
                      "measured:window.tap_targets_on_a_pair.*", "measured:first_contact.pair_title_slack_px_one_pair_per_question.*", "measured:chips.reason_labels.*", "measured:view_stability.load_toast.*",
                      "measured:view_stability.refusal_toast.*", "measured:view_stability.next_pair_message.*", "measured:view_stability.second_chip_in_a_part.*", "measured:view_stability.clamped_key_opened_by_a_tap.*",
                      "measured:view_stability.no_deductions_tap.*", "measured:view_stability.grade_button_on_a_pair.*", "measured:view_stability.rebuild_with_ticks.stamp_bumps_right_after_the_rebuild",
                      "measured:view_stability.rebuild_with_ticks.ticked_*", "measured:view_stability.rebuild_with_ticks.warnings_before", "measured:view_stability.rebuild_with_ticks.warnings_above_the_window_before", *UNMOVED_CHAINS],
    effect="{renderTallies}; {tgTallies}. At {this} the list stays on the same chip after a rebuild when parts have ticks. Before, only a tap drew a pair's part tallies and warnings, so a rebuild blanked them: the list above the window was shorter "
           "by what was left undrawn, and the position the rebuild put back showed another chip (the sample reviewer's S-1). The registration for be4e324 did not see it, because its probes never ticked a chip before a rebuild; "
           "this one's tool does (`view_stability.rebuild_with_ticks`, measured on this script and, with the same tool, on the script of that registration, whose folder holds those numbers in new-keys.json). "
           "Two small things follow. A heading that holds a tally is taller than one that held none, and the parts hold theirs from the first render, so every part is longer, each list is longer by the sum, and the Queue button is further down it "
           "(the docs name the same cause on the kit's own pages: {tgQueueFar}); the open part of the sheet did not change. And the first tap in a part no longer grows its heading, so a chip tap moves nothing under the finger. "
           "Those are the numbers that moved: the parts' headings, the length of each list and the screens it is, the Queue distance, the chips in view, and the positions where the tool puts a row. "
           "The stamp does not bump on a rebuild, before or after (the tool reads it). Checked: the window (the head, the open part, the strips of the sheet), the messages and the pair's first-contact numbers did not move; " + NO_CHAIN_MOVED + ".")

FLOOR_IGNORES_THE_MESSAGE = dict(
    id="floor-ignores-the-message",
    change="The sheet's lowest height no longer counts a message that floats above it: a sheet pulled down to its floor is not raised when a message comes and does not stay raised when it goes (SF2)",
    moved=["measured:view_stability.sheet_at_its_floor.*"],
    nothing_moved_in=["measured:view_stability.sheet_at_its_floor.stored_height_fraction", *UNMOVED_CHAINS],
    effect="{sheetFloor}; {tgFloor}. At {this} a message does not count in the lowest height the sheet may be dragged to. Before, a reader who had dragged the sheet to its floor saw it grow by the message's height while the load message showed "
           "(the first draft's script), and from the third round on it also stayed taller after the message had gone (the build for be4e324). That matters only to a reader who dragged the sheet to its floor: the pass starts at the default height, "
           "and nothing in the runbook asks for the floor. The tool's new probe pulls the sheet to its floor and shows the load message (`view_stability.sheet_at_its_floor`; the table gives the heights). "
           "No chain has a step that does this and no event rests on it, so the registration reports the number and moves nothing for it. " + NO_CHAIN_MOVED[0].upper() + NO_CHAIN_MOVED[1:] + ".")

UPDATE_VIEW = dict(
    id="update-view",
    change="Two things at the end of an update: a sheet that was hidden while an update ended opens at the report, and the Update foot's button says `Checking…` while the students are read back (SF1 and the foot's label)",
    moved=[], nothing_moved_in=["measured:primary_action.*", "measured:interruption.*", *UNMOVED_CHAINS],
    effect="{reportTopEnd}; {reportTopFail}; {footChecking}; {tgHideEnd}; {tgFootWord}. Both are in Update Canvas, which the owner is told not to use during the pass ({rbNoUpdate}). "
           "Nothing on the path of a sampled pair moved, and no measured number: the tool does not run an update. If one is run by mistake, the report is at the top and the button says what it is doing.")

DOCS_FOURTH_ROUND = dict(
    id="docs-fourth-round",
    change="The runbook and docs/TAPGRADE.md say what is true about writing during the pass (Save and Save and next on a sampled pair write nothing; three other doors can write, and a fourth, Set up rubric from a file, is offered only when Canvas holds no rubric; each asks once first), "
           "give the limits below 390 px, for a late data script and in landscape, and count the fourth round's checks; the runbook's step 10 says what to do on the phone before the bulk pass",
    moved=[], nothing_moved_in=["declared:install:*", "number:install:*", "declared:export:*", "number:export:*", "declared:handback:*", "number:handback:*", "event:I*"],
    effect="The docs say it ({tgWriteDoors}; {rbWriteRow}). The docs name four doors: the first three are counted in the same sentence, the fourth follows it, and the sentence that names the fourth, in the runbook's decision row and in the docs' paragraph, was added by a docs-only commit after `66eee2a` (the head of the fourth round). "
           "P11, the event about a stray write, rests on the measured question and on this, and its p does not change: the fourth door, which creates a rubric on Canvas, is offered only when Canvas holds none, and this registration did not try it with a sample loaded (the docs say so too). "
           "The three limits are now written down, and they are the reviewers' and the kit author's numbers, not this tool's, which does not measure them: narrower than 390 px the head is cut ({tgNarrower}); "
           "in landscape the Grade view's bar is below the screen ({tgLandscape}); a data script that fires late moves the list, because the position put back is of pixels, not of a place ({tgLateScript}). "
           "This registration measures at 390 by 844 in portrait and says so in its limits. "
           "The runbook's step 10 now tells the owner what to do on the phone before the bulk pass ({rbBulkOnPhone}): copy the picks and keep them as `sample/picks.json`, then clear the sample data, which asks first when picks are recorded and changes nothing on Canvas. "
           "That is after the pass and on no chain of this registration. Nothing measured moved and no declared property: the owner reads the same pages in the same order as before.")

NOT_ON_THE_PATH_THIRD_ROUND = dict(
    id="not-on-the-path-third-round",
    change="Everything else in the third round (cec1bba to be4e324): the new checks of the kit's audit and their twins that test the checks (they test the kit, not the owner's phone), the build stamp, a comment in the script about the way to the queue, the counts and the changelog in the docs",
    moved=[], nothing_moved_in=["number:handback:*", "number:ranking:*"],
    effect="Not on the path of a sampled pair.")

NOT_ON_THE_PATH_FOURTH_ROUND = dict(
    id="not-on-the-path-fourth-round",
    change="Everything else in the fourth round (be4e324 to {this}): the audit's new checks (they test the kit, not the owner's phone; S-2 is a check that a guard in Accept & next, which already held, holds), the build stamp, the counts and the changelog in the docs",
    moved=[], nothing_moved_in=["number:handback:*", "number:ranking:*"],
    effect="Not on the path of a sampled pair.")

WHAT_DID_NOT_MOVE = dict(
    id="what-did-not-move",
    change="Everything the be4e324 registration rests on that the fourth round did not touch",
    moved=[], nothing_moved_in=["declared:*", "number:*", "measured:export.*", "measured:primary_action.*", "measured:interruption.*", "measured:two_pages.*", "measured:first_contact.*", "event:*"],
    effect="Stated so that a reader need not look: no declared property of any chain moved, no load, peak, finding, rank, tie or onset moved, and the five friction events with the highest p are the same five. "
           "No event changed. P1, P2 and P8 follow the rule at the top of events.py from numbers that moved a little (the key out of view in the large bank, the screens per question), and the rule gives the p they had; "
           "the table in section 4d says so for each. P4 and P5 keep theirs: a rebuild that landed off the chip (S-1) was real on the build for be4e324 and was in neither p, and it is gone at {this}, so nothing is lowered for it. "
           "No measured number of the export, the buttons, the interruptions, the two pages, the messages, the window or the first page outside the sample moved (timings aside).")

CHANGES = [
    dict(id="schema-and-key", change="The sample's data file has its own schema (tapgrade-blind-sample/1) and its own storage key (tapgrade:sampleauto:...); a machine data file and the sample never replace each other; the refusal sentence stays on the phone (head, top of Grade, Files > Loaded); the load toast is one short line",
         moved=["measured:sample.file"], nothing_moved_in=["measured:window.pair_view_with_toast.msg_h", "declared:install:*", "number:install:*"],
         effect="The install notes cite the new lines and say which entry the data script writes. Nothing else moved: the toast's text and its own height are the same as in the first draft (what it takes from the sheet is the third round's, below), and the chains assume the machine's data script is out of the folder, as the runbook advises for a quiet pass ({rbFolder}), so the refusal sentences are not on a chain."),
    dict(id="bank-closed", change="The Bank is closed while a sample is loaded (the strip is This student | Sample; no Bank tab, no 'Edit the bank', no 'Add deduction' or 'Add credit item'), and the shared bank page is not pushed",
         moved=[], nothing_moved_in=["measured:primary_action.queue_sheet.*"],
         effect="The queue's note says so. Nothing moved: the queue view fits the sheet as before, and no chain used the Bank."),
    dict(id="asks-before-writing", change="What can still write asks once, naming the blind pass, while a sample is loaded: Update Canvas (Apply, Resume, Retry failed), Remove older summary comments (and Retry failed removals), and Save and next or Accept & next for a student outside the sample",
         moved=["measured:first_contact.outside_sample.tap_save_and_next.*", "event:P11:*"], nothing_moved_in=["measured:first_contact.outside_sample.save_and_next_*"],
         effect="The one tap of the pass that could reach Canvas by mistake, Save and next on a page outside the sample, is measured on both scripts: the first draft's wrote at the first tap and asked nothing; this one asks, names the blind pass and Canvas, and sends nothing on Cancel. P11 falls, and this registration backs it with that measurement. The other asks are on no chain: the owner is told not to use Update Canvas ({rbNoUpdate}), and a tap on the bar's red button only reads."),
    dict(id="review-clear-export", change="Check > Review leaves the sample out; a pick whose deduction value changed is stale; Clear sample data leaves nothing behind; a half point alone is exported as a signed question-level deduction",
         moved=[], nothing_moved_in=["measured:export.*", "declared:export:*", "number:export:*"],
         effect="The export notes cite them. Nothing moved: the copy holds the same picks, characters and lines, and Sample picks is still the fifth tab."),
    dict(id="merge-and-reload", change="Picks are merged from storage at save time (a stale page cannot erase another page's pick) and read again when a page comes back (pageshow, visibilitychange); a note typed on a student outside the sample is kept when another tab changes the sample",
         moved=["measured:two_pages.*", "event:P13:added"], nothing_moved_in=["declared:pair*:*", "number:pair*:*", "measured:interruption.*"],
         effect="One new measured predictor and one new event. The lock chain's note, which said there was no visibilitychange handler, is rewritten, and the pair chain's save note cites the merge. No declared property or load moved."),
    dict(id="first-line-note", change="A student outside the sample gets a first-line note (above the purpose line) that says Save writes to Canvas, with an 'Open the sample queue' button",
         moved=["measured:first_contact.outside_sample.hint_*", "measured:first_contact.outside_sample.notice.*", "declared:queue:2:amount", "number:queue:*", "event:Q5:p"], nothing_moved_in=[],
         effect="The button is in view with the load message up (it was cut off in the first draft), the note comes before 'Changes Canvas', and the owner has less to read before the button. The queue's SCAN amount, and so the queue's load, go down; the order of the segments does not change. The foot of such a student is as it was: Save and next present, disabled until Mark rest full."),
    dict(id="route-in-the-docs", change="The runbook and docs/TAPGRADE.md were corrected to give the way to the first pair as it is: 2 taps from a page outside the sample (Open the sample queue, then Next pair); from a pair, Queue is the last row of a long page, then Next pair; the Sample tab is not in the Grade view and exists only inside the queue",
         moved=["event:Q1:p"], nothing_moved_in=[],
         effect="At ca80695 the runbook said \"The pass: Grade, then the Sample tab, then Next pair\", and the Grade view has no such tab. At {this} the runbook gives the route ({rbRoute}; {rbRouteOutside}; {rbRouteSampled}) and so does docs/TAPGRADE.md ({tgRoute}), "
                "so the owner is told where to look and the chance of trouble finding the queue falls. Q1 and the queue notes cite the docs as they are at {this}. This change is in the docs: no declared property or load moved because of it."),
    dict(id="not-on-the-path", change="Everything else in the diff of the script up to cec1bba (Update Canvas's grade arithmetic, a Grade row with a comment and no points opening undecided, the Files line about the bank, the build stamp)",
         moved=[], nothing_moved_in=["number:handback:*", "number:ranking:*"],
         effect="Not on the path of a sampled pair."),
    MESSAGE_FLOATS,
    LIST_KEEPS_ITS_PLACE,
    PAIR_VIEW_LAYOUT,
    dict(id="docs-third-round",
         change="The runbook (step 7) and docs/TAPGRADE.md give the stop rule as three signs, one per kind of first page, any one missing meaning stop; say that the history route and the export differ for a half point that changes no points, so the blind pass uses the export; and count the third round's checks",
         moved=[], nothing_moved_in=["declared:install:*", "number:install:*", "declared:export:*", "number:export:*", "event:I*"],
         effect="The install note cites the three signs ({rbStop}: {rbStopLoad}; {rbStopPair}; {rbStopOther}; docs/TAPGRADE.md says the same: {tgStopRule}), and the notes of the pages that carry a sign name it. The runbook already told the owner to look for three things; it now says which page shows which. "
                "The half-point sentence is at {rbHalfRoute} and {tgHalfRoute}; the export chain already says the export keeps a half point as a signed deduction. "
                "Nothing measured moved and no declared property: the owner was to check the load message after the reload (install step 11) and read the header of the first pair, as before."),
    NOT_ON_THE_PATH_THIRD_ROUND,
    FLOOR_IGNORES_THE_MESSAGE,
    UPDATE_VIEW,
    DOCS_FOURTH_ROUND,
    NOT_ON_THE_PATH_FOURTH_ROUND,
]

# why each moved item moved: pattern -> reason (no numbers: they come from the two sides).  The first pattern that matches is the reason, so a specific one stands before a general one.
WHY_FIRST_DRAFT_LATER = {
    # the messages (third round)
    "measured:view_stability.load_toast.*": "the message floats above the sheet: it takes no room and moves nothing when it comes or goes",
    "measured:view_stability.refusal_toast.*": "the message floats above the sheet: it takes no room and moves nothing when it comes or goes",
    "measured:view_stability.next_pair_message.*": "the message after Save and next now floats over the top of the student's work instead of pushing the work down; the earlier script covered none of it (measured on that script by the current tool)",
    "measured:view_stability.load_toast_leaves_with_the_list_scrolled.*": "the message's timer takes it away without rebuilding the sheet, so the list stays where the reader had scrolled it; on the earlier script the message leaving rebuilt the sheet and threw the list to the top (measured on that script by the current tool)",
    "measured:window.pair_view_with_toast.body_h": "with a message up the open part is no longer smaller by the message's height, because the message floats; in the large bank it also gets what the whole head gives back (see the head change)",
    "measured:window.pair_view_with_toast.msg_over_page_px": "the message now covers this much of the page above the sheet; the earlier script's message covered none of it (it pushed the content and shrank the list instead; measured on that script by the current tool)",
    "event:P4:p": "the message part of this event is gone on the mock (a message no longer moves the content); the warning line, the chip taps and the rest stay. A judgment, not a rule: the same author's, who has now seen the change; one third taken off",
    "event:P14:added": "the message now covers the top of the student's work for the seconds it shows: the friction this fix may add; a guess",
    # the list keeps its place (third round) and lands on the same chip (fourth)
    "measured:view_stability.none_tap.jumps_to_the_top": "the list is put back where it was after the sheet is rebuilt",
    "measured:view_stability.none_tap.scroll_after_px": "the list is put back where it was after the sheet is rebuilt",
    "measured:view_stability.no_deductions_tap.scroll_after_px": "the list is put back where it was after the sheet is rebuilt",
    "measured:view_stability.grade_button_on_a_pair.scroll_after_px": "the list is put back where it was after the sheet is rebuilt",
    "measured:view_stability.hide_and_reopen_the_sheet.scroll_after_px": "hiding the sheet remembers where the list was and opening it puts the list back there (held by the end of the list where the list is short)",
    "measured:view_stability.resize_the_sheet_by_dragging_its_head.scroll_after_px": "the list is put back where it was after the sheet is rebuilt (held by the end of the list where a taller sheet leaves less to scroll)",
    "measured:view_stability.rebuild_with_ticks.scroll_after_px": "the list is put back where it was after the sheet is rebuilt",
    "measured:view_stability.rebuild_with_ticks.same_chip_shift_px": "the list is put back (the first draft threw it to the top) and the rebuild draws the warnings of the ticked parts, so the position put back shows the same chip",
    "measured:view_stability.rebuild_with_ticks.warnings_after_the_rebuild": "the rebuild draws the warnings of the ticked parts; before the fourth round only a tap did, and a rebuild blanked them",
    "event:P5:p": "the list no longer jumps to the top on the mock; what is left is the chance that a phone still does it, so p falls. A judgment, not a rule: the same author's, who has now seen the change; the event now tests the fix on a phone",
    "event:P5:kind": "p is now at or below the line the registration draws for a prediction that nothing goes wrong",
    # the pair's layout (third round: the head; fourth: the part tallies at the first render)
    "measured:window.part_headings_at_the_first_render.saying_full": "a rebuild draws the part tallies, so the parts say `full` from the first render; before the fourth round only a tap drew them",
    "measured:window.part_headings_at_the_first_render.heading_h_px": "a heading that holds its tally is a little taller than one that held none",
    "measured:window.pair_view.head_h": "the tag stays on one line, so the head keeps its height",
    "measured:window.pair_view_with_toast.head_h": "the tag stays on one line, so the head keeps its height",
    "measured:window.*.body_h": "the head keeps its height, so the open part of the sheet is taller",
    "measured:window.pair_view.body_pct_of_screen": "the head keeps its height, so the open part of the sheet is taller",
    "measured:window.per_question.*.scroll_h": "each part heading holds its tally from the first render and is taller by it, so the list is longer by the sum (the fourth round)",
    "measured:window.per_question.*.screens": "the open part is taller in the large bank, so the same list is fewer screens of it; the headings' growth lengthens the list a little and gives a little back, in both banks",
    "measured:window.screens_per_question.*": "the open part is taller in the large bank, so the same list is fewer screens of it; the headings' growth lengthens the list a little and gives a little back, in both banks",
    "measured:window.pair_view_largest_sheet.screens_for_first_question": "the open part is taller, so the same list is fewer screens of it; the headings' growth gives a little back",
    "measured:window.queue_button_from_pair.offset_in_body_px": "Queue is the last row of a list that is longer by the part headings' growth (the fourth round)",
    "measured:window.queue_button_from_pair.screens_down": "Queue is further down a longer list (the headings' growth); the open part is taller in the large bank, so the distance in screens is shorter there, and a little longer in the example-size bank, where the open part is as it was",
    "measured:window.*": "the open part of the sheet is taller, so the same list is fewer screens of it",
    "measured:chips.at_the_default_sheet.part_group_height_px.mean": "a part's heading holds its tally from the first render and is taller by it (the fourth round)",
    "measured:chips.at_the_default_sheet.part_group_height_px.max": "a part's heading holds its tally from the first render and is taller by it (the fourth round)",
    "measured:chips.at_the_default_sheet.part_group_height_px.share_that_fit_in_the_open_body": "the open part of the sheet is taller, so more parts fit whole",
    "measured:chips.*": "in the large bank the open part of the sheet is taller, so more of the list is in view at once; in both banks the list is a little longer, so the scroll windows looked at, and what is in view in them, differ a little",
    "measured:first_contact.pair_title_slack_px_one_pair_per_question.*": "the stamp is set smaller when it is long, so it leaves the title its room",
    "measured:view_stability.chip_tap.max_chip_shift_px": "a chip tap changes the stamp's points and its part's heading: before, a longer stamp made the tag wrap and the head grow, which moved every chip under it (the shift measured in the example-size bank), and the first tap in a part grew the heading, which the rebuild now draws at the start (the shift measured in the large bank); neither moves anything now",
    "measured:view_stability.chip_tap.scroll_jump_px": "the list moved at a chip tap, while the chips under the finger moved; a chip tap no longer changes the head or the part's heading, so nothing moves",
    "measured:view_stability.*.scroll_before_px": "where the tool had put the row before the tap (the middle of the open part, or a set offset, held by the end of the list): the open part, the head over it and the headings above the row changed, so the same row sits at another scroll position",
    # the sheet's lowest height (fourth round; the head change moved the strips that set it)
    "measured:view_stability.sheet_at_its_floor.raised_by_the_message_px": "a message that floats above the sheet is not counted in the sheet's lowest height",
    "measured:view_stability.sheet_at_its_floor.sheet_h_with_the_load_message_px": "a message is not counted in the lowest height, and the head keeps its height, so the strips that set the floor are lower",
    "measured:view_stability.sheet_at_its_floor.*": "the head keeps its height, so the strips that set the lowest height are lower",
}

WHY = {
    "measured:sample.file": "the file's schema id changed",
    "measured:first_contact.outside_sample.hint_button_visible_fraction_with_toast": "the note sits first in the body, so the load toast no longer pushes its button out of the open part",
    "measured:first_contact.outside_sample.notice.*": "the note moved from after the purpose line to before it",
    "measured:first_contact.outside_sample.tap_save_and_next.*": "Save and next on a page outside the sample asks once before it writes, naming the blind pass and Canvas (measured on both scripts)",
    "measured:two_pages.*": "the merge at save time and the re-read when a page returns (the first-draft script lost the other page's pick)",
    "declared:queue:2:amount": "the toast, then the note with its button: fewer things to read before the button",
    "number:queue:*": "follows from the amount",
    "event:Q1:p": "the {this} runbook names the route (the ca80695 one sent the owner to a Sample tab the Grade view does not have) and the button is first and in view; the long scroll to Queue from a pair is still there, and for a student inside the sample the trouble was never the tab alone",
    "event:Q5:p": "the sentence that says what the page is now comes before 'Changes Canvas' and is in view",
    "event:P11:p": "a write takes a third tap, on a question that names the blind pass and Canvas, and Cancel sends nothing (measured)",
    "event:P11:basis": "the question and what Cancel does are measured, not read from the code",
    "event:P13:added": "the merge at save time and the re-read when a page returns are new, and measured",
    **WHY_FIRST_DRAFT_LATER,
}

# the same, for what moved since the registration this one supersedes (built against speeds-kit be4e324): the fourth round, and a list of what did not move
CHANGES_SINCE_REPLACED = [
    TALLIES_ON_REBUILD,
    FLOOR_IGNORES_THE_MESSAGE,
    UPDATE_VIEW,
    DOCS_FOURTH_ROUND,
    NOT_ON_THE_PATH_FOURTH_ROUND,
    WHAT_DID_NOT_MOVE,
]
WHY_SINCE_REPLACED = {
    "measured:window.part_headings_at_the_first_render.saying_full": "a rebuild draws the part tallies now, so the parts say `full` from the first render; before, only a tap drew them",
    "measured:window.part_headings_at_the_first_render.heading_h_px": "a heading that holds its tally is a little taller than one that held none",
    "measured:view_stability.rebuild_with_ticks.warnings_after_the_rebuild": "the rebuild draws the warnings of the ticked parts; before, only a tap did, and a rebuild blanked them",
    "measured:view_stability.rebuild_with_ticks.same_chip_shift_px": "with the warnings drawn by the rebuild the list above the window is as long as it was, so the position put back shows the same chip (before, it landed off by what the rebuild had left undrawn)",
    "measured:view_stability.chip_tap.*": "the heading of the part already holds its tally at the first render, so the first tap in a part grows nothing under the finger (before, it grew the heading)",
    "measured:window.per_question.*.scroll_h": "each part heading holds its tally from the first render and is taller by it, so the list is longer by the sum",
    "measured:window.per_question.*.screens": "the list is longer (the part headings are taller) and the open part is the same, so it is a little more screens",
    "measured:window.screens_per_question.*": "the list is longer (the part headings are taller) and the open part is the same, so it is a little more screens",
    "measured:window.queue_button_from_pair.offset_in_body_px": "Queue is the last row of a list that is longer by the part headings' growth",
    "measured:window.queue_button_from_pair.screens_down": "Queue is further down a longer list, and the open part is the same",
    "measured:chips.at_the_default_sheet.part_group_height_px.*": "a part's heading holds its tally from the first render and is taller by it",
    "measured:chips.*": "the list is a little longer, so the scroll windows looked at, and what is in view in them, differ a little",
    "measured:view_stability.none_tap.*": "the row sits lower in the list: each part above it has a heading that holds its tally from the first render, taller by it (where the tool put the row, and where the list is put back)",
    "measured:view_stability.hide_and_reopen_the_sheet.*": "the tool scrolls to a set offset and the end of the list holds it (the example-size bank's list is short): the list is longer by the headings' growth, so its end is further down",
    "measured:view_stability.resize_the_sheet_by_dragging_its_head.*": "the tool scrolls to a set offset and the end of the list holds it (the example-size bank's list is short): the list is longer by the headings' growth, so its end is further down",
    "measured:view_stability.load_toast_leaves_with_the_list_scrolled.*": "the tool scrolls to a set offset and the end of the list holds it (the example-size bank's list is short): the list is longer by the headings' growth, so its end is further down",
    "measured:view_stability.sheet_at_its_floor.*": "a message that floats above the sheet is not counted in the sheet's lowest height now, so a sheet at its floor does not rise with the message and does not stay raised after it",
}

def comparisons(repo: Path) -> dict:
    """the comparisons to make: with the first draft always, and with the registration this one replaces when its folder docs/predictions/replaced-<commit>/ exists (one at most)"""
    out = {"first_draft": dict(dir=BASELINE_DIR, changes=CHANGES, why=WHY, since="the first draft")}
    found = sorted(p.name for p in (Path(repo) / "docs/predictions").glob("replaced-*") if p.is_dir())
    if len(found) > 1:
        raise Unattributed(f"more than one replaced registration in docs/predictions/: {found}; keep the one this registration replaces")
    if found:
        out["replaced"] = dict(dir=f"docs/predictions/{found[0]}", changes=CHANGES_SINCE_REPLACED, why=WHY_SINCE_REPLACED, since=f"the registration for {found[0][len('replaced-'):]}")
    return out


# what a measured key means, for the reader (the key itself stays in brackets)
LABELS = {
    "first_contact.outside_sample.hint_button_visible_fraction_with_toast": "'Open the sample queue' button: share inside the open part, load toast up",
    "first_contact.outside_sample.notice.index_in_body": "the note's place in the body (0 = first)",
    "first_contact.outside_sample.notice.purpose_line_index": "the purpose line's place in the body",
    "first_contact.outside_sample.notice.before_the_purpose_line": "the note comes before the purpose line",
    "first_contact.outside_sample.tap_save_and_next.asks_first": "Save and next, after Mark rest full, on a page outside the sample asks before it writes",
    "first_contact.outside_sample.tap_save_and_next.names_the_blind_pass": "the question names the blind pass",
    "first_contact.outside_sample.tap_save_and_next.says_it_writes_to_canvas": "the question says it writes to Canvas",
    "first_contact.outside_sample.tap_save_and_next.writes_after_cancel": "requests that write to Canvas after the tap, Cancel chosen when asked",
    "first_contact.outside_sample.tap_save_and_next.writes_after_ok": "requests that write to Canvas after the tap, OK chosen",
    "two_pages.stale_page_save.picks_after_this_page_saved": "picks on the phone after a stale page saved (the other page had saved one)",
    "two_pages.stale_page_save.the_other_pages_pick_is_kept": "the other page's pick kept after a stale page saved",
    "two_pages.return_to_a_stale_page.sees_it_without_a_reload": "a page that comes back shows the other page's save, no reload",
    "two_pages.return_to_a_stale_page.queue_line_for_the_pair_the_other_page_recorded.after": "queue line for the pair the other page recorded, after the page came back",
    "sample.file": "the sample file's schema id",
    # the third round
    "view_stability.load_toast.content_moves_when_it_goes_px": "the content moves when the load message goes (px)",
    "view_stability.load_toast.open_body_grows_px": "the open part grows when the load message goes (px)",
    "view_stability.refusal_toast.content_moves_when_it_comes_px": "the content moves when an error message comes (px)",
    "view_stability.next_pair_message.over_the_page_px": "the message after Save and next: px of the student's work above the sheet that it covers",
    "view_stability.next_pair_message.share_of_the_work_area_pct": "the message after Save and next: share of the student's work above the sheet that it covers (%)",
    "view_stability.load_toast_leaves_with_the_list_scrolled.scroll_after_px": "list position (px) after the load message leaves, the list scrolled before it",
    "view_stability.load_toast_leaves_with_the_list_scrolled.scroll_before_px": "list position (px) before the load message leaves (the tool scrolls to a set offset)",
    "view_stability.none_tap.scroll_after_px": "list position (px) after a tap on None",
    "view_stability.none_tap.scroll_before_px": "list position (px) before a tap on None (where the tool put the row)",
    "view_stability.none_tap.jumps_to_the_top": "a tap on None throws the list to the top",
    "view_stability.no_deductions_tap.scroll_after_px": "list position (px) after a tap on No deductions",
    "view_stability.no_deductions_tap.scroll_before_px": "list position (px) before a tap on No deductions (where the tool put the button)",
    "view_stability.grade_button_on_a_pair.scroll_after_px": "list position (px) after the bar's Grade button, tapped on a pair",
    "view_stability.hide_and_reopen_the_sheet.scroll_after_px": "list position (px) after hiding the sheet and opening it by its pill",
    "view_stability.hide_and_reopen_the_sheet.scroll_before_px": "list position (px) before hiding the sheet (the tool scrolls to a set offset)",
    "view_stability.resize_the_sheet_by_dragging_its_head.scroll_after_px": "list position (px) after pulling the sheet up by its head",
    "view_stability.resize_the_sheet_by_dragging_its_head.scroll_before_px": "list position (px) before pulling the sheet up (the tool scrolls to a set offset)",
    "view_stability.chip_tap.max_chip_shift_px": "the most a chip moves when a chip is tapped (px)",
    "window.pair_view_with_toast.msg_over_page_px": "px of the page above the sheet that the load message covers",
    "window.pair_view_with_toast.body_h": "open part of the sheet on a pair, load message up (px)",
    "window.pair_view_with_toast.head_h": "head of the sheet on a pair, load message up (px)",
    "window.pair_view.body_h": "open part of the sheet on a pair (px)",
    "window.pair_view.head_h": "head of the sheet on a pair (px)",
    "window.pair_view.body_pct_of_screen": "open part of the sheet on a pair (% of the screen)",
    "window.pair_view_largest_sheet.body_h": "open part of the sheet at its largest height (px)",
    "window.pair_view_largest_sheet.screens_for_first_question": "screens of the open part for the first question's list, sheet at its largest",
    "window.screens_per_question.median": "screens of the open part per question's list, median",
    "window.screens_per_question.max": "screens of the open part per question's list, longest",
    "window.queue_button_from_pair.screens_down": "Queue button, screens down from the top of a pair's list",
    "window.queue_button_from_pair.offset_in_body_px": "Queue button, px down from the top of a pair's list",
    "first_contact.pair_title_slack_px_one_pair_per_question.min": "room left beside the pair's title in the head, tightest question (px; below 0 = cut off)",
    "first_contact.pair_title_slack_px_one_pair_per_question.clipped": "questions whose pair title is cut off in the head",
    "first_contact.pair_title_slack_px_one_pair_per_question.borderline_under_2px": "questions with under 2 px to spare beside the pair's title",
    "chips.at_the_default_sheet.in_view.mean_fully_visible": "chips fully in view at once, mean over scroll windows (default sheet)",
    "chips.at_the_default_sheet.in_view.mean_fully_visible_when_any": "chips fully in view at once, mean over windows with at least one (default sheet)",
    "chips.at_the_default_sheet.in_view.mean_similarity_seen_together": "look-alike score of chips seen together, mean (default sheet)",
    "chips.at_the_default_sheet.in_view.pairs_seen_together": "pairs of chips in view together over the scroll windows (default sheet)",
    "chips.at_the_default_sheet.in_view.share_of_windows_with_two_or_more": "share of scroll windows with two chips or more in view (default sheet)",
    "chips.at_the_default_sheet.in_view.windows": "scroll windows looked at (default sheet)",
    "chips.at_the_default_sheet.key_in_view_with_a_chip.chip_views": "chip views counted for the key's visibility (default sheet)",
    "chips.at_the_default_sheet.key_in_view_with_a_chip.share": "share of chip views in which the key of the part is in view (default sheet)",
    "chips.at_the_default_sheet.part_group_height_px.share_that_fit_in_the_open_body": "share of part groups (header, key, chips) that fit the open part whole",
    "chips.at_the_largest_sheet.in_view.mean_fully_visible": "chips fully in view at once, mean over scroll windows (largest sheet)",
    "chips.at_the_largest_sheet.in_view.mean_fully_visible_when_any": "chips fully in view at once, mean over windows with at least one (largest sheet)",
    "chips.at_the_largest_sheet.in_view.pairs_seen_together": "pairs of chips in view together over the scroll windows (largest sheet)",
    "chips.at_the_largest_sheet.in_view.windows": "scroll windows looked at (largest sheet)",
    "chips.at_the_default_sheet.part_group_height_px.mean": "height of a part group (header, key, chips), mean (px)",
    "chips.at_the_default_sheet.part_group_height_px.max": "height of a part group (header, key, chips), tallest (px)",
    # the fourth round
    "window.part_headings_at_the_first_render.saying_full": "part headings that say `full` at the first render (of the parts of the first pair opened)",
    "window.part_headings_at_the_first_render.heading_h_px": "height of a part heading at the first render, mean (px)",
    "view_stability.chip_tap.scroll_jump_px": "the list's own movement when a chip is tapped (px)",
    "view_stability.rebuild_with_ticks.warnings_after_the_rebuild": "warnings drawn after the sheet was rebuilt, two chips ticked in a part (one was drawn before)",
    "view_stability.rebuild_with_ticks.same_chip_shift_px": "how far a chip far below the ticked part sits from where it was after a rebuild (px; 0 = the same chip)",
    "view_stability.rebuild_with_ticks.scroll_after_px": "list position (px) after a rebuild with ticks in a part",
    "view_stability.rebuild_with_ticks.scroll_before_px": "list position (px) before a rebuild with ticks (where the tool put a chip far below the ticked part)",
    "view_stability.sheet_at_its_floor.raised_by_the_message_px": "px that the load message raises a sheet pulled down to its lowest height",
    "view_stability.sheet_at_its_floor.sheet_h_with_the_load_message_px": "sheet pulled down to its lowest height, load message up (px)",
    "view_stability.sheet_at_its_floor.sheet_h_after_it_left_px": "sheet pulled down to its lowest height, after the load message left (px)",
    "view_stability.sheet_at_its_floor.sheet_h_after_a_rebuild_px": "sheet pulled down to its lowest height, after a rebuild with no message (px)",
    "view_stability.sheet_at_its_floor.stays_raised_after_it_left": "the sheet stays raised after the load message has left",
}


class Unattributed(RuntimeError):
    pass


def load_baseline(repo: Path, rel: str = BASELINE_DIR) -> dict:
    d = Path(repo) / rel
    out = {"sha": {}}
    for name in BASELINE_FILES:
        raw = (d / name).read_bytes()
        out["sha"][name] = hashlib.sha256(raw).hexdigest()
        out[name.rsplit(".", 1)[0]] = json.loads(raw.decode("utf-8"))
    return out


def snapshot(reg: dict, fixture: dict, what: str, registered_in: str | None = None, registered_before: list | None = None) -> dict[str, str]:
    """declared.json and summary.json of a baseline, from a registration (its JSON) and its fixture: the numbers it printed, as data.
    `registered_in`: the commit that added that registration to the history, when it was committed (a registration replaced before any commit has none).
    `registered_before`: the registrations committed before it, newest first: [{"commit": ..., "speeds_kit": ...}]"""
    declared = {c["id"]: [{k: v for k, v in s.items() if k not in ("target", "note")} for s in c["steps"]] for c in fixture["chains"]}
    segs = {}
    for s in reg["segments"]:
        chk = next(c for c in reg["chain_check_json"]["files"][0]["chains"] if c["id"] == s["id"])
        segs[s["id"]] = {"steps": s["steps"], "load": round(s["load"], 2), "peak_slots": chk["peak_slots"], "findings": len(chk["findings"]), "rank": s["rank"],
                         "over_budget": {b: reg["over_budget_steps"][b][s["id"]] for b in ("2", "3", "4")}}
    summary = {
        "what": what,
        "registered_in": registered_in,
        "registered_before": registered_before or [],
        "artifact": {k: reg["artifact"][k] for k in ("commit", "script_sha256", "script_lines", "version", "build")},
        "drafted": reg["drafted"],
        "segments": segs,
        "findings": [[c["id"], f["step"], f["verifier"]] for c in reg["chain_check_json"]["files"][0]["chains"] for f in c["findings"]],
        "events": {e["id"]: {"p": e["p"], "basis": e["basis"], "kind": e["kind"], "steps": [[r["chain"].split("-sample-")[-1], r["step"]] for r in e["steps"]]} for e in reg["events"]},
        "unstable_pairs": [[u["a"], u["b"], u["a_above_b_share"]] for u in reg["parameters"]["rank_ties"]["unstable_pairs"]],
        "groups": reg["ranking"]["groups_longest_first"],
    }
    dump = lambda d: json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    return {"declared.json": dump(declared), "summary.json": dump(summary)}


def flatten(obj, prefix: str = "") -> dict:
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    else:
        out[prefix] = obj
    return out


def fmt(v) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) < 100 else f"{v:,.0f}"
    if isinstance(v, int):
        return f"{v:,}" if abs(v) >= 10000 else str(v)
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return "none" if v is None else str(v)


def delta(a, b) -> str:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        d = b - a
        return ("+" if d > 0 else "-" if d < 0 else "") + fmt(abs(round(d, 4)))
    return ""


def _item(key, what, before, after, per_bank=None):
    return {"key": key, "what": what, "before": fmt(before), "after": fmt(after), "delta": delta(before, after), **({"banks": per_bank} if per_bank else {})}


def label_of(key: str) -> str:
    """what a measured key means, for the reader: LABELS, or a sentence for the per-question keys; the key itself when nothing is known"""
    if key in LABELS:
        return LABELS[key]
    m = re.fullmatch(r"window\.per_question\.(Q\d+)\.(body_h|screens|scroll_h)", key)
    if m:
        return f"{m.group(1)}, the pair opened: " + {"body_h": "open part of the sheet (px)", "screens": "screens of the open part that its list is", "scroll_h": "length of its list (px)"}[m.group(2)]
    return key


def measured_items(baseline: dict, new_large: dict, new_example: dict) -> list[dict]:
    """every measured key whose value is not the baseline's (timings aside), the two bank sizes together"""
    out = {}
    extra = flatten(baseline["new-keys"].get("predictors", {}))        # keys that did not exist when the baseline was measured: its own script, measured again
    for bank, old, new in (("large", baseline["measured"], new_large), ("example", baseline["measured-example-bank"], new_example)):
        o, n = flatten(old["predictors"]), flatten(new["predictors"])
        o.update({k: v for k, v in extra.items() if k not in o and bank == "large"})
        o["sample.file"] = old["sample"].get("file", "tapgrade-proposals/2 with a sample key")
        n["sample.file"] = new["sample"].get("file")
        for k in sorted(set(o) | set(n)):
            if k.startswith(NOISY):
                continue
            if k in o and k in n and o[k] == n[k]:
                continue
            if k not in o and bank == "example":
                continue                                               # the baseline script was re-measured at the large bank only; the example bank's new keys follow the large one's
            out.setdefault(k, {})[bank] = (o.get(k, "not measured"), n.get(k, "no longer measured"))
    items = []
    for k, banks in sorted(out.items()):
        (b0, a0) = banks.get("large", next(iter(banks.values())))
        same = all(v == (b0, a0) for v in banks.values()) and len(banks) == 2 or len(banks) == 1
        items.append(_item(f"measured:{k}", f"{label_of(k)} (`{k}`)", b0, a0, None if same else {bk: [fmt(x) for x in v] for bk, v in banks.items()}))
        if len(banks) == 1:
            items[-1]["what"] += f", {next(iter(banks))} bank"
    return items


def declared_items(old_declared: dict, new_doc: dict) -> list[dict]:
    """a declared property (any step key except the text) that differs, step by step, chain by chain"""
    items = []
    new = {c["id"]: c["steps"] for c in new_doc["chains"]}
    for cid in sorted(set(old_declared) | set(new)):
        suffix = cid.split("-sample-")[-1]
        if cid not in old_declared or cid not in new:
            items.append({"key": f"declared:{suffix}:0:chain", "what": f"chain {suffix}", "before": "present" if cid in old_declared else "absent", "after": "present" if cid in new else "absent", "delta": ""})
            continue
        o, n = old_declared[cid], new[cid]
        if len(o) != len(n):
            items.append({"key": f"declared:{suffix}:0:steps", "what": f"{suffix}: number of steps", "before": str(len(o)), "after": str(len(n)), "delta": ""})
            continue
        for i, (so, sn) in enumerate(zip(o, n), 1):
            sn = {k: v for k, v in sn.items() if k not in ("target", "note")}
            for k in sorted(set(so) | set(sn)):
                if so.get(k, "default") != sn.get(k, "default"):
                    items.append(_item(f"declared:{suffix}:{i}:{k}", f"{suffix} step {i} ({sn.get('op', so.get('op'))}): {k}", so.get(k, "default"), sn.get(k, "default")))
    return items


def top_five(events: dict) -> list[str]:
    """the five friction events with the highest p (ties in the order of the table), as the registration's first page prints them"""
    return [i for i, e in sorted(((i, e) for i, e in events.items() if e["kind"] == "friction"), key=lambda ie: -ie[1]["p"])[:5]]


def number_items(old: dict, segments: list[dict], findings: list[list], unstable: list, groups: list, events: list[dict]) -> list[dict]:
    items = []
    for s in segments:
        suffix = s["id"].split("-sample-")[-1]
        o = old["segments"][s["id"]]
        for k, new_v in (("steps", s["steps"]), ("load", round(s["load"], 2)), ("peak_slots", s["peak_slots"]), ("findings", s["findings"]), ("rank", s["rank"])):
            if o[k] != new_v:
                two = k == "load"
                items.append(_item(f"number:{suffix}:{k}", f"{suffix}: {k.replace('_', ' ')}", f"{o[k]:.2f}" if two else o[k], f"{new_v:.2f}" if two else new_v) | ({"delta": f"{new_v - o[k]:+.2f}"} if two else {}))
        for b in ("2", "3", "4"):
            if o["over_budget"][b] != s["over_budget"][b]:
                items.append(_item(f"number:{suffix}:over_budget_B{b}", f"{suffix}: steps over B = {b}", o["over_budget"][b], s["over_budget"][b]))
    fo, fn = {tuple(f) for f in old["findings"]}, {tuple(f) for f in findings}
    for f in sorted(fn - fo):
        items.append({"key": f"number:{f[0].split('-sample-')[-1]}:finding_added", "what": f"a finding appears: {f[0].split('-sample-')[-1]} step {f[1]} {f[2]}", "before": "none", "after": "present", "delta": ""})
    for f in sorted(fo - fn):
        items.append({"key": f"number:{f[0].split('-sample-')[-1]}:finding_removed", "what": f"a finding goes: {f[0].split('-sample-')[-1]} step {f[1]} {f[2]}", "before": "present", "after": "none", "delta": ""})
    if old["unstable_pairs"] != unstable:
        items.append({"key": "number:ranking:ties", "what": "pairs of segments the weights do not order stably", "before": fmt(old["unstable_pairs"]), "after": fmt(unstable), "delta": ""})
    if old["groups"] != groups:
        items.append({"key": "number:ranking:order", "what": "the order of the segments", "before": fmt(old["groups"]), "after": fmt(groups), "delta": ""})
    now = top_five({e["id"]: e for e in events})
    was = top_five(old["events"])
    if was != now:
        items.append({"key": "number:events:top_five", "what": "the five friction events with the highest p", "before": ", ".join(was), "after": ", ".join(now), "delta": ""})
    return items


def event_items(old: dict, events: list[dict]) -> list[dict]:
    items, new = [], {e["id"]: e for e in events}
    for eid, e in new.items():
        o = old["events"].get(eid)
        if o is None:
            items.append({"key": f"event:{eid}:added", "what": f"new event {eid}: {e['event']}", "before": "none", "after": f"p {e['p']:.2f}, {e['basis']}", "delta": ""})
            continue
        for k in ("p", "basis", "kind"):
            if o[k] != e[k]:
                items.append(_item(f"event:{eid}:{k}", f"{eid} {k}", f"{o[k]:.2f}" if k == "p" else o[k], f"{e[k]:.2f}" if k == "p" else e[k]) | ({"delta": f"{e[k] - o[k]:+.2f}"} if k == "p" else {}))
        if [[r["chain"].split("-sample-")[-1], r["step"]] for r in e["steps"]] != o["steps"]:
            items.append({"key": f"event:{eid}:steps", "what": f"{eid} steps", "before": fmt(o["steps"]), "after": fmt([[r["chain"].split('-sample-')[-1], r["step"]] for r in e["steps"]]), "delta": ""})
    for eid in old["events"]:
        if eid not in new:
            items.append({"key": f"event:{eid}:removed", "what": f"event {eid} removed", "before": "present", "after": "none", "delta": ""})
    return items


def script_facts(old: dict, inputs: dict, n_events: int, n_findings: int) -> dict:
    a, b = old["artifact"], inputs["speeds_kit"]["script"]
    return {"before": {"commit": a["commit"], "sha256": a["script_sha256"], "lines": a["script_lines"], "build": a["build"], "version": a["version"],
                       "events": len(old["events"]), "findings": len(old["findings"])},
            "this": {"commit": inputs["speeds_kit"]["commit"], "sha256": b["sha256"], "lines": b["lines"], "build": b["build"], "version": b["version"],
                     "events": n_events, "findings": n_findings}}


def matches(key: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(key, p) for p in patterns)


def attribute(items: list[dict], changes: list[dict] | None = None, why_table: dict | None = None, since: str = "the first draft", fill=None) -> list[dict]:
    """the comparison's changes with the moved items under each; stops when an item belongs to no change, or to two, has no reason, or sits where nothing was said to move.
    `fill` turns a text with {placeholders} into the sentence that is printed (see `compute`); by default the text is printed as it stands."""
    changes = CHANGES if changes is None else changes
    why_table = WHY if why_table is None else why_table
    fill = fill or (lambda text: text)
    claimed = {}
    out = []
    for ch in changes:
        got = [i for i in items if matches(i["key"], ch["moved"])]
        for i in got:
            if i["key"] in claimed:
                raise Unattributed(f"{i['key']} is claimed by two changes ({claimed[i['key']]} and {ch['id']})")
            claimed[i["key"]] = ch["id"]
            why = next((w for p, w in why_table.items() if fnmatch.fnmatchcase(i["key"], p)), None)
            if why is None:
                raise Unattributed(f"{i['key']} moved but WHY has no reason for it: add one in checks/hw2_sample_prediction/changes.py")
            i["why"] = fill(why)
        out.append({"id": ch["id"], "change": fill(ch["change"]), "effect": fill(ch["effect"]), "moved": got})
    for ch in changes:                                   # a claim that nothing moved is checked against what moved
        for i in items:
            if matches(i["key"], ch["nothing_moved_in"]):
                raise Unattributed(f"{ch['id']} says nothing moved in {ch['nothing_moved_in']}, but {i['key']} did ({i['before']} -> {i['after']}): say which change moved it")
    loose = [i for i in items if i["key"] not in claimed]
    if loose:
        raise Unattributed(f"these moved since {since} and no change claims them: " + "; ".join(f"{i['key']} ({i['before']} -> {i['after']})" for i in loose)
                           + ". Read what changed in TapGrade, then say which change moved each in checks/hw2_sample_prediction/changes.py (CHANGES and WHY, or their SINCE_REPLACED twins).")
    return out


def filler(inputs: dict):
    """the function that turns a text of CHANGES or WHY into the sentence that is printed: {this} is the snapshot's short commit, {rbRoute} and the other anchors of cites.py the line they cite"""
    cite = Cites(inputs["citations"])
    facts = {"this": inputs["speeds_kit"]["commit"][:7], **{k: cite(k) for k in inputs["citations"]}}

    def fill(text: str) -> str:
        try:
            return text.format_map(facts)
        except (KeyError, IndexError, ValueError) as e:
            raise Unattributed(f"a text of checks/hw2_sample_prediction/changes.py has a placeholder that is no anchor of cites.py ({e!r}): {text[:80]!r}") from e
    return fill


def compute(repo: Path, inputs: dict, MJ: dict, AJ: dict, doc: dict, segments: list[dict], findings: list, unstable: list, groups: list, events: list[dict]) -> dict:
    """{comparison id: {"scripts", "baseline", "changes", "moved_count"}} for each comparison of `comparisons`"""
    result = {}
    fill = filler(inputs)
    for cid, spec in comparisons(repo).items():
        baseline = load_baseline(repo, spec["dir"])
        items = (measured_items(baseline, MJ, AJ) + declared_items(baseline["declared"], doc)
                 + number_items(baseline["summary"], segments, findings, unstable, groups, events) + event_items(baseline["summary"], events))
        result[cid] = {"scripts": script_facts(baseline["summary"], inputs, len(events), len(findings)),
                       "baseline": {"path": spec["dir"] + "/", "sha256": baseline["sha"], "registered_in": baseline["summary"].get("registered_in"),
                                    "registered_before": baseline["summary"].get("registered_before", []), "new_keys_check": baseline["new-keys"].get("checked_against_the_baseline")},
                       "changes": attribute(items, spec["changes"], spec["why"], spec["since"], fill), "moved_count": len(items)}
    return result
