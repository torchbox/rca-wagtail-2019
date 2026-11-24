import { render } from '@testing-library/react';
import React from 'react';
import { StudyModeContext } from '../context/StudyModeContext';
import ModeCheckbox from './StudyModeCheckbox';

const renderModeCheckbox = (contextValue) =>
    render(
        <StudyModeContext.Provider value={contextValue}>
            <ModeCheckbox ariaLabel="Study mode" />
        </StudyModeContext.Provider>,
    );

describe('StudyModeCheckbox', () => {
    it('exposes a group role and the given label for assistive tech', () => {
        const { container } = renderModeCheckbox({
            isFullTime: 'false',
            setIsFullTime: jest.fn(),
            isPartTime: 'false',
            setIsPartTime: jest.fn(),
        });
        const group = container.querySelector('.mode-checkbox');
        expect(group.getAttribute('role')).toBe('group');
        expect(group.getAttribute('aria-label')).toBe('Study mode');
    });
});
