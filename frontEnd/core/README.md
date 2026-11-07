# LuHmOS Tier-0 JavaScript Canon library

**Source-only candidate.** No new LLM provider, agent runtime, file server, deployment, payment, or authority.

This `namespaceCanon.mjs` module implements the existing `doctrine/namingNamespaceCanonV1.json` four-step machine-to-human projection:

1. `machineSqlDragonTail` = `OPERATION_TITAN` (uppercase machine/SQL namespace).
2. `repositoryKebabNamespace` = `operation-titan` (transport).
3. `vowelRippedStrictCamelHump` = `oprtTtn` (registered shorthand).
4. `fullHumanCenteredCamelHump` = `operationTitan` (full canonical identity).

Canonical JSON/JS object names remain `camelHump`. `DRAGONTAIL` is an uppercase machine-state and SQL projection, not a license to rewrite current JS keys. Names recover identity **only**, never permissions.

```js
import { createNamespaceRegistry, reconcileSourceEvidence } from "./namespaceCanon.mjs";
const registry = createNamespaceRegistry([{
  machineSqlDragonTail: "OPERATION_TITAN",
  repositoryKebabNamespace: "operation-titan",
  vowelRippedStrictCamelHump: "oprtTtn",
  fullHumanCenteredCamelHump: "operationTitan"
}]);
registry.resolve("OPERATION_TITAN").fullHumanCenteredCamelHump; // "operationTitan"
```

The registry fails closed on undeclared names, unknown aliases, invalid namespace spelling and alias collisions. No fuzzy dispatch. `reconcileSourceEvidence` requires exact 40-hex SHA, taskId, scopeId, a unique camelHump checkId and a matching evidenceRef. Empty or stale evidence is `AMBER`, matching explicit failure is `RED`, all matching source-only proof yields only `GREEN_SOURCE_ONLY` with `runtime: "UNVERIFIED"` and `crown: "STOP"`.

### Architectural compatibility

Follows `doctrine/luHmOSFourLayerArchitectureV1.json` Tier 0. Existing cockpit jQuery modules, optional Vue layer, Godot, Python task router, SQL, and MCP adapters remain higher and **unchanged**. This module is not auto-mounted in the live UI; its unit tests extend `npm run check`. Source-evidence records are caller-provided observations, **not cryptographically authenticated**; GitHub CI and actual provider receipts must be independently verified before any external assertion of GREEN.

The 15-agent operational quarantine, Professor promotion, private artwork boundaries and CAST release rules remain unchanged. This library never calls a provider or starts an agent.
