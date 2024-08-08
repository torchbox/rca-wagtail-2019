import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
    programmePageShape,
    programmeCategories,
} from '../../programmes.types';
import { searchProgrammes } from '../../programmes.slice';

import Icon from '../Icon/Icon';
import ProgrammeTeaser from './ProgrammeTeaser';
import { pushState, getCategoryURL } from '../../programmes.routes';
import ModeCheckbox from '../StudyModeCheckbox';
import { useStudyMode } from '../../context/StudyModeContext';

const getResultsStatus = (
    isLoading,
    categories,
    category,
    categoryValue,
    count,
) => {
    if (isLoading) {
        return 'Loading…';
    }

    const activeCategory = categories.find((c) => c.id === category);
    if (activeCategory) {
        const activeItem = activeCategory.items.find(
            (i) => `${i.id}` === categoryValue,
        );

        if (activeItem) {
            return `${activeCategory.title}: ${activeItem.title}`;
        }
    }

    switch (count) {
        case 0: {
            return 'No results match your search';
        }
        case 1: {
            return '1 result matches your search';
        }
        default: {
            return `${count} results match your search`;
        }
    }
};

/**
 * A list of pages matching a search or filter.
 * The list auto-magically appears when matches are found.
 */
const ProgrammesResults = ({
    categories,
    programmes,
    isLoading,
    startSearch,
    activeCategory,
    activeValue,
    searchQuery,
}) => {
    const [activeProgramme, setActiveProgramme] = useState(null);
    const hasActiveFilter = activeCategory && activeValue;
    const theme = hasActiveFilter ? 'light' : 'dark';
    const { isFullTime, isPartTime } = useStudyMode();

    useEffect(() => {
        if (hasActiveFilter || !!isFullTime || !!isPartTime) {
            startSearch(null, { [activeCategory]: activeValue });
            const mount = document.querySelector(
                '[data-mount-programmes-explorer]',
            );
            // If we scrolled past the top of the programmes explorer, scroll back to it.
            if (mount && mount.getBoundingClientRect().top < 0) {
                mount.scrollIntoView({ behavior: 'smooth' });
            }
        } else if (searchQuery) {
            startSearch(searchQuery);
        }
    }, [
        startSearch,
        hasActiveFilter,
        activeCategory,
        activeValue,
        searchQuery,
        isFullTime,
        isPartTime,
    ]);

    return (
        <div className="programmes-results__wrapper">
            <div className="section section--above-grid bg bg--dark">
                <div className="section__notch">
                    <div className="section__notch-fill section__notch-fill--content-height section__notch-fill--first-col">
                        <div className="programmes-results__actions">
                            {hasActiveFilter ? (
                                <button
                                    type="button"
                                    className="button programmes-results__back body body--one"
                                    onClick={() => {
                                        if (
                                            hasActiveFilter ||
                                            !!isFullTime ||
                                            !!isPartTime
                                        ) {
                                            const href = getCategoryURL(
                                                activeCategory,
                                                isFullTime,
                                                isPartTime,
                                            );
                                            pushState(href);
                                        } else {
                                            window.history.back();
                                        }
                                    }}
                                >
                                    <Icon
                                        name="arrow"
                                        className="programmes-results__back-icon"
                                    />
                                    <span className="programmes-results__back-text">
                                        Back
                                    </span>
                                </button>
                            ) : null}
                        </div>
                    </div>
                    <div
                        className="section__notch-fill section__notch-fill--content-height section__notch-fill--third-col
                    section__notch-fill--third-col-two-span-four"
                    >
                        <nav>
                            <h2 className="body body--two programmes-results__heading">
                                Exploring by
                            </h2>
                            <p
                                className="heading heading--five programmes-results__status"
                                role="alert"
                                style={{
                                    marginBottom: 0,
                                }}
                            >
                                {getResultsStatus(
                                    isLoading,
                                    categories,
                                    activeCategory,
                                    activeValue,
                                    programmes.length,
                                )}
                            </p>
                        </nav>
                    </div>
                </div>
            </div>
            <div className="section section--above-grid section--programme-toggles bg bg--light">
                <div className="section__notch">
                    <ModeCheckbox ariaLabel="Programme study mode" />
                </div>
            </div>
            <div className={`programmes-results bg bg--${theme} section`}>
                {programmes.length === 0 ? null : (
                    <div className="grid">
                        <div className="programmes-results__list">
                            {programmes.map((prog) => {
                                const setActive = () =>
                                    setActiveProgramme(prog.id);

                                return (
                                    <ProgrammeTeaser
                                        key={prog.id}
                                        programme={prog}
                                        onFocus={setActive}
                                        onMouseOver={setActive}
                                    />
                                );
                            })}
                        </div>
                        <div className="programmes-results__images">
                            <div className="programmes-results__images-sticky">
                                {programmes.map((prog, i) => {
                                    const isActive =
                                        activeProgramme === prog.id || i === 0;

                                    if (!prog.hero_image_square) {
                                        return null;
                                    }

                                    return (
                                        <img
                                            key={prog.id}
                                            className={`programmes-results__image ${
                                                isActive
                                                    ? 'programmes-results__image--active'
                                                    : ''
                                            }`}
                                            src={prog.hero_image_square.url}
                                            width={prog.hero_image_square.width}
                                            height={
                                                prog.hero_image_square.height
                                            }
                                            alt=""
                                        />
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                )}
            </div>
            {hasActiveFilter ? null : (
                <div className="section bg bg--dark" aria-hidden="true">
                    <div className="section__notch section__notch--opposite">
                        <div className="section__notch-fill section__notch-fill--second-col" />
                    </div>
                </div>
            )}
        </div>
    );
};

ProgrammesResults.propTypes = {
    categories: programmeCategories.isRequired,
    programmes: PropTypes.arrayOf(programmePageShape).isRequired,
    isLoading: PropTypes.bool.isRequired,
    startSearch: PropTypes.func.isRequired,
    activeCategory: PropTypes.string.isRequired,
    activeValue: PropTypes.string,
    searchQuery: PropTypes.string,
};

ProgrammesResults.defaultProps = {
    searchQuery: null,
    activeValue: null,
};

const mapStateToProps = ({ programmes }) => {
    return {
        programmes: programmes.results,
        isLoading: programmes.ui.isLoading || !programmes.ui.isLoaded,
    };
};

const mapDispatchToProps = {
    startSearch: searchProgrammes,
};

export default connect(mapStateToProps, mapDispatchToProps)(ProgrammesResults);
