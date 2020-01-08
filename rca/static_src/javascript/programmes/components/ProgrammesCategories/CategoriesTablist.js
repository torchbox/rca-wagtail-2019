import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

/**
 * A list of tabs, one per category. The active tab is underlined.
 * Tabs can be moved through with the arrow keys.
 */
const CategoriesTablist = ({ categories, activeCategory }) => {
    return (
        <nav
            className="categories-tablist bg bg--light"
            aria-label="Filter programmes"
        >
            <h2 className="body body--two categories-tablist__heading">
                Explore by
            </h2>
            <div role="tablist">
                {categories.map((c) => (
                    <a
                        key={c.id}
                        id={`${c.id}-tab`}
                        href={`#${c.id}`}
                        className="categories-tablist__tab body body--one"
                        role="tab"
                        aria-selected={c.id === activeCategory}
                        aria-controls={c.id}
                        onKeyDown={(e) => {
                            const isArrowLeft = e.keyCode === 37;
                            const isArrowRight = e.keyCode === 39;

                            if (isArrowLeft && e.target.previousSibling) {
                                window.location.hash = e.target.previousSibling.getAttribute(
                                    'href',
                                );
                                e.target.previousSibling.focus();
                            }

                            if (isArrowRight && e.target.nextSibling) {
                                window.location.hash = e.target.nextSibling.getAttribute(
                                    'href',
                                );
                                e.target.nextSibling.focus();
                            }
                        }}
                    >
                        {c.title}
                    </a>
                ))}
            </div>
        </nav>
    );
};

CategoriesTablist.propTypes = {
    categories: programmeCategories.isRequired,
    activeCategory: PropTypes.string.isRequired,
};

export default CategoriesTablist;
