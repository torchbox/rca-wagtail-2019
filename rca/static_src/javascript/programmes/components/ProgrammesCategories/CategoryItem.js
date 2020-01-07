import React from 'react';

import { programmeCategoryShape } from '../../programmes.types';

import Icon from '../Icon/Icon';

const CategoryItem = ({ category }) => {
    const { id, title, description } = category;

    return (
        <a href={`#test-${id}`} className="categories-panels__item grid">
            <h3 className="heading heading--three categories-panels__item__heading">
                {title}
            </h3>
            <p className="categories-panels__item__description">
                {description}
            </p>
            <Icon
                name="arrow-right"
                className="categories-panels__item__icon"
            />
        </a>
    );
};

CategoryItem.propTypes = {
    category: programmeCategoryShape.isRequired,
};

export default CategoryItem;
