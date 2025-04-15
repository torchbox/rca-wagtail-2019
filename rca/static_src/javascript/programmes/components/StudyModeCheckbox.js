import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import { getCourseLengthURL, pushState } from '../programmes.routes';
import { useStudyMode } from '../context/StudyModeContext';

const ModeCheckbox = ({ ariaLabel }) => {
    const { isFullTime, setIsFullTime, isPartTime, setIsPartTime } =
        useStudyMode();
    const [showError, setShowError] = useState(false);

    useEffect(() => {
        // Hide error when at least one checkbox is checked
        setShowError(isFullTime !== 'true' && isPartTime !== 'true');

        // Update the URL with the new Part-time value
        const url = getCourseLengthURL(isFullTime, isPartTime);
        pushState(url);
    }, [isFullTime, isPartTime]);

    return (
        <div
            className={`mode-checkbox ${
                showError ? 'mode-checkbox--error' : ''
            }`}
            aria-label={ariaLabel}
        >
            {showError && (
                <div className="mode-checkbox__error">
                    Please select a full-time or part-time option.
                </div>
            )}
            <div className="mode-checkbox__formset">
                <label
                    htmlFor="is-full-time"
                    className={`mode-checkbox__label${
                        isFullTime ? ' mode-checkbox__label--selected' : ''
                    }`}
                    data-label="full-time"
                >
                    <input
                        type="checkbox"
                        className={`mode-checkbox__checkbox${
                            showError ? ' mode-checkbox__checkbox--error' : ''
                        }`}
                        id="is-full-time"
                        checked={isFullTime === 'true'}
                        onChange={() =>
                            setIsFullTime(
                                isFullTime === 'true' ? 'false' : 'true',
                            )
                        }
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
                        className={`mode-checkbox__checkbox${
                            showError ? ' mode-checkbox__checkbox--error' : ''
                        }`}
                        id="is-part-time"
                        checked={isPartTime === 'true'}
                        onChange={() =>
                            setIsPartTime(
                                isPartTime === 'true' ? 'false' : 'true',
                            )
                        }
                    />
                    Part-time
                </label>
            </div>
        </div>
    );
};

ModeCheckbox.propTypes = {
    ariaLabel: PropTypes.string.isRequired,
};

export default ModeCheckbox;
