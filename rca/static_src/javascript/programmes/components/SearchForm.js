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
        >
            <label>
                <span>{label}</span>
                <input
                    type="search"
                    value={searchQuery}
                    onChange={(e) => {
                        const query = e.target.value;

                        setSearchQuery(query);

                        if (query.length >= 3) {
                            searchProgrammes(query);
                        }
                    }}
                />
            </label>
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
