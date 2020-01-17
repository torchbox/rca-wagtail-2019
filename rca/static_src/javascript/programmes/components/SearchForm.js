import React, { useCallback, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';
import { useDebounce } from 'react-use';

import { clearResults, searchProgrammes } from '../programmes.slice';

import Icon from './Icon/Icon';
import {
    pushState,
    replaceState,
    getIndexURL,
    getSearchURL,
} from '../programmes.routes';

const pushStateDebounced = debounce(pushState, 300);

/**
 * A search form for programmes, visually only appearing as a single field.
 */
const SearchForm = ({ searchQuery, label, startSearch, clear, isLoaded }) => {
    const [value, setValue] = useState(searchQuery);
    const startSearchDebounced = useCallback(debounce(startSearch, 300), [
        startSearch,
    ]);
    const showClearButton = value !== '' && isLoaded;

    // Keep search field in sync with search query, but debounce it so users can type.
    useDebounce(
        () => {
            if (value !== searchQuery) {
                setValue(searchQuery);
            }
        },
        500,
        [value, searchQuery, setValue],
    );

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                // Users can submit the search at any time even with no characters entered.
                startSearch(value);
                pushState(getSearchURL(value));
            }}
            className="bg bg--dark"
            method="get"
            role="search"
        >
            <div className="grid">
                <div className="search search--programmes">
                    <label
                        className="search__label"
                        htmlFor="programmes-search-input"
                    >
                        {label}
                    </label>
                    <input
                        className="search__input input"
                        id="programmes-search-input"
                        type="search"
                        placeholder={label}
                        value={value}
                        onChange={(e) => {
                            const query = e.target.value;

                            setValue(query);

                            if (query) {
                                if (query.length >= 3) {
                                    startSearchDebounced(query);
                                    pushStateDebounced(getSearchURL(query));
                                }
                            } else {
                                replaceState(getIndexURL());
                            }
                        }}
                    />
                    {showClearButton ? (
                        <button
                            className="search__button button body body--two"
                            type="button"
                            onClick={(e) => {
                                pushState(getIndexURL(), e);
                                setValue('');
                                clear();
                            }}
                        >
                            Clear
                        </button>
                    ) : (
                        <button
                            className="search__button button"
                            type="submit"
                            aria-label="Search"
                        >
                            <Icon name="arrow" className="search__icon" />
                        </button>
                    )}
                </div>
            </div>
        </form>
    );
};

SearchForm.propTypes = {
    searchQuery: PropTypes.string,
    label: PropTypes.string,
    isLoaded: PropTypes.bool.isRequired,
    clear: PropTypes.func.isRequired,
    startSearch: PropTypes.func.isRequired,
};

SearchForm.defaultProps = {
    searchQuery: '',
    label: null,
};

const mapStateToProps = ({ programmes }) => {
    return {
        isLoaded: programmes.ui.isLoaded,
    };
};

const mapDispatchToProps = {
    clear: clearResults,
    startSearch: searchProgrammes,
};

export default connect(mapStateToProps, mapDispatchToProps)(SearchForm);
