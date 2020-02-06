import PropTypes from 'prop-types';

import { programmePage } from './programmes.types';

const PROGRAMME_TYPE = 'programmes.ProgrammePage';
const PROGRAMME_FIELDS = [
    'degree_level',
    'programme_description_subtitle',
    'pathway_blocks',
    'hero_image_square',
];

const WAGTAIL_API_ENDPOINT = '/api/v3/pages';

/**
 * Generates a Wagtail API query string based on the given attributes.
 */
export const getWagtailAPIQueryString = ({
    search,
    filters,
    type,
    fields,
    limit,
}) => {
    const parameters = {
        type: type || null,
        limit: limit || null,
        fields: fields.join(',') || null,
        search: search || null,
        ...filters,
    };
    Object.keys(parameters).forEach((param) => {
        if (parameters[param] === null) {
            delete parameters[param];
        }
    });

    const str = new URLSearchParams(parameters).toString();
    return `${str ? '?' : ''}${str}`;
};

let abortGetProgrammes = new AbortController();

/**
 * Retrieve programmes based on:
 * @param {string} query – a textual search query.
 * @param {object} filters – A key-val mapping of filters.
 * Or both!
 */
export const getProgrammes = ({ query, filters = {} }) => {
    const queryString = getWagtailAPIQueryString({
        search: query,
        filters,
        type: PROGRAMME_TYPE,
        fields: PROGRAMME_FIELDS,
        limit: 50,
    });
    const url = `${WAGTAIL_API_ENDPOINT}${queryString}`;

    // Abort the previous controller if any, and create a new one.
    abortGetProgrammes.abort();
    abortGetProgrammes = new AbortController();

    return fetch(url, { signal: abortGetProgrammes.signal })
        .then((res) => res.json())
        .then((result) => {
            // Use prop-types definitions to check that the API response matches what we expect.
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
