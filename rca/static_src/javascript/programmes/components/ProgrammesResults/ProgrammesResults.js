import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { programmePageShape } from '../../programmes.types';

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
const ProgrammesResults = ({ programmes, hasActiveSearch }) => {
    if (!hasActiveSearch) {
        return null;
    }

    const count = getResultsCount(programmes.length);
    return (
        <div className="bg bg--dark section">
            <div className="programmes-results">
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
                        className="heading heading--five programmes-results__count"
                        role="alert"
                    >
                        {count}
                    </p>
                </div>
                {programmes.length === 0 ? null : (
                    <div className="programmes-results__list">
                        {programmes.map((prog) => {
                            return (
                                <ProgrammeTeaser
                                    key={prog.id}
                                    programme={prog}
                                />
                            );
                        })}
                    </div>
                )}
            </div>
            <div className="section__notch section__notch--opposite">
                <div className="section__notch-fill section__notch-fill--second-col" />
            </div>
        </div>
    );
};

ProgrammesResults.propTypes = {
    programmes: PropTypes.arrayOf(programmePageShape).isRequired,
    hasActiveSearch: PropTypes.bool.isRequired,
};

const mapStateToProps = ({ programmes }) => {
    return {
        programmes: programmes.results,
        hasActiveSearch: programmes.searchQuery.length >= 3,
    };
};

export default connect(mapStateToProps)(ProgrammesResults);
