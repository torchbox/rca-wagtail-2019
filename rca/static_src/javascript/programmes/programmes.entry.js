import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import ProgrammesExplorer from './components/ProgrammesExplorer';
import createReduxStore from './programmes.store';

const mount = document.querySelector('[data-mount-programmes-explorer]');

if (mount) {
    const { searchLabel } = mount.dataset;

    const store = createReduxStore();

    ReactDOM.render(
        <Provider store={store}>
            <ProgrammesExplorer searchLabel={searchLabel} />
        </Provider>,
        mount,
    );
}
