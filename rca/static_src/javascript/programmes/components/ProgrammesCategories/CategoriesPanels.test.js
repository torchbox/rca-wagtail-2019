import React from 'react';
import { shallow } from 'enzyme';
import CategoriesPanels from './CategoriesPanels';

describe('CategoriesPanels', () => {
    it('empty', () => {
        expect(
            shallow(
                <CategoriesPanels
                    categories={[]}
                    activeCategory=""
                    isFullTime
                    isPartTime={false}
                />,
            ),
        ).toMatchInlineSnapshot(`
            <div
              className="categories-panels bg bg--light"
            />
        `);
    });

    it('categories are set to active with ARIA-attributes', () => {
        const wrapper = shallow(
            <CategoriesPanels
                categories={[
                    {
                        id: 'test',
                        title: 'Test title',
                        description: 'Test description',
                        items: [],
                    },
                    {
                        id: 'test2',
                        title: 'Test title 2',
                        description: 'Test description 2',
                        items: [],
                    },
                ]}
                activeCategory="test"
                isFullTime
                isPartTime={false}
            />,
        );
        expect(wrapper.find('#test').prop('aria-expanded')).toBe(true);
        expect(wrapper.find('#test').prop('hidden')).toBe(false);
        expect(wrapper.find('#test2').prop('aria-expanded')).toBe(false);
        expect(wrapper.find('#test2').prop('hidden')).toBe(true);
    });
});
