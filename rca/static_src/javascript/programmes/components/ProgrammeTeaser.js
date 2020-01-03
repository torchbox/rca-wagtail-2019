import React from 'react';

import { programmePageShape } from '../programmes.types';

const ProgrammeTeaser = ({ programme }) => {
    const {
        meta,
        title,
        degree_level,
        programme_description_title,
        pathway_blocks,
        hero_image_square,
    } = programme;

    return (
        <a href={meta.html_url} className="programme-teaser">
            <div className="programme-teaser__heading">
                <h2 className="heading heading--five">
                    <span className="programme-teaser__heading-inner">
                        {title}
                    </span>
                </h2>
                <p>{degree_level.title}</p>
            </div>
            <div className="programme-teaser__description">
                <p>{programme_description_title}</p>
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
