import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import ProgrammesExplorer from './components/ProgrammesExplorer';
import programmesReducer from './programmes.slice';

const mount = document.querySelector('[data-mount-programmes-explorer]');

if (mount) {
    const { searchLabel } = mount.dataset;

    const store = configureStore({
        // https://redux-starter-kit.js.org/api/configureStore
        devTools: true,
        reducer: {
            programmes: programmesReducer,
        },
    });

    ReactDOM.render(
        <Provider store={store}>
            <ProgrammesExplorer searchLabel={searchLabel} />
        </Provider>,
        mount,
    );
}
