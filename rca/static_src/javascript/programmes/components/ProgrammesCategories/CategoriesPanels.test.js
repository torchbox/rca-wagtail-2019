import React from 'react';
import { render } from '@testing-library/react';
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
        expect(testElement.getAttribute('aria-expanded')).toBe('true');
        expect(testElement.hasAttribute('hidden')).toBe(false);
        expect(test2Element.getAttribute('aria-expanded')).toBe('false');
        expect(test2Element.hasAttribute('hidden')).toBe(true);
    });
});
