# Zenodo DOI runbook

*v0.1.0 · 2026-08-31 · written because P5 sat in the human queue for three
sessions as "enable Zenodo, then say the word" with no actual instructions.*

Two actors. The human does part A in a browser; a session does part B by API.
**Part A must complete first and the order is not recoverable** — see the
constraint below before doing anything.

---

## The constraint that makes ordering matter

Zenodo mints a DOI *at the moment a GitHub Release is published*, and only for
releases created **after** the repository is switched on in Zenodo. A release
cut first mints nothing, and the version number is spent: a GitHub repository
cannot be attached to an existing Zenodo record afterwards, no DOI can be
reserved ahead of time, and there is no way to learn the DOI before it is
minted. Recorded in OPEN-PROBLEMS P5 at confidence B on 2026-08-30; raised to
**A** on 2026-08-31 after three independent sources agreed.

Current state, checked 2026-08-31: **0 tags, 0 releases** on the repository, and
no `drunken-emu` record on Zenodo. Nothing has been spent; `v0.1.0` is free.

---

## Part A — human, in a browser (~5 minutes)

### A1. Switch the repository on in Zenodo

1. <https://zenodo.org> → **Log in with GitHub** → authorise when redirected.
2. <https://zenodo.org/account/settings/github/> — the repository list.
3. Find `drunken-emu`. If it is missing, press **Sync now** (newly created or
   newly public repositories often need one sync).
4. Move its toggle to **On**.

Stop here and confirm the toggle is on. Everything in Part B depends on it.

### A2. Authorise ORCID auto-update — **at DataCite, not at Zenodo**

This is the step the earlier ledger entry described wrongly. Zenodo mints its
DOIs through DataCite, so the permission lives in a DataCite profile:

1. <https://profiles.datacite.org/> → **Sign in with ORCID** → Authorise.
2. In **Settings**, next to **ORCID Auto-Update**, press **Click to Enable**.
3. Approve the permission prompt. DataCite then appears under Trusted Parties
   in your ORCID account settings, and every future DOI carrying your ORCID iD
   lands in your ORCID record without manual entry.

Two things worth knowing before you wonder whether it broke:

- Auto-update fires only when the ORCID iD is in the DOI's **creators** field.
  A contributor-only iD is ignored. `CITATION.cff` lists the iD under
  `authors:`, which Zenodo maps to `creators` — correct as it stands.
- For repositories that version heavily, DataCite pushes only the **first** DOI
  to ORCID, not each subsequent version. So `v0.1.0` will appear and `v0.2.0`
  will not. That is expected behaviour, not a misconfiguration.

### A3. Optional but recommended: rehearse on the sandbox

<https://sandbox.zenodo.org> is a throwaway copy of Zenodo. Enabling a
repository there and cutting a disposable tag exercises the whole path without
consuming a real version number. The integration's own documentation advises
testing on the sandbox before doing this in production.

---

## Part B — session, by API (~1 minute)

Say the word once A1 is on. A session then runs, with `Contents: RW` only:

    TAG=v0.1.0
    git tag -a $TAG -m "drunken-emu $TAG"
    git push origin $TAG
    curl -s -X POST -H "Authorization: Bearer $(cat /home/claude/.gh_pat)" \
      -H "Accept: application/vnd.github+json" -H "User-Agent: claude" \
      https://api.github.com/repos/yulinl2/drunken-emu/releases \
      -d "{\"tag_name\":\"$TAG\",\"name\":\"$TAG\",\"generate_release_notes\":true}"

Then, after Zenodo has archived it (a minute or two):

1. Read the DOI at <https://zenodo.org/me/uploads>, opening the `drunken-emu`
   record. Take the one under **Cite all versions** — that is the *concept* DOI,
   which always resolves to the newest version and is the one to cite.
2. Apply it to both files in one step:

       bin/apply_doi.sh 10.5281/zenodo.XXXXXXX

   which inserts the badge under the CI badge in `README.md` and adds an
   `identifiers:` block to `CITATION.cff`. It is idempotent — running it twice
   replaces rather than duplicates.
3. Commit and push once, per `CONTRIBUTING.md`.

---

## Failure modes seen in the wild

| Symptom | Cause |
|---|---|
| Repository absent from the Zenodo list | Not synced yet — press **Sync now** |
| Release published, no DOI | Toggle was off at publish time. The version number is spent; enable, then cut the next tag |
| DOI minted, ORCID record unchanged | ORCID auto-update not enabled in DataCite Profiles, or the iD sits in `contributor` rather than `creators` |
| Second release does not reach ORCID | Expected: DataCite pushes only the first DOI of a versioned series |
