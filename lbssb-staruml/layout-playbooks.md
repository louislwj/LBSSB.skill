# Layout Playbooks

These playbooks define human-like layout strategy before MCP drawing.

## General Method

1. Inspect local baselines first: parent `mcp/*.mjs`, previous good `.mdj`, exported PNGs, `.lbssb`, and course/reference summaries.
2. If a good baseline project exists for the same assignment/domain, copy/adapt that `.mdj` instead of rebuilding from scratch.
3. Build `DiagramPlan`: elements and relationships.
4. Build `LayoutPlan`: zones, lanes, anchor points, expected line routes.
5. Draw or repair a pilot diagram or the highest-risk diagram first.
6. Export PNG and inspect visually.
7. Repair locally using move/resize/edge routing.
8. Reuse the proven layout pattern for the remaining diagrams.

Do not batch-generate every diagram before seeing one exported result.

The preferred native repair implementation is the course-style script pattern:

- `loadDiagram(name, types)`;
- `namedNodes(ctx)` and `endpointNodes(ctx)`;
- `setBox(view, x, y, width, height)` through StarUML API/MCP;
- `setEdge(edge, points, lineStyle)` through StarUML API/MCP;
- explicit layout maps per diagram family;
- export and inspect after each family.

This pattern is faster and visually better than repeated global auto-layout. Use global auto-layout only as a draft bootstrap and never after final manual bounds/routes are set.

## LayoutPlan Minimum

Every complex native diagram needs concrete geometry before MCP drawing:

- `canvas`: width and height.
- `zones`: named rectangles for modules, lanes, actors, role inheritance, core domain, support area, exception area.
- `elementBounds`: final-ish x/y/width/height for each visible element.
- `primaryEdges`: business-critical lines that must stay readable.
- `secondaryEdges`: optional/include/dependency/return lines that may be edge-routed, hidden, or delayed.
- `labelBudget`: max label length, wrap/shorten rules, minimum box width for Chinese text.
- `routePolicy`: direct, orthogonal, edge-routed, or hidden-if-noisy.

If these fields are missing, the diagram is not ready for bulk native generation.

## Use Case Layout

Use zones:

- left/right margins: actors;
- center: main business use cases;
- inner secondary ring: included use cases;
- lower or side area: optional/extend use cases;
- boundary rectangle: system scope.

For single-actor diagrams, group by business module:

- account;
- order;
- borrow/return;
- teacher appointment;
- evaluation/ranking.

Actor lines should connect to module entry use cases. Shared includes stay close to the base use case.

Baseline-aligned use case layout:

- for role-specific diagrams, a vertical main-use-case column is acceptable and often clearer than artificial module cards;
- place secondary included use cases in a right-side column close to their base use cases;
- preserve `<<include>>` / `<<extend>>` semantics when they are readable;
- avoid a central actor bus; if actor lines are numerous, keep the actor outside the boundary and connect directly with clean diagonal/short lines;
- do not replace a semantically rich use case diagram with isolated "module entry" ovals unless the included/extended details remain visible elsewhere.

Coordinate defaults:

- canvas: `1600 x 1100` for role-specific use case diagrams, `1900 x 1200` for overall diagrams.
- actor margin: at least `180` px outside the system boundary.
- boundary padding: at least `80` px.
- use case size: at least `210 x 70`; increase width for labels over 8 Chinese characters.
- module gap: at least `70` px horizontal and `60` px vertical.

Line budget:

- actor associations connect only to entry use cases.
- include/extend lines stay inside the boundary whenever possible.
- hide or defer secondary actor lines if they cross use case labels.
- if a single actor has more than 6 direct associations, introduce module entry use cases or split the diagram.

## Class Layout

Recommended zones:

- top: role/user inheritance;
- center: core domain trunk;
- left: order and borrowing aggregates;
- right: teacher appointment aggregate;
- bottom: payment/evaluation/support objects;
- edges: service/repository/gateway when needed.

Procedure:

1. Place classes by zone.
2. Size boxes based on attributes and operations.
3. Draw inheritance first.
4. Draw short aggregate/composition relations.
5. Draw cross-aggregate associations.
6. Add multiplicity labels.
7. Add dependencies only if they clarify architecture.

Avoid global layout after step 1 unless it is followed by a full local repair pass.

Coordinate defaults:

- canvas: `1900 x 1350` minimum for 18-28 classes.
- role/user inheritance zone: top center, `y <= 260`.
- core domain zone: visual center, `x 550-1350`, `y 360-850`.
- aggregate zones: left/right of core, not diagonally scattered.
- support zone: bottom or outer edges; support boxes should not dominate entity boxes.
- class width: max of `220` and `8 * longestMemberChars + 60`; height from visible compartments.

