import React, { useCallback, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';

import { clearResults, searchProgrammes } from '../programmes.slice';

import Icon from './Icon/Icon';
import {
    pushState,
    replaceState,
    getIndexURL,
    getSearchURL,
} from '../programmes.routes';

const replaceStateDebounced = debounce(replaceState, 300);

/**
 * A search form for programmes, visually only appearing as a single field.
 */
const SearchForm = ({ searchQuery, label, startSearch, clear, isLoaded }) => {
    const [value, setValue] = useState(searchQuery);
    const startSearchDebounced = useCallback(debounce(startSearch, 300), [
        startSearch,
    ]);
    const showClearButton = value !== '' && isLoaded;

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                if (value) {
                    // Users can submit the search at any time.
                    startSearch(value);
                    replaceState(getSearchURL(value));
                }
            }}
            className="bg bg--dark"
            method="get"
            role="search"
        >
            <div className="grid">
                <div className="search search--inline">
                    <label
                        className="search__label"
                        htmlFor="programmes-search-input"
                    >
                        {label}
                    </label>
                    <div className="search__magnifying">
                        <Icon name="magnifying-glass" />
                    </div>
                    <input
                        className="search__input search__input--with-left-icon input"
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
                                    replaceStateDebounced(getSearchURL(query));
                                }
                            } else {
                                replaceState(getIndexURL());
                            }
                        }}
                    />
                    {showClearButton && (
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
