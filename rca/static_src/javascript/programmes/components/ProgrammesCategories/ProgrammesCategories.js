import React from 'react';
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
const ProgrammesCategories = ({ categories }) => {
    const loc = useLocation();
    const params = new URLSearchParams(loc.search);
    const activeCategory = params.get('category') || categories[0].id;
    const activeItem = params.get('value');
    const activeSearch = params.get('search');

    if (activeItem || activeSearch) {
        return null;
    }

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
};

const mapDispatchToProps = {
    applyFilter: searchProgrammes.bind(null, ''),
};

export default connect(null, mapDispatchToProps)(ProgrammesCategories);
