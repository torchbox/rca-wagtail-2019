import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

import CategoryItem from './CategoryItem';

/**
 * Tabs for all categories pages can be filtered by.
 * All tabs are rendered to the DOM so screen readers’ ARIA markup
 * is correct.
 */
const CategoriesPanels = ({ categories, activeCategory }) => {
    return (
        <div className="categories-panels bg bg--light">
            {categories.map((c) => (
                <div
                    key={c.id}
                    id={c.id}
                    className="categories-panels__panel"
                    aria-labelledby={`${c.id}-tab`}
                    aria-expanded={c.id === activeCategory}
                    hidden={c.id !== activeCategory}
                >
                    {c.items.map((item) => (
                        <CategoryItem
                            key={item.id}
                            category={item}
                            parentId={c.id}
                        />
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
