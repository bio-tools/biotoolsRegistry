export interface Term { uri: string | null; term: string | null }
export interface IO { id: string; data: Term | null; formats: Term[] }
export interface FunctionSnapshot {
  id: string; token: string; operations: Term[]; input: IO[]; output: IO[];
}
export interface Step {
  id: string; resource: { id: string; name: string; revision: { token: string } };
  function: FunctionSnapshot; note: string; schemaRevision: string; vocabularyRevisions: Record<string, string>;
  selection: { direction: 'input' | 'output'; ioId: string | null; fingerprint: string;
    evidence: Record<string, { state: string; relation?: string; reasons?: string[]; obsolete?: boolean }> };
}
export interface Endpoint { step: string; io: string }
export interface Connection { id: string; from: Endpoint; to: Endpoint; evidence: 'exact' | 'related' | 'unknown' | 'conflict'; reason: string;
  dimensions?: Record<string, { state: string; relation?: string; reasons?: string[] }>;
  schemaRevision?: string; vocabularyRevisions?: Record<string, string> }
export interface Graph { version: 1; steps: Step[]; connections: Connection[] }

export function readDraft(text: string): Graph {
  if (text.length > 1_000_000) throw new Error('The draft is too large.');
  const data = JSON.parse(text);
  const isText = (value: unknown) => typeof value === 'string' && value.length <= 1000 && !/[\uD800-\uDFFF]/u.test(value);
  const term = (value: any) => value && (value.uri === null || isText(value.uri)) && (value.term === null || isText(value.term));
  const ios = (value: any) => Array.isArray(value) && value.length <= 200 &&
    new Set(value.map(io => io?.id)).size === value.length && value.every(io => io && isText(io.id) && io.id &&
      (io.data === null || term(io.data)) && Array.isArray(io.formats) && io.formats.length <= 200 && io.formats.every(term));
  if (!data || data.version !== 1 || !Array.isArray(data.steps) || data.steps.length > 100 ||
      !Array.isArray(data.connections) || data.connections.length > 300) throw new Error('Unsupported or invalid draft.');
  const ids = new Set<string>();
  for (const step of data.steps) {
    // Earlier prototype exports lack these fields; keep them as unresolved snapshots.
    if (step && typeof step === 'object') {
      if (step.schemaRevision === undefined) step.schemaRevision = '';
      if (step.vocabularyRevisions === undefined) step.vocabularyRevisions = {};
      if (step.selection === undefined) step.selection = { direction: 'input', ioId: null, fingerprint: '', evidence: {} };
    }
    if (!step || !isText(step.id) || !step.id || ids.has(step.id) || !isText(step.note) || !step.resource ||
        !isText(step.resource.id) || !isText(step.resource.name) || !isText(step.resource.revision?.token) ||
        !isText(step.schemaRevision) || !step.vocabularyRevisions || typeof step.vocabularyRevisions !== 'object' ||
        Array.isArray(step.vocabularyRevisions) || Object.keys(step.vocabularyRevisions).some(key =>
          !['data', 'format', 'operation'].includes(key) || !isText(step.vocabularyRevisions[key])) ||
        !step.selection || !['input', 'output'].includes(step.selection.direction) ||
        !(step.selection.ioId === null || (isText(step.selection.ioId) && step.selection.ioId)) || !isText(step.selection.fingerprint) ||
        !step.selection.evidence || typeof step.selection.evidence !== 'object' || Array.isArray(step.selection.evidence) ||
        Object.keys(step.selection.evidence).some(key => !['data', 'format', 'operation'].includes(key) ||
          !['exact', 'related', 'unknown', 'conflict', 'not_requested'].includes(step.selection.evidence[key]?.state) ||
          (step.selection.evidence[key].relation !== undefined && !isText(step.selection.evidence[key].relation)) ||
          (step.selection.evidence[key].reasons !== undefined && (!Array.isArray(step.selection.evidence[key].reasons) ||
            step.selection.evidence[key].reasons.length > 10 || !step.selection.evidence[key].reasons.every(isText))) ||
          (step.selection.evidence[key].obsolete !== undefined && typeof step.selection.evidence[key].obsolete !== 'boolean')) ||
        !step.function || !isText(step.function.id) || !step.function.id || !isText(step.function.token) || !step.function.token ||
        !Array.isArray(step.function.operations) || step.function.operations.length > 200 ||
        !step.function.operations.every(term) || !ios(step.function.input) || !ios(step.function.output)) {
      throw new Error('The draft contains an invalid step.');
    }
    if (step.selection.ioId !== null && !step.function[step.selection.direction].some((io: IO) => io.id === step.selection.ioId)) {
      throw new Error('The selected annotation is missing from the step snapshot.');
    }
    ids.add(step.id);
  }
  const graph: Graph = { ...data, version: 1, steps: data.steps, connections: [] };
  const edgeIds = new Set<string>();
  for (const edge of data.connections) {
    if (!edge || !isText(edge.id) || !edge.id || edgeIds.has(edge.id) || !edge.from || !edge.to ||
        !isText(edge.from.step) || !isText(edge.from.io) || !isText(edge.to.step) || !isText(edge.to.io) || !isText(edge.reason)) {
      throw new Error('The draft contains an invalid connection.');
    }
    const checked = connect(graph, edge.from, edge.to, edge.reason, edge.id);
    if (!['exact', 'related', 'unknown', 'conflict'].includes(edge.evidence) ||
        (edge.evidence === 'exact' && checked.evidence !== 'exact') || (edge.evidence !== 'exact' && !edge.reason.trim())) {
      throw new Error('The draft contains inconsistent connection evidence.');
    }
    if (edge.dimensions !== undefined && (!edge.dimensions || typeof edge.dimensions !== 'object' || Array.isArray(edge.dimensions) ||
        Object.keys(edge.dimensions).some(key => !['data', 'format'].includes(key) ||
          !['exact', 'related', 'unknown', 'conflict'].includes(edge.dimensions[key]?.state) ||
          (edge.dimensions[key].relation !== undefined && !isText(edge.dimensions[key].relation)) ||
          (edge.dimensions[key].reasons !== undefined && (!Array.isArray(edge.dimensions[key].reasons) ||
            edge.dimensions[key].reasons.length > 10 || !edge.dimensions[key].reasons.every(isText)))))) {
      throw new Error('The draft contains invalid connection details.');
    }
    if ((edge.schemaRevision !== undefined && !isText(edge.schemaRevision)) ||
        (edge.vocabularyRevisions !== undefined && (!edge.vocabularyRevisions || typeof edge.vocabularyRevisions !== 'object' ||
          Array.isArray(edge.vocabularyRevisions) || Object.keys(edge.vocabularyRevisions).some(key =>
            !['data', 'format'].includes(key) || !isText(edge.vocabularyRevisions[key]))))) {
      throw new Error('The draft contains invalid connection revisions.');
    }
    graph.connections.push({ ...edge, ...checked, evidence: edge.evidence });
    edgeIds.add(edge.id);
  }
  return graph;
}

