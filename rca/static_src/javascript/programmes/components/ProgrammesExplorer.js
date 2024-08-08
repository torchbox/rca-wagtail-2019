import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import { useLocation } from 'react-use';

import { programmeCategories } from '../programmes.types';

import ProgrammesCategories from './ProgrammesCategories/ProgrammesCategories';
import ProgrammesResults from './ProgrammesResults/ProgrammesResults';
import SearchForm from './SearchForm';
import { StudyModeContext } from '../context/StudyModeContext';

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
    const hasActiveSearch = !!searchQuery;
    const showCategories = !hasActiveCategoryFilter && !hasActiveSearch;
    const showResults = hasActiveCategoryFilter || hasActiveSearch;

    const [isFullTime, setIsFullTime] = useState(params.get('full-time') || '');
    const [isPartTime, setIsPartTime] = useState(params.get('part-time') || '');

    /* eslint-disable react-hooks/exhaustive-deps */
    useEffect(() => {
        // Only do this on initial load
        if (isFullTime === '' && isPartTime === '') {
            setIsFullTime('true');
            setIsPartTime('true');
        }
    }, []);

    return (
        <StudyModeContext.Provider
            value={{
                params,
                isFullTime,
                setIsFullTime,
                isPartTime,
                setIsPartTime,
            }}
        >
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
                            isFullTime={isFullTime === 'true'}
                            isPartTime={isPartTime === 'true'}
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
                            isFullTime={isFullTime === 'true'}
                            isPartTime={isPartTime === 'true'}
                        />
                    </CSSTransition>
                ) : null}
            </TransitionGroup>
        </StudyModeContext.Provider>
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
