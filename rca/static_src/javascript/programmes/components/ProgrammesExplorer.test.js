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
        global.fetch = jest.fn(() =>
            Promise.resolve({ json: () => Promise.resolve({ items: [] }) }),
        );
    });

    afterEach(() => {
        delete global.fetch;
    });

    // Regression test: selecting a category used to crash the whole explorer
    // with "ReactDOM.findDOMNode is not a function", because react-dom 19
    // removed findDOMNode and react-transition-group's CSSTransition falls
    // back to it whenever no nodeRef prop is provided.
    it('switches from categories to results when a category item is selected', async () => {
        renderExplorer();

        await userEvent.click(
            screen.getByRole('link', { name: /^Architecture/ }),
        );

        expect(
            screen.getByRole('heading', { name: 'Exploring by' }),
        ).toBeInTheDocument();
    });
});
