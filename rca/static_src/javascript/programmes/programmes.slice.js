import { createSlice } from '@reduxjs/toolkit';

import { getProgrammes } from './programmes.api';

const initialState = {
    searchQuery: '',
    ui: {
        isLoading: false,
        isLoaded: false,
        error: null,
    },
    results: [],
};

const { reducer, actions } = createSlice({
    name: 'programmes',
    initialState,
    reducers: {
        setSearchQuery: (state, { payload }) => {
            state.searchQuery = payload;
        },

        loadResultsStart: (state) => {
            state.ui = { ...initialState.ui };
            state.ui.isLoading = true;
        },

        loadResultsSuccess: (state, { payload }) => {
            state.ui = { ...initialState.ui };
            state.ui.isLoaded = true;
            state.results = payload;
        },

        loadResultsError: (state, { payload }) => {
            state.ui = { ...initialState.ui };
            state.ui.error = payload;
        },
    },
});

export const { setSearchQuery } = actions;

export const searchProgrammes = (searchQuery) => {
    return (dispatch) => {
        dispatch(actions.loadResultsStart());

        getProgrammes({
            query: searchQuery,
        }).then(
            (result) => {
                dispatch(actions.loadResultsSuccess(result.items));
            },
            (error) => {
                // If the API call was cancelled, we can safely dismiss that error.
                if (error.name !== 'AbortError') {
                    dispatch(actions.loadResultsError(error));
                }
            },
        );
    };
};

export default reducer;
