import fixtures from '../../backend/elixirapp/tests/data/ResourceEditor.json';

// Expected wire fixture: labels remain in the original fixture used for draft/export assertions.
export const richSubmission = structuredClone(fixtures.rich);
const concepts = [...richSubmission.topic, ...richSubmission.function.flatMap(annotation => [
  ...annotation.operation,
  ...[...(annotation.input || []), ...(annotation.output || [])].flatMap(io => [io.data, ...(io.format || [])]),
])];
for (const concept of concepts) Reflect.deleteProperty(concept, 'term');
