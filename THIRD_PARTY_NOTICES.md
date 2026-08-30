# Third-party notices

`vendor/` contains unmodified upstream browser bundles, redistributed so the kit
runs with no network access. Rationale is in README.md ("Why it is shaped this
way", item 1): the sandbox egress proxy re-signs TLS and headless Chromium
rejects the resulting certificate, so CDN loads fail with
`ERR_CERT_AUTHORITY_INVALID`.

All four are MIT licensed, which permits redistribution with attribution.

| File | Package | Version | SHA-256 (first 16) | Size |
|---|---|---|---|---|
| `vendor/react.js` | react (`react.production.min.js`) | 18.2.0 | `4b4969fa4ef35943` | 10.5 KB |
| `vendor/reactdom.js` | react-dom | 18.2.0 | `21758ed084cd0e37` | 128.8 KB |
| `vendor/babel.js` | @babel/standalone | 7.23.5 | `558a1f7f5ffe2184` | 2772.6 KB |
| `vendor/tailwind.js` | tailwindcss (Play CDN build) | *not embedded* | `6cdb72b843779c37` | 401.9 KB |

## How these versions were determined

- **react / react-dom 18.2.0** — confirmed two independent ways: a `18.2.0`
  version string inside each bundle, and the presence of `createRoot` /
  `hydrateRoot`, which exist only in React 18+. `bin/sync_artifact.py` emits a
  `ReactDOM.createRoot(...)` mount call, consistent with 18.
- **@babel/standalone 7.23.5** — version string in the bundle.
- **tailwindcss** — the Play CDN build embeds no version string. The SHA-256
  above is therefore the only pin; treat the hash, not a version number, as the
  identity of this file.

## Licenses

- **React, React DOM** — MIT, Copyright (c) Meta Platforms, Inc. and affiliates.
  The `@license React` header is retained verbatim at the top of `vendor/react.js`.
- **Babel (@babel/standalone)** — MIT, Copyright (c) 2014-present Sebastian
  McKenzie and other contributors.
- **Tailwind CSS** — MIT, Copyright (c) Tailwind Labs, Inc.

This kit itself ships under **Apache-2.0** (`LICENSE`, `NOTICE`). The MIT
license of the vendored bundles is compatible with that: MIT is permissive, so
the bundles may be redistributed inside an Apache-2.0 work provided their own
copyright notices are retained. They are — `vendor/react.js` keeps its
`@license React` header verbatim, and the copyright holders are listed above.

## Replacing a bundle

Fetch the upstream file, overwrite in `vendor/`, update the version and SHA-256
in the table above, and re-run `python3 checks/ci_claims.py`. A bundle swap that
changes mount cost will move the C3 slope; that is expected, and the claims
check asserts the *shape* of the relationship rather than a constant, so it
should still pass. If it does not, that is a real finding and belongs in the
`## Falsified` section of README.md.
