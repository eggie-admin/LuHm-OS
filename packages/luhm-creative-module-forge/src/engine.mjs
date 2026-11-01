/** LuHm original RPG: bounded JSON scene DSL. No eval, dynamic code or I/O. */
const ID = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const DICE = /^([1-9][0-9]?)d(4|6|8|10|12|20|100)([+-](?:0|[1-9][0-9]?))?$/;
const ALLOWED_EFFECTS = new Set(["grant", "none"]);
const ALLOWED_NODES = new Set(["dialogue", "encounter", "ending"]);
const SCHEMA = "luhmOs.rpgModule.v1";

function ensure(condition, code) {
  if (!condition) throw new TypeError(code);
}
function slug(value) {
  ensure(typeof value === "string" && value.length <= 48 && ID.test(value)
    && !["__proto__", "constructor", "prototype"].includes(value), "RED_RPG_SLUG");
  return value;
}
function text(value, limit=240) {
  ensure(typeof value === "string" && value.length >= 1 && value.length <= limit
    && !/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(value), "RED_RPG_TEXT");
  return value;
}
function ownKeys(value, allowed, error) {
  ensure(value && typeof value === "object" && !Array.isArray(value)
    && Object.keys(value).every(key => allowed.includes(key)), error);
}
function rollFormula(expr) {
  ensure(typeof expr === "string" && expr.length <= 12, "RED_DICE_FORMULA");
  const match = DICE.exec(expr);
  ensure(match, "RED_DICE_FORMULA");
  const count = Number(match[1]), sides = Number(match[2]);
  ensure(count >= 1 && count <= 20 && count * sides <= 2000, "RED_DICE_BUDGET");
  const modifier = match[3] ? Number(match[3]) : 0;
  return {count, sides, modifier};
}
function nextSeed(seed) {
  const next = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
  return next;
}
export function rollDice(formula, seed=1) {
  const {count, sides, modifier} = rollFormula(formula);
  ensure(Number.isInteger(seed) && seed >= 0 && seed <= 0xffffffff, "RED_RPG_SEED");
  let state = seed >>> 0, subtotal = 0;
  const faces = [];
  for (let i=0; i<count; i++) {
    state = nextSeed(state);
    const face = (state % sides) + 1;
    faces.push(face);
    subtotal += face;
  }
  return {formula, faces, total: subtotal + modifier, nextSeed:state,
    status:"SYNTHETIC_DETERMINISTIC_ROLL_NOT_FAIR_RANDOM"};
}
export function validateModule(module) {
  ownKeys(module, ["schema","moduleId","title","rights","sourceRef","nodes","start"],
    "RED_RPG_MODULE_FIELDS");
  ensure(module.schema === SCHEMA, "RED_RPG_SCHEMA");
  const moduleId = slug(module.moduleId), title = text(module.title,96);
  ensure(module.rights === "originalOwned", "RED_RPG_RIGHTS");
  ensure(typeof module.sourceRef === "string" && /^[0-9a-f]{40}$/.test(module.sourceRef),
    "RED_RPG_SOURCE_ID");
  ensure(Array.isArray(module.nodes) && module.nodes.length >= 1 && module.nodes.length <= 32,
    "RED_RPG_NODE_COUNT");
  const nodes = new Map();
  for (const node of module.nodes) {
    ownKeys(node, ["id","type","text","choices"], "RED_RPG_NODE_FIELDS");
    const id=slug(node.id);
    ensure(!nodes.has(id), "RED_RPG_DUPLICATE_NODE");
    ensure(ALLOWED_NODES.has(node.type), "RED_RPG_NODE_TYPE");
    text(node.text,500);
    ensure(Array.isArray(node.choices) && node.choices.length <= 4
      && (node.type !== "ending" || node.choices.length === 0),
      "RED_RPG_CHOICES");
    for (const choice of node.choices) {
      ownKeys(choice, ["label","target","failureTarget","check","effect"], "RED_RPG_CHOICE_FIELDS");
      text(choice.label,96);slug(choice.target);
      if (Object.hasOwn(choice,"failureTarget")) {
        ensure(Object.hasOwn(choice,"check"), "RED_RPG_FAILURE_REQUIRES_CHECK");
        slug(choice.failureTarget);
      }
      if (Object.hasOwn(choice,"check")) {
        ownKeys(choice.check, ["formula","target"], "RED_RPG_CHECK_FIELDS");
        rollFormula(choice.check.formula);
        ensure(Number.isInteger(choice.check.target)
          && choice.check.target>=1 && choice.check.target<=100, "RED_RPG_DIFFICULTY");
      }
      if (Object.hasOwn(choice,"effect")) {
        ownKeys(choice.effect, ["type","resource","amount"], "RED_RPG_EFFECT_FIELDS");
        ensure(ALLOWED_EFFECTS.has(choice.effect.type), "RED_RPG_EFFECT_TYPE");
        if (choice.effect.type === "grant") {
          slug(choice.effect.resource);
          ensure(Number.isInteger(choice.effect.amount)
            && choice.effect.amount >= 1 && choice.effect.amount <= 10,
            "RED_RPG_EFFECT_BUDGET");
        } else {
          ensure(!Object.hasOwn(choice.effect,"resource")
            && !Object.hasOwn(choice.effect,"amount"), "RED_RPG_EFFECT_NONE");
        }
      }
    }
    nodes.set(id,node);
  }
  ensure(nodes.has(slug(module.start)), "RED_RPG_START");
  for(const node of nodes.values())for(const choice of node.choices) {
    ensure(nodes.has(choice.target), "RED_RPG_MISSING_TARGET");
    if (Object.hasOwn(choice,"failureTarget")) {
      ensure(nodes.has(choice.failureTarget), "RED_RPG_MISSING_FAILURE_TARGET");
    }
  }
  const summary = {schema:SCHEMA,moduleId,title,nodeCount:nodes.size,
    start:module.start,sourceRef:module.sourceRef,
    rights:"originalOwned",validatedStructure:true,
    distributionApproved:false,externalArtApproved:false};
  return Object.freeze(summary);
}
export function createModule(moduleId="moonlit-archive", sourceRef="0".repeat(40)) {
  slug(moduleId);
  ensure(typeof sourceRef==="string" && /^[0-9a-f]{40}$/.test(sourceRef),
    "RED_RPG_SOURCE_ID");
  return {
    schema:SCHEMA,moduleId,title:"Moonlit Archive",rights:"originalOwned",sourceRef,
    start:"gate",nodes:[
      {id:"gate",type:"dialogue",text:"A silver bell echoes over an abandoned observatory.",choices:[
        {label:"Examine the observatory seal",target:"vault",
          check:{formula:"1d20+2",target:12},failureTarget:"rest"},
        {label:"Rest beside the lantern",target:"rest",
          effect:{type:"grant",resource:"focus",amount:1}}
      ]},
      {id:"vault",type:"encounter",text:"A clockwork sentinel guards a sealed archive.",choices:[
        {label:"Stand down and review the ward",target:"ending"}
      ]},
      {id:"rest",type:"dialogue",text:"The lantern warms and reveals an alternate route.",choices:[
        {label:"Continue into the archive",target:"ending"}
      ]},
      {id:"ending",type:"ending",text:"The archive opens. Further scenes remain to be authored.",choices:[]}
    ]
  };
}
export function step(module, nodeId, choiceIndex, seed=1) {
  validateModule(module);
  slug(nodeId);
  ensure(Number.isInteger(choiceIndex) && choiceIndex>=0, "RED_RPG_CHOICE_INDEX");
  const node=module.nodes.find(x=>x.id===nodeId);
  ensure(node, "RED_RPG_CURRENT_NODE");
  const choice=node.choices[choiceIndex];
  ensure(choice, "RED_RPG_CHOICE_INDEX");
  const dice=choice.check?rollDice(choice.check.formula,seed):null;
  const success=dice ? dice.total>=choice.check.target : true;
  return Object.freeze({moduleId:module.moduleId,from:nodeId,
    to:!success && choice.failureTarget ? choice.failureTarget : choice.target,
    choice:choice.label,check:dice?{...dice,target:choice.check.target,success}:null,
    effect:success&&choice.effect?{...choice.effect}:null,
    sourceOnly:true,networkCalls:0,pluginCalls:0,writeCalls:0,
    productionGameProven:false});
}
