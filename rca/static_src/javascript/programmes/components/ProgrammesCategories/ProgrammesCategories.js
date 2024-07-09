import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

import CategoriesTablist from './CategoriesTablist';
import CategoriesPanels from './CategoriesPanels';
import ModeCheckbox from '../StudyModeCheckbox';

/**
 * Filter-based navigation to programmes, displayed as tabs.
 * If one of the categories is active, the corresponding tab is displayed.
 */
const ProgrammesCategories = ({
    categories,
    activeCategory,
    isFullTime,
    isPartTime,
}) => {
    return (
        <div className="programmes-categories">
            <div className="section section--above-grid bg bg--dark">
                <div className="section__notch">
                    <div
                        className="section__notch-fill section__notch-fill--content-height section__notch-fill--third-col
                    section__notch-fill--third-col-two-span-four"
                    >
                        <CategoriesTablist
                            categories={categories}
                            activeCategory={activeCategory}
                            isFullTime={isFullTime}
                            isPartTime={isPartTime}
                        />
                    </div>
                </div>
            </div>
            <ModeCheckbox
                ariaLabel="Programme study mode"
                isFullTime={isFullTime}
                isPartTime={isPartTime}
            />
            <CategoriesPanels
                categories={categories}
                activeCategory={activeCategory}
                isFullTime={isFullTime}
                isPartTime={isPartTime}
            />
        </div>
    );
};

ProgrammesCategories.propTypes = {
    categories: programmeCategories.isRequired,
    activeCategory: PropTypes.string.isRequired,
    isFullTime: PropTypes.bool.isRequired,
    isPartTime: PropTypes.bool.isRequired,
};

export default ProgrammesCategories;
