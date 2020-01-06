import React from 'react';
import PropTypes from 'prop-types';

import { programmePageShape } from '../../programmes.types';

/**
 * A programme’s teaser info, to be displayed as part of search results.
 */
const ProgrammeTeaser = ({ programme, onMouseOver, onFocus }) => {
    const {
        meta,
        title,
        degree_level,
        programme_description_subtitle,
        pathway_blocks,
    } = programme;

    return (
        <a
            href={meta.html_url}
            className="programme-teaser"
            onMouseOver={onMouseOver}
            onFocus={onFocus}
        >
            <div className="programme-teaser__title">
                <h2 className="programme-teaser__heading heading heading--five">
                    <span className="programme-teaser__heading-inner">
                        {title}
                    </span>
                </h2>
                <small className="programme-teaser__degree">
                    {degree_level.title}
                </small>
            </div>
            <div className="programme-teaser__info">
                <p className="programme-teaser__description body body--one">
                    {programme_description_subtitle}
                </p>
                {pathway_blocks.length > 0 ? (
                    <div>
                        <p className="programme-teaser__pathways-heading">
                            Pathways:
                        </p>
                        <p className="programme-teaser__pathways-text">
                            {pathway_blocks
                                .map((b) => b.value.heading)
                                .join(', ')}
                        </p>
                    </div>
                ) : null}
            </div>
        </a>
    );
};

ProgrammeTeaser.propTypes = {
    programme: programmePageShape.isRequired,
    onMouseOver: PropTypes.func.isRequired,
    onFocus: PropTypes.func.isRequired,
};

export default ProgrammeTeaser;
