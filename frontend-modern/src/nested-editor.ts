import { currentEditorPath, type EditorError, type EditorPath, type ResourceEditor } from './resource-editor';

export type FunctionItem = NonNullable<ResourceEditor['function']>[number];
export type FunctionValue = NonNullable<FunctionItem['value']>;
export type IOItem = NonNullable<FunctionValue['input']>[number];
export type ConceptItem = NonNullable<FunctionValue['operation']>[number];
export type Concept = NonNullable<ConceptItem['value']>;

export function fieldId(path: EditorPath): string {
  return 'nested-' + path.map(part => typeof part === 'string' ? part : part.itemId).join('-');
}

export function errorsAt(errors: EditorError[], path: EditorPath, descendants = false): string[] {
  return errors.filter(error => error.path && (descendants || error.path.length === path.length)
    && path.every((part, index) => JSON.stringify(part) === JSON.stringify(error.path![index])))
    .map(error => error.message);
}

export function nestedTarget(editor: ResourceEditor, error: EditorError): string | null {
  if (!error.path || !currentEditorPath(editor, error.path)) return null;
  const path = [...error.path];
  if (['uri', 'term'].includes(String(path.at(-1)))) path.pop();
  return fieldId(path);
}

export function errorLocation(editor: ResourceEditor, error: EditorError): string {
  if (!error.path?.length) return error.wirePath.join('.');
  const path = currentEditorPath(editor, error.path);
  return path ? path.filter((part, index) => part !== 'value' || typeof path[index - 1] !== 'number').map(part => typeof part === 'number' ? part + 1 : part).join(' / ')
    : 'Removed item (submitted ' + error.wirePath.join('.') + ')';
}

export function moveItem<T>(items: T[], index: number, direction: number): void {
  const target = index + direction;
  if (target >= 0 && target < items.length) [items[index], items[target]] = [items[target], items[index]];
}

function populated(value: unknown): boolean {
  if (Array.isArray(value)) return value.some(item => populated(item.value));
  if (value && typeof value === 'object') return Object.values(value).some(populated);
  return value !== null && value !== undefined && value !== '';
}

export function removeSection<T extends { value: unknown }>(items: T[], index: number, label: string): void {
  if (!populated(items[index].value) || window.confirm(`Remove ${label} and its annotations?`)) items.splice(index, 1);
}

export function conceptURIs(concept: Concept | null | undefined): string[] {
  return concept?.uri ? [concept.uri] : [];
}

export function selectConcept(current: Concept | null | undefined, uris: string[]): Concept {
  if (current?.uri && current.uri === uris[0]) return current;
  const result = { ...current };
  delete result.uri;
  delete result.term;
  if (uris[0]) result.uri = uris[0];
  return result;
}
