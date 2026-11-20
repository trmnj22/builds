---
type: build-log
key: build-log
person: {{name}}
built: {{date}}
---
# Build log

- Built: {{date}}
- How: {{workflow (ultracode) | helpers | one agent}}
- Sources read: {{list with pages}}
- Not read: {{list with reason}}
- Notes written: {{counts by type}}
- Notes updated (already existed): {{count}}
- Facts checked: {{n}}. Supported: {{n}}. Flagged: {{n}}. Removed: {{n}}. Fixed: {{n}}.
- Supported + Flagged + Removed = Facts checked. Fixed counts lines changed by a fix, whatever their final state.

## Fixed during checking
- {{fact}} in [[note]]: {{verdict and fix}}

## Removed during checking
- {{fact}} in [[note]]: {{reason}}

## Flagged during checking
- {{fact}} in [[note]]: {{reason}}

## Questions asked
1. …

[[Index]]
