# Visual Quality Gates

These gates decide whether a diagram is readable enough to call `Verified`.
They are separate from engineering checks such as `.mdj` open/save/export.

## Status Split

- `Engineering Verified`: StarUML/MCP can open, write, save, and export.
- `Diagram Quality Verified`: exported PNGs are visually readable and match the intended UML semantics.

Editable StarUML delivery may be final `Verified` only when both statuses pass.

## Universal Diagram Gates

- No important text is clipped, hidden, or outside its shape.
- No relationship line crosses a class title, state label, use case label, lifeline header, or activity action text.
- Long labels are shortened, wrapped, or moved to notes; do not rely on default StarUML text overflow behavior.
- Main business flow is visually traceable without following more than two crossing lines at a time.
- Diagrams use stable zones, lanes, columns, or layers instead of an unstructured grid.
- Imported Mermaid diagrams are treated as drafts until exported PNGs are inspected and repaired.
- Global auto-layout is allowed only for first drafts. Final repair must use local movement, resizing, and edge routing.

## Use Case Diagram Gates

- Actor-to-use-case lines connect only to main use cases unless a secondary actor truly participates.
- Use cases are grouped by business module, not by simple row/column fill order.
- Shared included use cases are placed close to their base use cases.
- Optional/conditional use cases use `extend` and are placed near the extension point.
- System boundary is present when a diagram has more than one actor or more than one functional cluster.
- Single-actor diagrams still need module grouping when they contain more than 8 use cases.
- Actor glyph and actor label must be fully visible; a cropped actor head or off-canvas actor fails the gate.
- Use case labels must not be crossed by actor association lines.
- Maximum obvious actor-line crossings: `3` for a single actor diagram, `7` for an overall diagram.

## Class Diagram Gates

- Existing class names, attributes, operations, and language style are preserved unless the user requests translation or redesign.
- Role inheritance is top-center or top-left with enough whitespace around generalization arrows.
- Core domain entities occupy the visual center.
- Aggregates and composition structures are placed close together.
- Support classes, controllers, services, repositories, gateways, and adapters stay at the edges.
- Multiplicity labels are readable and do not sit on class borders or arrowheads.
- Global auto-layout must not be run after manual semantic grouping unless a follow-up repair pass restores groups.
- If the source model used English identifiers, class names and members remain English or bilingual by explicit plan; silently replacing them with Chinese-only members fails source-preservation review.
- Class boxes must be sized after restoring source members, not before.
- Relationship labels and multiplicities must be adjusted after final class resize.

## State Diagram Gates

- State boxes are wide enough for the longest state name.
- Transition labels are short event/guard labels. Long business explanations belong in notes or documentation.
- A lifecycle diagram reads primarily left-to-right or top-to-bottom, not as a tangled graph.
- Initial and final pseudostates do not overlap with transition labels.
- State nodes must not use default small boxes when Chinese labels exceed available width.
- No transition label may sit inside another state box.
- Maximum transition label overlap: `0`.

## Sequence Diagram Gates

- Participants follow a stable order, normally Actor -> Boundary/Page -> Controller/Service -> Repository/Gateway -> DB/External.
- Lifeline headers are wide enough for participant names.
- Messages are evenly spaced and ordered top-to-bottom.
- Branches use visible `alt/else` or equivalent fragments with guard labels.
- Return messages are visually distinct from calls.
- Imported Mermaid sequence diagrams are drafts unless activation bars, fragments, and message spacing are visually checked.
- A sequence diagram with message labels floating far from visible arrows fails the gate.
- Branch labels must be placed inside or adjacent to the fragment they describe, not as isolated text.
- Lifeline spacing must leave enough horizontal room for the longest message between adjacent participants.

## Activity Diagram Gates

- Main flow has a clear direction.
- Decision nodes have guard labels.
- Branches rejoin through explicit merge/join points.
- Action nodes reserve enough width for Chinese text.
- Loops do not cross action labels.

## Review Evidence

Before final `Verified`, record one of these for each diagram:

- `visualStatus: Verified`
- `visualStatus: Unverified: <reason>`
- `visualStatus: Failed: <reason>`

If a diagram is only structurally present but visually poor, use `Engineering Verified` plus `Diagram Quality Unverified`.
