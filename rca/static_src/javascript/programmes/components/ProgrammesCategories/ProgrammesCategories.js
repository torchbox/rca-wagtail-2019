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
const ProgrammesCategories = ({ categories, activeCategory }) => {
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
                        />
                    </div>
                </div>
            </div>
            <div className="section section--above-grid section--programme-toggles bg bg--light">
                <div className="section__notch">
                    <ModeCheckbox ariaLabel="Programme study mode" />
                </div>
            </div>
            <CategoriesPanels
                categories={categories}
                activeCategory={activeCategory}
            />
        </div>
    );
};

ProgrammesCategories.propTypes = {
    categories: programmeCategories.isRequired,
    activeCategory: PropTypes.string.isRequired,
};

export default ProgrammesCategories;
