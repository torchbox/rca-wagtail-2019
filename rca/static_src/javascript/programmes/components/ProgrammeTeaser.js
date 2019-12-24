import React from 'react';

import { programmePageShape } from '../programmes.types';

/**
 * A programme’s teaser info, to be displayed as part of search results.
 */
const ProgrammeTeaser = ({ programme }) => {
    const {
        meta,
        title,
        degree_level,
        programme_description_subtitle,
        pathway_blocks,
        hero_image_square,
    } = programme;

    return (
        <a href={meta.html_url} className="programme-teaser">
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
            <div className="programme-teaser__description">
                <p>{programme_description_subtitle}</p>
                {pathway_blocks.length > 0 ? (
                    <div>
                        <p>Pathways:</p>
                        <p>
                            {pathway_blocks
                                .map((b) => b.value.heading)
                                .join(', ')}
                        </p>
                    </div>
                ) : null}
            </div>
            <div className="programme-teaser__image-wrapper">
                <img
                    className="programme-teaser__image"
                    src={hero_image_square.url}
                    width={hero_image_square.width}
                    height={hero_image_square.height}
                    alt=""
                />
            </div>
        </a>
    );
};

ProgrammeTeaser.propTypes = {
    programme: programmePageShape.isRequired,
};

ProgrammeTeaser.defaultProps = {};

export default ProgrammeTeaser;
