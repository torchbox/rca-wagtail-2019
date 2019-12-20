import { configureStore } from '@reduxjs/toolkit';

import programmes from './programmes.slice';

const createReduxStore = () => {
    // https://redux-starter-kit.js.org/api/configureStore
    return configureStore({
        devTools: true,
        reducer: {
            programmes,
        },
    });
};

export default createReduxStore;
