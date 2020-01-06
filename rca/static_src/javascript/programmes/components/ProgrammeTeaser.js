import React from 'react';

import { programmePageShape } from '../programmes.types';

/**
 * A programme’s teaser info, to be displayed as part of search results.
 */
const ProgrammeTeaser = ({ programme }) => {
    const { meta, title } = programme;

    return (
        <div>
            <a href={meta.html_url} className="programme-teaser">
                {title}
            </a>
        </div>
    );
};

ProgrammeTeaser.propTypes = {
    programme: programmePageShape.isRequired,
};

export default ProgrammeTeaser;