export function connect(graph: Graph, from: Endpoint, to: Endpoint, reason: string, id: string): Connection {
  const source = graph.steps.find(step => step.id === from.step);
  const target = graph.steps.find(step => step.id === to.step);
  const output = source?.function.output.find(io => io.id === from.io);
  const input = target?.function.input.find(io => io.id === to.io);
  if (!output || !input || from.step === to.step) throw new Error('Choose an output and an input on different steps.');
  if (graph.connections.some(edge => edge.from.step === from.step && edge.from.io === from.io &&
      edge.to.step === to.step && edge.to.io === to.io)) throw new Error('That connection already exists.');
  const seen = new Set<string>();
  const pending = [to.step];
  while (pending.length) {
    const current = pending.pop()!;
    if (current === from.step) throw new Error('This connection would create a cycle.');
    if (seen.has(current)) continue;
    seen.add(current);
    pending.push(...graph.connections.filter(edge => edge.from.step === current).map(edge => edge.to.step));
  }
  const exactData = !!output.data?.uri && output.data.uri === input.data?.uri;
  const exactFormat = output.formats.some(format => !!format.uri && input.formats.some(other => other.uri === format.uri));
  const evidence = exactData && exactFormat ? 'exact' : 'unknown';
  if (evidence === 'unknown' && !reason.trim()) throw new Error('Explain why you want to connect these annotations.');
  return { id, from, to, evidence, reason: reason.trim() };
}
