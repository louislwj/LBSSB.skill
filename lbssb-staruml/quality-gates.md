# Quality Gates

The final status is `Verified` only when the required gates pass. If a gate cannot be checked, use `Unverified: <reason>`.

## Universal

- StarUML delivery preflight passed when editable `.mdj` delivery is requested.
- Required `.mdj` exists when editable delivery is requested.
- Required PNGs exist and are non-empty.
- Manifest exists and records every PNG.
- Each PNG has readable text, visible lines, and no clipped key elements.
- Diagram titles match required business scenarios.
- Diagram type matches the business logic it claims to show.
- No source `.mdj` is modified directly.
- No silent fallback was used.

## StarUML MDJ Delivery Gate

Use this gate whenever the task promises editable StarUML output.

- `StarUML.exe` was launchable.
- `NODE_OPTIONS` was checked; Electron main process errors were diagnosed through `NODE_OPTIONS` first.
- Ports `58321` and `58322` were connectable before production work.
- A minimum test `.mdj` opened successfully in StarUML.
- A test diagram screenshot exported successfully through MCP/API.
- Production `.mdj` opens in StarUML.
- Diagram count matches the guide/requirements.
- Each diagram has its main expected elements.
- Each structural/interaction diagram has at least one expected relationship, edge, or message.
- Every required diagram can export PNG.
- Manifest records validation result for each diagram.
- Native objects were created through StarUML MCP/API, not direct `.mdj` JSON synthesis.

If any item fails, final status is `Failed: <reason>` or `Unverified: <reason>`, not `Verified`.

## PlantUML Fallback Gate

Use this gate when StarUML/MCP is unavailable.

- Outputs are labeled as `.puml`, PNG, and documentation only.
- No editable StarUML `.mdj` claim is made.
- Manifest records `deliveryBackend: plantuml-fallback`.
- Final summary states that StarUML native delivery was not verified.

## Use Case Diagram

- At least one external actor exists.
- Actor names are roles, not system modules.
- Use case names are business verb phrases.
- System boundary excludes external actors.
- `include` points to mandatory shared behavior.
- `extend` points from optional extension to base use case.
- Actor-use-case lines do not bury the main cluster.

## Class Diagram

- Domain model is visually central.
- Role inheritance is separate and readable.
- Class count and relationship count meet `class-diagram-rules.md`.
- Multiplicity labels exist on core associations.
- Composition/aggregation semantics are justified.
- No action-only classes.
- No isolated classes.
- Relationship lines do not cross title compartments.
- Core relationship completeness is at least 90%.

## Sequence Diagram

- Participants follow `Actor -> Page/Boundary -> Controller -> Service -> Repository -> DB` unless a documented reason exists.
- Messages are ordered top to bottom.
- Calls and returns are visually distinct.
- Branches use `alt/else` or equivalent frames/labels.
- Persistence work goes through Repository or Gateway.
- Self-calls are limited to validation, calculation, or state update.
- Long participant names fit in headers.

## Activity Diagram

- Has initial and final nodes.
- Main flow is readable in one direction.
- Decisions have guard labels.
- Parallel or alternative operations are branches, not serial steps.
- Merge/join points are explicit.
- Return loops do not cross action text.

## Communication Diagram

- Objects are named consistently with sequence/class diagrams.
- Every message has a visible number.
- Message numbering is continuous and understandable.
- Main collaboration path is not hidden by return lines.
- Branch messages have condition labels.
- Lines do not cover object names.

## State Diagram

- Models one object's lifecycle.
- Has initial state and stable terminal/final state when applicable.
- State names are lifecycle states, not operation steps.
- Transitions include events, guards, or triggers.
- Does not duplicate an activity diagram.

## Component Diagram

- Components are modules, services, adapters, databases, or external systems.
- Interfaces or dependencies show direction.
- UI, domain, application, infrastructure, and external boundaries are visible when relevant.
- Buttons, fields, or single use cases are not modeled as components.

## Deployment Diagram

- Nodes are runtime environments or devices.
- Artifacts/components are deployed to nodes.
- Network links are labeled when meaningful.
- Database/cache/message broker nodes are explicit if used.
- Entity classes are not modeled as deployment nodes.

## Manifest Gate

Each record must include:

```json
{
  "file": "",
  "diagramTitle": "",
  "type": "",
  "source": "staruml-export | draw_from_plan | normalized | plantuml-fallback",
  "mdjDiagram": "",
  "consistency": "native | semantic-consistent | unverified"
}
```

Compatibility rule:

- `source` may record the export route: `staruml-export`, `draw_from_plan`, or `normalized`.
- PlantUML fallback may record `source: plantuml-fallback` and must not use `consistency: native`.
- A consistency/source label must also record one of: `native`, `normalized`, `semantic-consistent`, or `unverified`.
- `draw_from_plan` output can be `semantic-consistent`; it is not proof that the native `.mdj` layout is equally optimized.
