import { editorToResource, resourceToEditor, type Json, type ResourceEditor } from './resource-editor';

export function identity(value: Json): string {
  if (Array.isArray(value)) return '[' + value.map(identity).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + identity(value[key])).join(',') + '}';
  return JSON.stringify(value);
}

export function mergeSuggestions(current: Json[], selected: Json[]): Json[] {
  const result = [...current];
  for (const item of selected) if (!result.some(existing => identity(existing) === identity(item))) result.push(item);
  return result;
}

export function applySuggestions(draft: ResourceEditor, changes: Record<string, Json>) {
  const before = editorToResource(draft) as Record<string, Json>;
  const converted = resourceToEditor(changes) as Record<string, unknown>;
  for (const [key, value] of Object.entries(changes)) {
    const old = (draft as Record<string, unknown>)[key];
    const previous = before[key];
    if (Array.isArray(value) && Array.isArray(previous) && Array.isArray(old)) {
      const available = previous.map((item, index) => ({ item, editor: old[index], used: false }));
      converted[key] = (converted[key] as unknown[]).map((item, index) => {
        const match = available.find(entry => !entry.used && identity(entry.item) === identity(value[index]));
        if (match) { match.used = true; return match.editor; }
        return item;
      });
    }
  }
  Object.assign(draft, converted);
}
