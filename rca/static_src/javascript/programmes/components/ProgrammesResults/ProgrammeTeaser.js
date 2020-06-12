import React from 'react';
import PropTypes from 'prop-types';

import {
    SHORT_COURSE_PAGE_TYPE,
    programmePageShape,
} from '../../programmes.types';

/**
 * A programme or short course’s teaser info, to be displayed as part of search results.
 * "Degree level" and "Pathway blocks" are for programmes only. Other fields are shared.
 */
const ProgrammeTeaser = ({ programme, onMouseOver, onFocus }) => {
    const { meta, title, summary, degree_level, pathway_blocks } = programme;
    const isShortCourse = meta.type === SHORT_COURSE_PAGE_TYPE;
    // Short courses have no degree level. Display a distinguishing label instead.
    const degreeLabel = isShortCourse ? 'Short course' : degree_level.title;

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
                    {degreeLabel}
                </small>
            </div>
            <div className="programme-teaser__info">
                <p className="programme-teaser__description body body--one">
                    {summary}
                </p>
                {pathway_blocks && pathway_blocks.length > 0 ? (
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
