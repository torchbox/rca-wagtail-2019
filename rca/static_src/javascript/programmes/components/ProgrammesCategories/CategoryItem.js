import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategoryItemShape } from '../../programmes.types';

import Icon from '../Icon/Icon';
import { getCategoryItemURL, pushState } from '../../programmes.routes';

/**
 * A single instance from a category, leading to a filtered view of matching programmes.
 */
const CategoryItem = ({ category, parentId, isFullTime, isPartTime }) => {
    const { id, title, description, slug } = category;
    const href = getCategoryItemURL(parentId, id, slug, isFullTime, isPartTime);

    console.log('CategoryItem: getCategoryItemURL:', getCategoryItemURL);

    return (
        <div className="category-item__wrapper grid">
            <a
                href={href}
                className="category-item"
                onClick={pushState.bind(null, href)}
            >
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
    category: programmeCategoryItemShape.isRequired,
    parentId: PropTypes.string.isRequired,
    isFullTime: PropTypes.bool.isRequired,
    isPartTime: PropTypes.bool.isRequired,
};

export default CategoryItem;
