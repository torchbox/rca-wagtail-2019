import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
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
    const searchQuery = params.get('search') || '';
    // The explorer is a two-state toggle: either you are browsing the
    // categories, or you are looking at the results of a filter or a search.
    const showResults = Boolean(activeValue || searchQuery);

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
            {/* Whichever view mounts fades itself in — see _programmes-explorer.scss. */}
            <div className="explorer-transitions">
                {showResults ? (
                    <ProgrammesResults
                        categories={categories}
                        activeCategory={activeCategory}
                        activeValue={activeValue}
                        searchQuery={searchQuery}
                        isFullTime={isFullTime === 'true'}
                        isPartTime={isPartTime === 'true'}
                    />
                ) : (
                    <ProgrammesCategories
                        categories={categories}
                        activeCategory={activeCategory}
                        isFullTime={isFullTime === 'true'}
                        isPartTime={isPartTime === 'true'}
                    />
                )}
            </div>
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
