import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../programmes.types';

import SearchForm from './SearchForm';
import ProgrammesResults from './ProgrammesResults/ProgrammesResults';
import ProgrammesCategories from './ProgrammesCategories/ProgrammesCategories';

const ProgrammesExplorer = ({ searchLabel, categories }) => {
    return (
        <>
            <SearchForm label={searchLabel} />
            <ProgrammesCategories categories={categories} />
            <ProgrammesResults categories={categories} />
        </>
    );
};

ProgrammesExplorer.propTypes = {
    searchLabel: PropTypes.string,
    categories: programmeCategories.isRequired,
};

ProgrammesExplorer.defaultProps = {
    searchLabel: null,
};

export default ProgrammesExplorer;
