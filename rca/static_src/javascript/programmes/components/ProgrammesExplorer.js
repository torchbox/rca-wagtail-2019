import React from 'react';
import PropTypes from 'prop-types';
import { useLocation } from 'react-use';
import { CSSTransition, TransitionGroup } from 'react-transition-group';

import { programmeCategories } from '../programmes.types';

import SearchForm from './SearchForm';
import ProgrammesResults from './ProgrammesResults/ProgrammesResults';
import ProgrammesCategories from './ProgrammesCategories/ProgrammesCategories';

const ProgrammesExplorer = ({ searchLabel, categories }) => {
    const loc = useLocation();
    const params = new URLSearchParams(loc.search);
    const activeCategory = params.get('category') || categories[0].id;
    const activeValue = params.get('value');
    const hasActiveCategoryFilter = !!activeValue;
    const searchQuery = params.get('search') || '';
    const hasActiveSearch = !!searchQuery;
    const showCategories = !hasActiveCategoryFilter && !hasActiveSearch;
    const showResults = hasActiveCategoryFilter || hasActiveSearch;

    return (
        <>
            <SearchForm searchQuery={searchQuery} label={searchLabel} />
            <TransitionGroup className="explorer-transitions">
                {showCategories ? (
                    <CSSTransition
                        key="categories"
                        classNames="categories-transition"
                        timeout={500}
                        in={showCategories}
                        mountOnEnter
                        unmountOnExit
                    >
                        <ProgrammesCategories
                            categories={categories}
                            activeCategory={activeCategory}
                        />
                    </CSSTransition>
                ) : null}
                {showResults ? (
                    <CSSTransition
                        key="results"
                        classNames="results-transition"
                        timeout={500}
                        in={showResults}
                        mountOnEnter
                        unmountOnExit
                    >
                        <ProgrammesResults
                            categories={categories}
                            activeCategory={activeCategory}
                            activeValue={activeValue}
                            searchQuery={searchQuery}
                        />
                    </CSSTransition>
                ) : null}
            </TransitionGroup>
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
