---
id: tool.non-utf-8-files
kind: tool
status: VERIFIED
title: "Non-UTF-8 files"
sources: [S82]
---

# Non-UTF-8 files

**Sources:** [S82](src.s82.md)

Claude can't use NotebookEdit on a file that isn't valid UTF-8. The same goes for Edit, unless the file starts with a little-endian UTF-16 byte-order mark. When Claude tries, the tool refuses the change and leaves the file untouched. Refused files include non-ASCII text saved in a legacy encoding such as Windows-1252 or Shift-JIS, binary files, and UTF-8 with an invalid byte sequence.
