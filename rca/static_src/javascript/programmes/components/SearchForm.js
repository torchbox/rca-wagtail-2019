import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { setSearchQuery, searchProgrammes } from '../programmes.slice';

const SearchForm = ({
    searchQuery,
    label,
    setSearchQuery,
    searchProgrammes,
}) => {
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
                    <button
                        className="search__button button"
                        type="submit"
                        aria-label="Search"
                    >
                        <svg width="12px" height="8px" className="search__icon">
                            <use xlinkHref="#arrow" />
                        </svg>
                    </button>
                </div>
            </div>
        </form>
    );
};

SearchForm.propTypes = {
    searchQuery: PropTypes.string.isRequired,
    label: PropTypes.string,
};

SearchForm.defaultProps = {
    label: null,
};

const mapStateToProps = ({ programmes }) => {
    return {
        searchQuery: programmes.searchQuery,
    };
};

const mapDispatchToProps = {
    setSearchQuery,
    searchProgrammes,
};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(SearchForm);