Baseline-aligned class layout:

- BCE style is preferred for training-project deliverables when no conflicting source model exists.
- Left column: `<<boundary>>` View/Adapter classes.
- Middle-left column: `<<control>>` Control classes.
- Middle/right area: `<<entity>>` domain classes.
- Far right/bottom: support records, payment/review, repository/interface/external classes.
- Preserve English class names, attributes, operations, and stereotypes.
- It is better to show fewer high-value dependencies clearly than to draw every View-to-Control or Control-to-Repository dependency through the domain trunk.
- Multiplicity labels are first-class deliverable content. Reposition them after routing.

Line budget:

- draw inheritance and compositions first.
- draw only P0/P1 associations before checking readability.
- route repository/service dependencies around edges.
- remove View-to-Control and obvious technical dependencies when they cross the domain trunk.
- if more than 36 relationships are visible, compress dependencies into a gateway or split diagram.

## State Layout

Use lifecycle rows or columns:

- initial state;
- normal active states;
- blocked/exception states;
- terminal states.

Keep transition labels short:

- good: `publish`, `full`, `cancel`, `timeout`;
- bad: `教师关闭或时间截止后系统处理所有预约`.

If Chinese labels are long, expand state boxes and route transition labels away from nodes.

Coordinate defaults:

- canvas: `1300 x 1000`.
- state width: max of `160` and `14 * labelChars + 40`.
- state height: at least `70`.
- keep exception states in a side lane.
- keep terminal/final states at the far right or bottom.

Line budget:

- transition labels should be event/guard words, not full business sentences.
- labels over 12 Chinese characters must be shortened or moved to notes.
- no transition label may overlap another state box.
- use orthogonal routes for return/cancel transitions.

Baseline-aligned state layout:

- use 4-8 stable lifecycle states per object;
- place the normal lifecycle in a simple row or two-row rhythm;
- place cancellation, timeout, repair, scrap, and offline transitions on outer channels;
- use short labels such as `订单取消或超时`, `订单支付成功`, `办理借书`, `读者还书`, `检查正常`, `无法修复`;
- prefer readable separated labels over dense central routing;
- final state may be omitted from the visual center if terminal states are already explicit and the diagram remains valid for the assignment.

## Sequence Layout

Use stable participant order:

```text
Actor -> Boundary/Page -> Controller/Service -> Repository/Gateway -> DB/External
```

Keep lifeline gap wide enough for Chinese names.
Use fragments for branches. Do not encode all business logic as free-floating message text.

Coordinate defaults:

- participant order: Actor -> Boundary/Page -> Controller/Service -> Repository/Gateway -> DB/External.
- lifeline gap: at least `220` px; use `280` px when messages contain Chinese object names.
- header width: max of `130` and `12 * participantNameChars + 50`.
- message vertical gap: at least `54` px; branch frames add at least `80` px top/bottom padding.

Line budget:

- messages must connect visible lifelines.
- returns are shorter/dashed and should not carry core business text.
- `alt/else` frames must enclose the branch messages, not sit as a detached label.
- if the longest message cannot fit between adjacent lifelines, widen participants before export.

Baseline-aligned sequence layout:

- keep participant headers compact and evenly spaced;
- show visible sequence numbers;
- use activation bars when supported;
- keep `alt` fragments visually lightweight, but branch messages must stay inside or immediately adjacent to their branch;
- if StarUML's native fragment frame hurts readability, use clear numbered messages and branch guard labels rather than a large cluttered frame;
- never accept a Mermaid-imported sequence diagram as final without rerouting lifelines, messages, labels, and fragments.

## Communication Layout

- Place objects around a loose circle or layered collaboration path, not in a tight row.
- Put the initiating actor/object at upper left.
- Keep main numbered messages clockwise or left-to-right.
- Route return/secondary messages outside the object ring.
- Message labels must include visible sequence numbers such as `1`, `1.1`, `2`.

## Activity Layout

- Use vertical lanes when actors or subsystems matter.
- Put start node at top and final node at bottom.
- Place decisions with two clear outgoing routes and guard labels close to the diamond.
- Keep loops on the side; do not route loops through action labels.
- Action width must fit Chinese labels; use at least `220 x 70`.

## Repair Priority

Repair in this order:

1. clipped text;
2. line-through-label defects;
3. unreadable actor or class relationships;
4. missing grouping/layering;
5. excess decorative detail.
