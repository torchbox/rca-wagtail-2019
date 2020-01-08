import React from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import ProgrammesExplorer from './components/ProgrammesExplorer';
import programmesReducer from './programmes.slice';
import { programmeCategory } from './programmes.types';

const mount = document.querySelector('[data-mount-programmes-explorer]');

if (mount) {
    const { searchLabel } = mount.dataset;

    const filtersScript = document.querySelector('#programme-listing-filters');
    let filters = [];

    if (filtersScript) {
        try {
            filters = JSON.parse(filtersScript.innerHTML);

            // Use prop-types definitions to check that the API response matches what we expect.
            if (process.env.NODE_ENV === 'development') {
                filters.forEach((item) => {
                    PropTypes.checkPropTypes(
                        programmeCategory,
                        item,
                        '',
                        'Serialised filters',
                    );
                });
            }
        } catch (e) {
            console.error('Failed reading JSON config from', filtersScript, e);
        }
    }

    const store = configureStore({
        // https://redux-starter-kit.js.org/api/configureStore
        devTools: true,
        reducer: {
            programmes: programmesReducer,
        },
    });

    ReactDOM.render(
        <Provider store={store}>
            <ProgrammesExplorer
                searchLabel={searchLabel}
                categories={filters}
            />
        </Provider>,
        mount,
    );
}
