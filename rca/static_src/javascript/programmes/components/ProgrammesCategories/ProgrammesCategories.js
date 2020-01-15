import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

import CategoriesTablist from './CategoriesTablist';
import CategoriesPanels from './CategoriesPanels';

/**
 * Filter-based navigation to programmes, displayed as tabs.
 * If one of the categories is active, the corresponding tab is displayed.
 */
const ProgrammesCategories = ({ categories, activeCategory }) => {
    return (
        <div>
            <div className="section section--opposite-notch bg bg--dark">
                <div className="section__notch section__notch--opposite">
                    <div className="section__notch-fill section__notch-fill--content-height section__notch-fill--first-col section__notch-fill--second-col@medium">
                        <CategoriesTablist
                            categories={categories}
                            activeCategory={activeCategory}
                        />
                    </div>
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
