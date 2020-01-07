import React from 'react';
import PropTypes from 'prop-types';

/**
 * Accessible icon component, loading icons from separate sprite.
 */
const Icon = ({ name, className, width, height }) => (
    <svg className={className} width={width} height={height} aria-hidden="true">
        <use xlinkHref={`#${name}`} />
    </svg>
);

Icon.propTypes = {
    name: PropTypes.string.isRequired,
    className: PropTypes.string,
    width: PropTypes.string,
    height: PropTypes.string,
};

Icon.defaultProps = {
    className: null,
    width: null,
    height: null,
};

export default Icon;
