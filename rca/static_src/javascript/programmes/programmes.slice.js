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

        clearSearchQuery: (state) => {
            state.searchQuery = initialState.searchQuery;
            state.results = initialState.results;
        },

        loadResultsStart: (state) => {
            state.ui = { ...initialState.ui };
            state.ui.isLoading = true;
            state.results = initialState.results;
        },

        loadResultsSuccess: (state, { payload }) => {
            state.ui = { ...initialState.ui };
            state.ui.isLoaded = true;
            state.results = payload;
        },

        loadResultsError: (state, { payload }) => {
            state.ui = { ...initialState.ui };
            state.ui.error = payload;
            state.results = initialState.results;
        },
    },
});

export const { setSearchQuery, clearSearchQuery } = actions;

/**
 * Get the matching programmes from the search API.
 * @param {string} searchQuery
 */
export const searchProgrammes = (searchQuery, filters = {}) => {
    return (dispatch) => {
        dispatch(actions.loadResultsStart());

        getProgrammes({
            query: searchQuery,
            filters,
        }).then(
            (programmes) => {
                dispatch(actions.loadResultsSuccess(programmes));
            },
            (error) => {
                // If the error is an API call cancellation, we can safely dismiss that error.
                if (error.name !== 'AbortError') {
                    dispatch(actions.loadResultsError(error));
                }
            },
        );
    };
};

export default reducer;
