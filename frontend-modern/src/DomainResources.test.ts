import { expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import DomainResources from './DomainResources.vue';

it('finds and removes a member while retaining the rest of the draft', async () => {
  const wrapper = mount(DomainResources, { props: { initial: ['alpha', 'beta', 'gamma'], names: { beta: 'Sequence viewer' } } });
  await wrapper.get('#domain-resource-filter').setValue('sequence');
  expect(wrapper.findAll('li')).toHaveLength(1);
  await wrapper.get('[aria-label="Remove beta"]').trigger('click');
  expect((wrapper.get('input[name="resources"]').element as HTMLInputElement).value).toBe('alpha\ngamma');
  await wrapper.get('#domain-resource-add').setValue('delta');
  await wrapper.get('#domain-resource-add').trigger('keydown.enter');
  expect((wrapper.get('input[name="resources"]').element as HTMLInputElement).value).toBe('alpha\ngamma\ndelta');
  wrapper.unmount();
});
