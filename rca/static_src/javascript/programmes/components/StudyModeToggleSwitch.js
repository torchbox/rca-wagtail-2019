import PropTypes from 'prop-types';
import React from 'react';

const ToggleSwitch = ({ ariaLabel, labelOne, labelTwo }) => {
    return (
        // eslint-disable-next-line jsx-a11y/label-has-associated-control
        <label
            className="toggle-switch"
            data-study-mode-toggle
            aria-label={ariaLabel}
        >
            <input type="checkbox" className="toggle-switch__checkbox" />
            <span className="toggle-switch__switch" />
            <span className="toggle-switch__label toggle-switch__label--first">
                {labelOne}
            </span>
            <span className="toggle-switch__label toggle-switch__label--last">
                {labelTwo}
            </span>
        </label>
    );
};

ToggleSwitch.propTypes = {
    ariaLabel: PropTypes.string.isRequired,
    labelOne: PropTypes.string.isRequired,
    labelTwo: PropTypes.string.isRequired,
};

export default ToggleSwitch;
