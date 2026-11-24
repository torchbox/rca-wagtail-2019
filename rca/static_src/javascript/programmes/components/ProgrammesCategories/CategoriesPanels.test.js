import { render } from '@testing-library/react';
import React from 'react';
import CategoriesPanels from './CategoriesPanels';

describe('CategoriesPanels', () => {
    it('empty', () => {
        const { container } = render(
            <CategoriesPanels
                categories={[]}
                activeCategory=""
                isFullTime
                isPartTime={false}
            />,
        );
        expect(container).toMatchSnapshot();
    });

    it('categories are set to active with ARIA-attributes', () => {
        const { container } = render(
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
        const testElement = container.querySelector('#test');
        const test2Element = container.querySelector('#test2');
        expect(testElement.getAttribute('role')).toBe('tabpanel');
        expect(testElement.hasAttribute('hidden')).toBe(false);
        expect(test2Element.getAttribute('role')).toBe('tabpanel');
        expect(test2Element.hasAttribute('hidden')).toBe(true);
    });
});
