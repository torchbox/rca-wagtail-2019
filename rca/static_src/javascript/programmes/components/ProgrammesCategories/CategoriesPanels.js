import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategories } from '../../programmes.types';

import Icon from '../Icon/Icon';

const CategoriesPanels = ({ categories, activeCategory, applyFilter }) => {
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
                    {c.items.map((i) => (
                        <button
                            className="categories-panels__panel-btn grid"
                            type="button"
                            key={i.id}
                            onClick={() => {
                                const params = new URLSearchParams(
                                    window.location.search,
                                );
                                params.set(c.id, i.id);
                                console.log(params);
                                window.history.pushState(
                                    null,
                                    null,
                                    `${window.location.pathname}?${params}`,
                                );
                                applyFilter({
                                    [c.id]: i.id,
                                });
                            }}
                        >
                            <h3 className="heading heading--three">
                                {i.title}
                            </h3>
                            <p>{i.description}</p>
                            <Icon name="arrow-right" />
                        </button>
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
