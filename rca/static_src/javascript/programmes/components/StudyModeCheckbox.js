import PropTypes from 'prop-types';
import React, { useState } from 'react';

import { getCourseLengthURL, pushState } from '../programmes.routes';

const ModeCheckbox = ({ ariaLabel, activeLength }) => {
    const [isPartTime, setIsPartTime] = useState(activeLength);

    const handleToggle = () => {
        setIsPartTime(!isPartTime);

        // Update the URL with the new Part-time value
        const url = getCourseLengthURL(isPartTime ? '' : 'true');
        pushState(url);
    };

    return (
        <div className="mode-checkbox" aria-label={ariaLabel}>
            <label
                htmlFor="is-full-time"
                className={`mode-checkbox__label${
                    !isPartTime ? ' mode-checkbox__label--selected' : ''
                }`}
                data-label="full-time"
            >
                <input
                    type="checkbox"
                    className="mode-checkbox__checkbox"
                    id="is-full-time"
                    checked={!isPartTime}
                    onChange={handleToggle}
                />
                Full-time
            </label>
            <label
                htmlFor="is-part-time"
                className={`mode-checkbox__label${
                    isPartTime ? ' mode-checkbox__label--selected' : ''
                }`}
                data-label="part-time"
            >
                <input
                    type="checkbox"
                    className="mode-checkbox__checkbox"
                    id="is-part-time"
                    checked={isPartTime}
                    onChange={handleToggle}
                />
                Part-time
            </label>
        </div>
    );
};

ModeCheckbox.propTypes = {
    ariaLabel: PropTypes.string.isRequired,
    activeLength: PropTypes.bool.isRequired,
};

export default ModeCheckbox;
