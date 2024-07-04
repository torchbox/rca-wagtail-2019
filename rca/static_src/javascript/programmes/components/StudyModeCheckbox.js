import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import { getCourseLengthURL, pushState } from '../programmes.routes';

const ModeCheckbox = ({ ariaLabel, isFullTime, isPartTime }) => {
    const [_isFullTime, setIsFullTime] = useState(isFullTime);
    const [_isPartTime, setIsPartTime] = useState(isPartTime);

    useEffect(() => {
        // Update the URL with the new Part-time value
        const url = getCourseLengthURL(
            String(_isFullTime),
            String(_isPartTime),
        );
        pushState(url);
    }, [_isFullTime, _isPartTime]);

    return (
        <div className="mode-checkbox" aria-label={ariaLabel}>
            <input
                type="checkbox"
                className="mode-checkbox__checkbox"
                id="is-full-time"
                checked={_isFullTime}
                onChange={() => setIsFullTime(!_isFullTime)}
            />
            <label
                htmlFor="is-full-time"
                className={`mode-checkbox__label${
                    _isFullTime ? ' mode-checkbox__label--selected' : ''
                }`}
                data-label="full-time"
            >
                Full-time
            </label>
            <input
                type="checkbox"
                className="mode-checkbox__checkbox"
                id="is-part-time"
                checked={_isPartTime}
                onChange={() => setIsPartTime(!_isPartTime)}
            />
            <label
                htmlFor="is-part-time"
                className={`mode-checkbox__label${
                    _isPartTime ? ' mode-checkbox__label--selected' : ''
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
    isFullTime: PropTypes.bool.isRequired,
    isPartTime: PropTypes.bool.isRequired,
};

export default ModeCheckbox;
