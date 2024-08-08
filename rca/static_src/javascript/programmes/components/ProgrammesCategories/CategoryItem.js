import React from 'react';
import PropTypes from 'prop-types';

import { programmeCategoryItemShape } from '../../programmes.types';

import Icon from '../Icon/Icon';
import { getCategoryItemURL, pushState } from '../../programmes.routes';
import { useStudyMode } from '../../context/StudyModeContext';

/**
 * A single instance from a category, leading to a filtered view of matching programmes.
 */
const CategoryItem = ({ category, parentId }) => {
    const { id, title, description, slug } = category;
    const { isFullTime, isPartTime } = useStudyMode();
    const href = getCategoryItemURL(parentId, id, slug, isFullTime, isPartTime);

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
};

export default CategoryItem;
