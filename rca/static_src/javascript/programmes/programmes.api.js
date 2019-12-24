import PropTypes from 'prop-types';

import { programmePage } from './programmes.types';

const PROGRAMME_TYPE = 'programmes.ProgrammePage';
const PROGRAMME_FIELDS = [
    'degree_level',
    'programme_description_subtitle',
    'pathway_blocks',
    'hero_image_square',
].join(',');

const PROGRAMMES_ENDPOINT = `/api/v2/pages?type=${PROGRAMME_TYPE}&fields=${PROGRAMME_FIELDS}&limit=50`;

let abortGetProgrammes = new AbortController();

/**
 * Retrieve programmes based on:
 * @param {string} query – a textual search query.
 * @param {object} filters – A key-val mapping of filters.
 * Or both!
 */
export const getProgrammes = ({ query, filters = {} }) => {
    const search = query ? `&search=${window.encodeURIComponent(query)}` : '';

    const additionalFilters = Object.entries(filters)
        .map(([filter, value]) => {
            return `&${filter}=${window.encodeURIComponent(value)}`;
        })
        .join('');

    const url = `${PROGRAMMES_ENDPOINT}${search}${additionalFilters}`;

    // Abort the previous controller if any, and create a new one.
    abortGetProgrammes.abort();
    abortGetProgrammes = new AbortController();

    return fetch(url, { signal: abortGetProgrammes.signal })
        .then((res) => res.json())
        .then((result) => {
            if (process.env.NODE_ENV === 'development') {
                result.items.forEach((item) => {
                    PropTypes.checkPropTypes(
                        programmePage,
                        item,
                        '',
                        'API client',
                    );
                });
            }

            return result.items;
        });
};
