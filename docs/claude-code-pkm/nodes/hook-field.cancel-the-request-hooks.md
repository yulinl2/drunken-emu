---
id: hook-field.cancel-the-request-hooks
kind: hook-field
status: VERIFIED
title: "Cancel the request"
sources: [S85]
---

# Cancel the request

**Sources:** [S85](src.s85.md)

return: `"action": "cancel"`; the server receives: `cancel`, along with the values the user submitted. To withhold them, return `"decline"`

## Linked from

- [Cancel the request](hook-field.cancel-the-request.md)
