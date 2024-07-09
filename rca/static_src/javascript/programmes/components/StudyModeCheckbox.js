import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import { getCourseLengthURL, pushState } from '../programmes.routes';

const ModeCheckbox = ({ ariaLabel, isFullTime, isPartTime }) => {
    const [_isFullTime, setIsFullTime] = useState(isFullTime);
    const [_isPartTime, setIsPartTime] = useState(isPartTime);
    const [showError, setShowError] = useState(false);

    useEffect(() => {
        // Hide error when at least one checkbox is checked
        setShowError(!_isFullTime && !_isPartTime);

        // Update the URL with the new Part-time value
        const url = getCourseLengthURL(
            String(_isFullTime),
            String(_isPartTime),
        );
        pushState(url);
    }, [_isFullTime, _isPartTime]);

    return (
        <div className="mode-checkbox__panel">
            <div className="mode-checkbox__wrapper">
                <div className="grid">
                    <div className="mode-checkbox" aria-label={ariaLabel}>
                        {showError && (
                            <div className="mode-checkbox__error">
                                You must select at least one mode of study.
                            </div>
                        )}
                        <div className="mode-checkbox__formset">
                            <label
                                htmlFor="is-full-time"
                                className={`mode-checkbox__label${
                                    _isFullTime
                                        ? ' mode-checkbox__label--selected'
                                        : ''
                                }`}
                                data-label="full-time"
                            >
                                <input
                                    type="checkbox"
                                    className={`mode-checkbox__checkbox${
                                        showError
                                            ? ' mode-checkbox__checkbox--error'
                                            : ''
                                    }`}
                                    id="is-full-time"
                                    checked={_isFullTime}
                                    onChange={() => setIsFullTime(!_isFullTime)}
                                />
                                Full-time
                            </label>
                            <label
                                htmlFor="is-part-time"
                                className={`mode-checkbox__label${
                                    _isPartTime
                                        ? ' mode-checkbox__label--selected'
                                        : ''
                                }`}
                                data-label="part-time"
                            >
                                <input
                                    type="checkbox"
                                    className={`mode-checkbox__checkbox${
                                        showError
                                            ? ' mode-checkbox__checkbox--error'
                                            : ''
                                    }`}
                                    id="is-part-time"
                                    checked={_isPartTime}
                                    onChange={() => setIsPartTime(!_isPartTime)}
                                />
                                Part-time
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

ModeCheckbox.propTypes = {
    ariaLabel: PropTypes.string.isRequired,
    isFullTime: PropTypes.bool.isRequired,
    isPartTime: PropTypes.bool.isRequired,
};

export default ModeCheckbox;
