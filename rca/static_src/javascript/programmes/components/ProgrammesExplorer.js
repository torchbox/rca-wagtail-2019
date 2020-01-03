import React from 'react';
import PropTypes from 'prop-types';

import SearchForm from './SearchForm';
import ProgrammesResults from './ProgrammesResults';

const ProgrammesExplorer = ({ searchLabel }) => {
    return (
        <div>
            <SearchForm label={searchLabel} />
            <ProgrammesResults />
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
