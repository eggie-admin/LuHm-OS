/** Deterministic 1->2->4 plan, no scheduler or live workers. */
export function workflowPlan({threads=2, tasks=[]}={}) {
  if (![1,2,4].includes(threads)) throw new Error("INVALID_THREAD_COUNT");
  if (!Array.isArray(tasks) || tasks.length>16) throw new Error("INVALID_TASKS");
  if (tasks.some(t=>typeof t!=="string" || !/^[a-zA-Z0-9_-]{1,48}$/.test(t))) throw new Error("INVALID_TASK");
  return Object.freeze({schema:"luhmOs.workflowPlan.v1", threads, tasks:[...tasks],
    execution:"SOURCE_ONLY", remoteCommands:false, crown:"STOP"});
}
