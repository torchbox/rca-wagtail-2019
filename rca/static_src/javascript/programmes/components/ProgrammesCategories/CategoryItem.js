import React from 'react';

import { programmeCategoryShape } from '../../programmes.types';

import Icon from '../Icon/Icon';

/**
 * A single instance from a category, leading to a filtered view of matching programmes.
 */
const CategoryItem = ({ category }) => {
    const { id, title, description } = category;

    return (
        <div className="category-item__wrapper grid">
            <a href={`#test-${id}`} className="category-item">
                <h3 className="heading heading--three category-item__heading">
                    <span className="category-item__heading-inner">
                        {title}
                    </span>
                </h3>
                <div className="category-item__description">{description}</div>
                <div className="category-item__icon-wrapper">
                    <Icon
                        name="arrow-right-filled"
                        className="category-item__icon"
                    />
                </div>
            </a>
        </div>
    );
};

CategoryItem.propTypes = {
    category: programmeCategoryShape.isRequired,
};

export default CategoryItem;
