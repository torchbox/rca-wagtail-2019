import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { useLocation } from 'react-use';

import { programmeCategories } from '../../programmes.types';
import { searchProgrammes } from '../../programmes.slice';

import CategoriesTablist from './CategoriesTablist';
import CategoriesPanels from './CategoriesPanels';

/**
 * A list of programmes matching a search or filter.
 * The list auto-magically appears when matches are found.
 */
const ProgrammesCategories = ({ categories, applyFilter }) => {
    const loc = useLocation();
    const activeCategory = loc.hash.replace('#', '') || categories[0].id;
    return (
        <div>
            <div className="section section--opposite-notch bg bg--dark">
                <div className="section__notch section__notch--opposite">
                    <div className="section__notch-fill section__notch-fill--second-col">
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
                applyFilter={applyFilter}
            />
        </div>
    );
};

ProgrammesCategories.propTypes = {
    categories: programmeCategories.isRequired,
    applyFilter: PropTypes.func.isRequired,
};

const mapDispatchToProps = {
    applyFilter: searchProgrammes.bind(null, ''),
};

export default connect(null, mapDispatchToProps)(ProgrammesCategories);
