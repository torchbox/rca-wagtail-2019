import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import ProgrammesExplorer from './ProgrammesExplorer';
import programmesReducer from '../programmes.slice';

const getMockCategories = () => [
    {
        id: 'discipline',
        title: 'Discipline',
        items: [
            {
                id: 1,
                title: 'Architecture',
                description: 'Architecture programmes',
                slug: 'architecture',
            },
        ],
    },
];

const renderExplorer = () => {
    const store = configureStore({
        reducer: { programmes: programmesReducer },
    });

    return render(
        <Provider store={store}>
            <ProgrammesExplorer
                searchLabel="Search"
                categories={getMockCategories()}
            />
        </Provider>,
    );
};

describe('ProgrammesExplorer', () => {
    beforeEach(() => {
        // The explorer drives its state through the URL via pushState, which
        // persists across tests in this file. Reset it, or each test inherits
        // wherever the previous one navigated to.
        window.history.pushState({}, '', '/');

        global.fetch = jest.fn(() =>
            Promise.resolve({ json: () => Promise.resolve({ items: [] }) }),
        );
    });

    afterEach(() => {
        delete global.fetch;
    });

    // Regression test: selecting a category used to crash the whole explorer
    // with "ReactDOM.findDOMNode is not a function", because react-dom 19
    // removed findDOMNode and react-transition-group's CSSTransition fell back
    // to it whenever no nodeRef prop was provided. The explorer no longer uses
    // react-transition-group at all — the fade is pure CSS.
    it('switches from categories to results when a category item is selected', async () => {
        renderExplorer();

        await userEvent.click(
            screen.getByRole('link', { name: /^Architecture/ }),
        );

        expect(
            screen.getByRole('heading', { name: 'Exploring by' }),
        ).toBeInTheDocument();
    });

    it('shows exactly one of the two views at a time', async () => {
        const { container } = renderExplorer();

        const views = () =>
            container.querySelectorAll(
                '.programmes-categories, .programmes-results__wrapper',
            );

        expect(views()).toHaveLength(1);
        expect(
            container.querySelector('.programmes-categories'),
        ).not.toBeNull();

        await userEvent.click(
            screen.getByRole('link', { name: /^Architecture/ }),
        );

        expect(views()).toHaveLength(1);
        expect(
            container.querySelector('.programmes-results__wrapper'),
        ).not.toBeNull();
    });
});
