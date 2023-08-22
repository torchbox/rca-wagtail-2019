import PropTypes from 'prop-types';
import React, { useState } from 'react';

import { getCourseLengthURL, pushState } from '../programmes.routes';

const ToggleSwitch = ({ ariaLabel, activeLength }) => {
    const [isPartTime, setIsPartTime] = useState(activeLength);

    const handleToggle = () => {
        setIsPartTime(!isPartTime);

        // Update the URL with the new Part-time value
        const url = getCourseLengthURL(isPartTime ? '' : 'true');
        pushState(url);
    };

    return (
        // eslint-disable-next-line jsx-a11y/label-has-associated-control
        <label className="toggle-switch" aria-label={ariaLabel}>
            <input
                type="checkbox"
                className="toggle-switch__checkbox"
                checked={isPartTime}
                onChange={handleToggle}
            />
            <span className="toggle-switch__switch" />
            <span
                className="toggle-switch__label toggle-switch__label--first"
                data-label="full-time"
            >
                Full-time
            </span>
            <span
                className="toggle-switch__label toggle-switch__label--last"
                data-label="part-time"
            >
                Part-time
            </span>
        </label>
    );
};

ToggleSwitch.propTypes = {
    ariaLabel: PropTypes.string.isRequired,
    activeLength: PropTypes.bool.isRequired,
};

export default ToggleSwitch;
