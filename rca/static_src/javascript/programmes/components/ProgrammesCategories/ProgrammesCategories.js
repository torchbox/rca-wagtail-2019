import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

import CategoriesTablist from './CategoriesTablist';
import CategoriesPanels from './CategoriesPanels';

/**
 * Filter-based navigation to programmes, displayed as tabs.
 * If one of the categories is active, the corresponding tab is displayed.
 */
const ProgrammesCategories = ({ categories, activeCategory, activeLength }) => {
    return (
        <div className="programmes-categories">
            <div className="section section--above-grid bg bg--dark">
                <div className="section__notch section__notch--opposite">
                    <div className="section__notch-fill section__notch-fill--content-height section__notch-fill--third-col section__notch-fill--third-col-span-four">
                        <CategoriesTablist
                            categories={categories}
                            activeCategory={activeCategory}
                            activeLength={activeLength}
                        />
                    </div>
                </div>
            </div>
            <CategoriesPanels
                categories={categories}
                activeCategory={activeCategory}
                activeLength={activeLength}
            />
        </div>
    );
};

ProgrammesCategories.propTypes = {
    categories: programmeCategories.isRequired,
    activeCategory: PropTypes.string.isRequired,
    activeLength: PropTypes.bool.isRequired,
};

export default ProgrammesCategories;
