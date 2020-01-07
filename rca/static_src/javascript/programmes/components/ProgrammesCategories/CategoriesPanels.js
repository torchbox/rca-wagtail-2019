import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

import CategoryItem from './CategoryItem';

const CategoriesPanels = ({ categories, activeCategory }) => {
    return (
        <div className="categories-panels bg bg--light">
            {categories.map((c) => (
                <div
                    key={c.id}
                    id={c.id}
                    className="categories-panels__panel"
                    role="tabpanel"
                    aria-labelledby={`${c.id}-tab`}
                    aria-expanded={c.id === activeCategory}
                    hidden={c.id !== activeCategory}
                >
                    {c.items.map((item) => (
                        <CategoryItem key={item.id} category={item} />
                    ))}
                </div>
            ))}
        </div>
    );
};

CategoriesPanels.propTypes = {
    categories: programmeCategories.isRequired,
    activeCategory: PropTypes.string.isRequired,
};

export default CategoriesPanels;
