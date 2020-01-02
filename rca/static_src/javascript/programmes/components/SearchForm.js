import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
    setSearchQuery,
    clearSearchQuery,
    searchProgrammes,
} from '../programmes.slice';

const SearchForm = ({
    searchQuery,
    label,
    setSearchQuery,
    clearSearchQuery,
    searchProgrammes,
    hasResults,
    isLoaded,
}) => {
    const showClear = hasResults && isLoaded;

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                searchProgrammes(searchQuery);
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
                        value={searchQuery}
                        onChange={(e) => {
                            const query = e.target.value;

                            setSearchQuery(query);

                            if (query.length >= 3) {
                                searchProgrammes(query);
                            }
                        }}
                    />
                    {showClear ? (
                        <button
                            className="search__button button body body--two"
                            type="button"
                            onClick={(e) => {
                                e.preventDefault();
                                clearSearchQuery();
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
                            <svg
                                width="12px"
                                height="8px"
                                className="search__icon"
                                aria-hidden="true"
                            >
                                <use xlinkHref="#arrow" />
                            </svg>
                        </button>
                    )}
                </div>
            </div>
        </form>
    );
};

SearchForm.propTypes = {
    label: PropTypes.string,
    searchQuery: PropTypes.string.isRequired,
    hasResults: PropTypes.bool.isRequired,
    isLoaded: PropTypes.bool.isRequired,
};

SearchForm.defaultProps = {
    label: null,
};

const mapStateToProps = ({ programmes }) => {
    return {
        searchQuery: programmes.searchQuery,
        hasResults: programmes.results.length > 0,
        isLoaded: programmes.ui.isLoaded,
    };
};

const mapDispatchToProps = {
    setSearchQuery,
    clearSearchQuery,
    searchProgrammes,
};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(SearchForm);
