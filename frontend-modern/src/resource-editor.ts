import { resourceContract } from '../../backend/elixir/resource-contract.generated';

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type Field = {
  kind: string; required: boolean; readOnly: boolean; nullable: boolean;
  empty?: boolean; blank?: boolean; fields?: Record<string, Field>; item?: Field;
  path?: string; label?: string; help?: string; writable?: boolean; public?: boolean;
  choices?: { value: string; label: string }[]; itemLabel?: string; multiline?: boolean;
  minLength?: number; maxLength?: number; minimum?: number; maximum?: number;
};
export type ResourceSchema = { protocol: number; revision: string; contract: Field };
export function supportedSchema(schema: ResourceSchema | null | undefined, revision: string | null | undefined): boolean {
  function supported(field: Field): boolean {
    if (!field || !['required', 'nullable', 'readOnly'].every(key => typeof field[key as keyof Field] === 'boolean')) return false;
    if (field.kind === 'object') return !!field.fields && Object.values(field.fields).every(supported);
    if (field.kind === 'array') return !!field.item && field.item.kind !== 'array' && supported(field.item);
    return ['string', 'number', 'boolean'].includes(field.kind);
  }
  return schema?.protocol === 1 && !!revision && schema.revision === revision && schema.contract?.kind === 'object' && supported(schema.contract);
}
type FieldValue<F> = F extends { kind: 'object'; fields: infer P }
  ? { -readonly [K in keyof P]?: FieldValue<P[K]> } | null
  : F extends { kind: 'array'; item: infer I } ? FieldValue<I>[] | null
  : F extends { kind: 'number' } ? number | null
  : F extends { kind: 'boolean' } ? boolean | null : string | null;

// Drafts may be incomplete; validity is established by the backend, not these types.
export type Resource = NonNullable<FieldValue<typeof resourceContract>>;
export type EditorItem<T> = { readonly id: string; value: EditorValue<T> };
export type EditorValue<T> = T extends (infer I)[] ? EditorItem<I>[]
  : T extends object ? { [K in keyof T]: EditorValue<T[K]> } : T;
type ResourceValue<T> = T extends { id: string; value: infer V }[] ? ResourceValue<V>[]
  : T extends object ? { [K in keyof T]: ResourceValue<T[K]> } : T;
export type ResourceEditor = EditorValue<Resource>;
export type EditorPath = readonly (string | { readonly itemId: string })[];
type WirePath = readonly (string | number)[];
export type ContractNotice = { path: EditorPath; reason: string };
export type Submission = {
  readonly payload: Readonly<Record<string, Json>>;
  readonly paths: Readonly<Record<string, EditorPath>>;
  readonly normalizations: readonly ContractNotice[];
  readonly blockers: readonly ContractNotice[];
};
export type EditorError = { path: EditorPath | null; wirePath: WirePath; message: string };

function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

/** Check only the shapes needed by the form; the server validates field values on save. */
export function editorShapeError(value: unknown, contract?: Field): string | null {
  if (!isObject(value)) return 'The JSON record must be an object.';
  if (Object.hasOwn(value, '__proto__')) return 'The JSON record contains an unsupported field: __proto__.';
  function check(item: unknown, field: Field, path: string): string | null {
    if (item === null) return null;
    if (field.kind === 'object') {
      if (!isObject(item)) return `${path} must be an object.`;
      for (const [name, child] of Object.entries(item)) {
        const childField = field.fields && Object.hasOwn(field.fields, name) ? field.fields[name] : undefined;
        if (childField) {
          const error = check(child, childField, path ? `${path}.${name}` : name);
          if (error) return error;
        }
      }
    } else if (field.kind === 'array') {
      if (!Array.isArray(item)) return `${path} must be a list.`;
      if (field.item) for (const [index, child] of item.entries()) {
        const error = check(child, field.item, `${path}[${index}]`);
        if (error) return error;
      }
    } else if (field.kind === 'number' ? typeof item !== 'number' || !Number.isFinite(item) : typeof item !== field.kind) {
      return `${path} must be ${field.kind === 'string' ? 'text' : `a ${field.kind}`}.`;
    }
    return null;
  }
  return contract ? check(value, contract, '') : null;
}

function load(value: unknown, ancestors = new Set<unknown>()): unknown {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value !== 'object' || ancestors.has(value)) throw new TypeError('Expected acyclic JSON data.');
  ancestors.add(value);
  let result: unknown;
  if (Array.isArray(value)) {
    // Array.from visits sparse slots too: never silently turn undefined into null.
    result = Array.from(value, item => ({ id: crypto.randomUUID(), value: load(item, ancestors) }));
  } else {
    if (Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) {
      throw new TypeError('Expected a plain JSON object.');
    }
    result = Object.fromEntries(Object.entries(value!).map(([key, child]) => [key, load(child, ancestors)]));
  }
  ancestors.delete(value);
  return result;
}

export function resourceToEditor<T extends object>(resource: T): EditorValue<T> {
  if (!isObject(resource)) throw new TypeError('Expected a resource object.');
  return load(resource) as EditorValue<T>;
}

export function newEditorItem<T>(value: T): EditorItem<T> {
  return { id: crypto.randomUUID(), value: load(value) as EditorValue<T> };
}

