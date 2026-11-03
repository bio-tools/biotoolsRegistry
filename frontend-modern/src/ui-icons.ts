const sections: Record<string, string> = {
  function: 'function', publication: 'publication', documentation: 'publication',
  download: 'download', link: 'link', relation: 'link', credit: 'people',
  topic: 'topic', editPermission: 'lock',
};

export function fieldIcon(kind?: string, hasChoices = false): string {
  if (hasChoices) return 'choice';
  return ['string', 'number', 'boolean', 'array', 'object'].includes(kind || '') ? kind! : 'object';
}

export function sectionIcon(path?: string, kind?: string): string {
  return path && Object.prototype.hasOwnProperty.call(sections, path) ? sections[path]! : fieldIcon(kind);
}
