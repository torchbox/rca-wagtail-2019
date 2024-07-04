import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import { getCourseLengthURL, pushState } from '../programmes.routes';

const ModeCheckbox = ({ ariaLabel, activeLength }) => {
    const [isFullTime, setIsFullTime] = useState(false);
    const [isPartTime, setIsPartTime] = useState(false);

    useEffect(() => {
        console.log('Full-time');
    }, [isFullTime]);

    useEffect(() => {
        console.log('Part-time');
    }, [isPartTime]);

    return (
        <div className="mode-checkbox" aria-label={ariaLabel}>
            <input
                type="checkbox"
                className="mode-checkbox__checkbox"
                id="is-full-time"
                checked={isFullTime}
                onChange={(e) => setIsFullTime(!isFullTime)}
            />
            <label
                htmlFor="is-full-time"
                className={`mode-checkbox__label${
                    isFullTime ? ' mode-checkbox__label--selected' : ''
                }`}
                data-label="full-time"
            >
                Full-time
            </label>
            <input
                type="checkbox"
                className="mode-checkbox__checkbox"
                id="is-part-time"
                checked={isPartTime}
                onChange={(e) => setIsPartTime(!isPartTime)}
            />
            <label
                htmlFor="is-part-time"
                className={`mode-checkbox__label${
                    isPartTime ? ' mode-checkbox__label--selected' : ''
                }`}
                data-label="part-time"
            >
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
