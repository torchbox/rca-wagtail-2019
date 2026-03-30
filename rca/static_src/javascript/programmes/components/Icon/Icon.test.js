import React from 'react';
import { render } from '@testing-library/react';
import Icon from './Icon';

describe('Icon', () => {
    it('renders', () => {
        const { container } = render(<Icon name="rocket" />);
        expect(container).toMatchSnapshot();
    });

    it('#className', () => {
        const { container } = render(
            <Icon name="rocket" className="button__icon" />,
        );
        expect(container).toMatchSnapshot();
    });

    it('#width and #height', () => {
        const { container } = render(
            <Icon name="rocket" width="12px" height="8px" />,
        );
        expect(container).toMatchSnapshot();
    });
});
