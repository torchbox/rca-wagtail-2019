import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { useLocation } from 'react-use';

import { programmePageShape } from '../../programmes.types';
import { searchProgrammes } from '../../programmes.slice';

import Icon from '../Icon/Icon';
import ProgrammeTeaser from './ProgrammeTeaser';

const getResultsCount = (count) => {
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
 * A list of programmes matching a search or filter.
 * The list auto-magically appears when matches are found.
 */
const ProgrammesResults = ({
    programmes,
    hasActiveSearch,
    isLoading,
    filterProgrammes,
}) => {
    const [activeProgramme, setActiveProgramme] = useState(null);
    const loc = useLocation();
    const params = new URLSearchParams(loc.search);
    const category = params.get('category');
    const value = params.get('value');
    const hasActiveFilter = category && value;

    useEffect(() => {
        if (hasActiveFilter) {
            filterProgrammes({ [category]: value });
            const mount = document.querySelector(
                '[data-mount-programmes-explorer]',
            );
            if (mount) {
                mount.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }, [filterProgrammes, hasActiveFilter, category, value]);

    if (!hasActiveFilter && !hasActiveSearch) {
        return null;
    }

    const count = getResultsCount(programmes.length);
    const theme = hasActiveFilter ? 'light' : 'dark';
    return (
        <>
            <div className={`programmes-results bg bg--${theme} section`}>
                <div className="grid">
                    <div className="programmes-results__actions">
                        <button
                            type="button"
                            className="button programmes-results__back body body--one"
                        >
                            <Icon
                                name="arrow"
                                className="programmes-results__back__icon"
                            />
                            <span className="programmes-results__back__text">
                                Back
                            </span>
                        </button>
                    </div>
                    <p
                        className="heading heading--five programmes-results__status"
                        role="alert"
                    >
                        {isLoading ? 'Loading…' : count}
                    </p>
                </div>
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
                <div
                    className="section section--opposite-notch bg bg--dark"
                    aria-hidden="true"
                >
                    <div className="section__notch section__notch--opposite">
                        <div className="section__notch-fill section__notch-fill--second-col" />
                    </div>
                </div>
            )}
        </>
    );
};

ProgrammesResults.propTypes = {
    programmes: PropTypes.arrayOf(programmePageShape).isRequired,
    hasActiveSearch: PropTypes.bool.isRequired,
    isLoading: PropTypes.bool.isRequired,
    filterProgrammes: PropTypes.func.isRequired,
};

const mapStateToProps = ({ programmes }) => {
    return {
        programmes: programmes.results,
        hasActiveSearch: programmes.searchQuery.length >= 3,
        isLoading: programmes.ui.isLoading || !programmes.ui.isLoaded,
    };
};

const mapDispatchToProps = {
    filterProgrammes: searchProgrammes.bind(null, null),
};

export default connect(mapStateToProps, mapDispatchToProps)(ProgrammesResults);
