---
id: feature.background-sessions-can-t-read-desktop-documents-or-download
kind: feature
status: VERIFIED
title: "Background sessions can't read Desktop, Documents, or Downloads on macOS"
sources: [S26]
---

# Background sessions can't read Desktop, Documents, or Downloads on macOS

**Sources:** [S26](src.s26.md)

On macOS, the background session host runs as its own process and requests access to protected folders separately from your terminal. If a background session reports `Operation not permitted` when reading `~/Desktop`, `~/Documents`, `~/Downloads`, or another protected location, grant access in System Settings under Privacy & Security > Files and Folders, or enable Full Disk Access for the entry.
