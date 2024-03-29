import PropTypes from 'prop-types';
import React from 'react';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import { useLocation } from 'react-use';

import { programmeCategories } from '../programmes.types';

import ProgrammesCategories from './ProgrammesCategories/ProgrammesCategories';
import ProgrammesResults from './ProgrammesResults/ProgrammesResults';
import SearchForm from './SearchForm';

/**
 * Programmes and short courses listing, with a search form, filters, and a results view.
 * Pages come from the Wagtail API (via Redux), UI state is synced in the URL.
 */
const ProgrammesExplorer = ({ searchLabel, categories }) => {
    const loc = useLocation();
    const params = new URLSearchParams(loc.search);
    const activeCategory = params.get('category') || categories[0].id;
    const filterValue = params.get('value') || '';
    const activeValue = filterValue.split('-')[0];
    const hasActiveCategoryFilter = !!activeValue;
    const searchQuery = params.get('search') || '';
    const activeLength = params.get('part-time') || '';
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
                            activeLength={activeLength}
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
                            activeLength={activeLength}
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
