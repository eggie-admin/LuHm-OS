/** Offline, read-only K9000 orchestration primitives. No network or model imports. */
export const quarters = Object.freeze(["local", "remote", "studio", "company"]);
export const layers = Object.freeze([
  "coreLibrary", "pluginExtension", "classWidgetOrganization", "stubAdapterBoundary"
]);
export const beats = Object.freeze(["hear", "resolve", "act", "verify"]);
export const owners = Object.freeze({
  hear: "lum",
  resolve: "skuldResearch",
  act: "kaji",
  verify: "belldandySecretary"
});
const roles = Object.freeze(["lum", "skuldResearch", "tetsu", "kaji", "yume", "belldandySecretary"]);

function requiredOneOf(value, values, type) {
  if (typeof value !== "string" || !values.includes(value)) {
    throw new TypeError(`UNREGISTERED_${type.toUpperCase()}`);
  }
  return value;
}

export class GoddessOrchestra {
  constructor() {
    this.authority = "NONE";
    this.workerCount = 0;
    Object.freeze(this);
  }

  plan(quarter, layer, beat) {
    requiredOneOf(quarter, quarters, "quarter");
    requiredOneOf(layer, layers, "layer");
    requiredOneOf(beat, beats, "beat");
    return Object.freeze({
      schema: "luhmOs.unifiedGoddessOrchestraPlan.v1",
      quarter, layer, beat,
      ownerRole: owners[beat],
      roster: [...roles],
      evidenceReviewer: "urdDoctorGoddess",
      sourceRef: null,
      scopeId: null,
      authority: "NONE",
      executionEnabled: false,
      runtimeProven: false,
      consent: "NOT_REQUESTED",
      costBudget: 0,
      crown: "STOP"
    });
  }

  matrix() {
    return quarters.flatMap(q =>
      layers.flatMap(l => beats.map(b => this.plan(q, l, b)))
    );
  }

  song() {
    return beats.map(beat => Object.freeze({
      beat,
      role: owners[beat],
      roleAuthority: "PLAN_ONLY_QUARANTINED",
      canStartWorker: false,
      independentReview: beat === "verify" ? "urdDoctorGoddess" : null
    }));
  }
}