function encode(value: unknown, ids: Set<string>, paths: Record<string, EditorPath>,
                wire: WirePath = [], path: EditorPath = [], ancestors = new Set<unknown>()): Json {
  paths[JSON.stringify(wire)] = path;
  if (value !== null && typeof value === 'object') {
    if (ancestors.has(value)) throw new TypeError('Expected acyclic JSON data.');
    ancestors.add(value);
  }
  if (Array.isArray(value)) {
    const result = Array.from(value, (item, index) => {
      if (!isObject(item) || typeof item.id !== 'string' || !item.id || ids.has(item.id)) {
        throw new TypeError('Repeated items require unique client IDs.');
      }
      ids.add(item.id);
      return encode(item.value, ids, paths, [...wire, index], [...path, { itemId: item.id }], ancestors);
    });
    ancestors.delete(value);
    return result;
  }
  if (isObject(value)) {
    if (Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) {
      throw new TypeError('Expected a plain JSON object.');
    }
    const result = Object.fromEntries(Object.entries(value).map(([key, child]) =>
      [key, encode(child, ids, paths, [...wire, key], [...path, key], ancestors)]));
    ancestors.delete(value);
    return result;
  }
  if (value === null || typeof value === 'string' || typeof value === 'boolean'
      || (typeof value === 'number' && Number.isFinite(value))) return value;
  throw new TypeError('Expected JSON data; delete absent properties instead of assigning undefined.');
}

/** Lossless local export, including server metadata and unknown fields. No cleanup. */
export function editorToResource<T extends object>(editor: T): ResourceValue<T> {
  return encode(editor, new Set(), {}) as ResourceValue<T>;
}

function freeze<T>(value: T): T {
  if (value !== null && typeof value === 'object') {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}

/** Capture once, send payload unchanged, and map the response with this same snapshot. */
export function editorToSubmission(editor: object, contract: Field = resourceContract): Submission {
  const paths: Record<string, EditorPath> = {};
  const payload = encode(editor, new Set(), paths) as Record<string, Json>;
  const normalizations: ContractNotice[] = [];
  const blockers: ContractNotice[] = [];
  function prepare(value: Json, field: Field, wire: WirePath = []): void {
    if (Array.isArray(value) && field.item) {
      value.forEach((item, index) => prepare(item, field.choices ? { ...field.item!, choices: field.choices } : field.item!, [...wire, index]));
    } else if (isObject(value) && field.fields) {
      // EDAM labels can change independently of the stored URI; resolve them on the server.
      if (typeof value.uri === 'string' && /^http:\/\/edamontology\.org\/(topic|operation|data|format)_[0-9]{4}$/.test(value.uri)
          && field.fields.uri && field.fields.term && !field.fields.term.readOnly && field.fields.term.writable !== false
          && (typeof value.term === 'string' || value.term === null)) {
        delete value.term;
        normalizations.push({ path: paths[JSON.stringify([...wire, 'term'])], reason: 'edam-label-from-uri' });
      }
      for (const [key, child] of Object.entries(value)) {
        const childWire = [...wire, key];
        const path = paths[JSON.stringify(childWire)];
        const policy = Object.hasOwn(field.fields, key) ? field.fields[key] : undefined;
        if (!policy) {
          blockers.push({ path, reason: 'unsupported-field' });
        } else if (policy.readOnly) {
          // Preserve authoritative values; the server rejects forged enrichment.
          continue;
        } else if (!policy.required && ((child === null && !policy.nullable)
            || (Array.isArray(child) && child.length === 0 && policy.empty === false))) {
          delete value[key];
          normalizations.push({ path, reason: child === null ? 'optional-null-to-absent' : 'optional-empty-list-to-absent' });
        } else {
          prepare(child as Json, policy, childWire);
        }
      }
    } else if (value !== null && field.choices && !field.choices.some(choice => choice.value === value)) {
      blockers.push({ path: paths[JSON.stringify(wire)], reason: 'removed-choice' });
    }
  }
  prepare(payload, contract);
  return freeze({ payload, paths, normalizations, blockers });
}

function locate(snapshot: Submission, wire: WirePath): EditorPath | null {
  // Missing field errors still have a location; nonexistent array indices do not.
  for (let length = wire.length; length >= 0; length--) {
    const prefix = snapshot.paths[JSON.stringify(wire.slice(0, length))];
    const rest = wire.slice(length);
    if (prefix && rest.every(part => typeof part === 'string')) return [...prefix, ...rest as string[]];
  }
  return null;
}

/** Supports DRF nested dictionaries/lists, numeric-key dictionaries and general_errors. */
export function backendErrorsToEditor(errors: unknown, snapshot: Submission): EditorError[] {
  const result: EditorError[] = [];
  function visit(value: unknown, wire: WirePath): void {
    if (typeof value === 'string') {
      result.push({ path: locate(snapshot, wire), wirePath: wire, message: value });
    } else if (Array.isArray(value)) {
      // Scalar arrays are messages for one field, not repeated resource items.
      value.forEach((child, index) => visit(child, typeof child === 'string' ? wire : [...wire, index]));
    } else if (isObject(value)) {
      for (const [key, child] of Object.entries(value)) {
        const next = key === 'general_errors' || key === 'non_field_errors' || (key === 'detail' && !wire.length)
          ? wire : [...wire, /^(0|[1-9][0-9]*)$/.test(key) ? Number(key) : key];
        visit(child, next);
      }
    }
  }
  visit(errors, []);
  return result;
}

/** Resolve by ID in the current draft. Removed items never fall back to an array index. */
export function currentEditorPath(editor: ResourceEditor, path: EditorPath): (string | number)[] | null {
  let value: unknown = editor;
  const result: (string | number)[] = [];
  for (const part of path) {
    if (typeof part === 'string') {
      if (!isObject(value)) return null;
      result.push(part);
      value = value[part];
    } else {
      if (!Array.isArray(value)) return null;
      const index = value.findIndex(item => item.id === part.itemId);
      if (index < 0) return null;
      result.push(index, 'value');
      value = value[index].value;
    }
  }
  return result;
}
