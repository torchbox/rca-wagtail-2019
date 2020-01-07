import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

const CategoriesTablist = ({ categories, activeCategory }) => {
    return (
        <div role="tablist" className="categories-tablist bg bg--light">
            <h2 className="body body--two categories-tablist__heading">
                Explore by
            </h2>
            <nav aria-label="Filter programmes">
                {categories.map((c) => (
                    <a
                        key={c.id}
                        id={`${c.id}-tab`}
                        href={`#${c.id}`}
                        className="categories-tablist__tab body body--one"
                        role="tab"
                        aria-selected={c.id === activeCategory}
                    >
                        {c.title}
                    </a>
                ))}
            </nav>
        </div>
    );
};

CategoriesTablist.propTypes = {
    categories: programmeCategories.isRequired,
    activeCategory: PropTypes.string.isRequired,
};

export default CategoriesTablist;
