import React from 'react';
import PropTypes from 'prop-types';

import SearchForm from './SearchForm';
import SearchResults from './SearchResults';

const ProgrammesExplorer = ({ searchLabel }) => {
    return (
        <div>
            <SearchForm label={searchLabel} />
            <SearchResults />
        </div>
    );
};

ProgrammesExplorer.propTypes = {
    searchLabel: PropTypes.string,
};

ProgrammesExplorer.defaultProps = {
    searchLabel: null,
};

export default ProgrammesExplorer;
