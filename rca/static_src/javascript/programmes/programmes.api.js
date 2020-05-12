import PropTypes from 'prop-types';

import { programmePage } from './programmes.types';

const PROGRAMME_TYPE = 'programmes.ProgrammePage';
const SHORT_COURSE_TYPE = 'shortcourses.ShortCoursePage';
const PROGRAMME_FIELDS = [
    'degree_level',
    'programme_description_subtitle',
    'pathway_blocks',
    'hero_image_square',
];
const SHORT_COURSE_FIELDS = ['introduction', 'hero_image_square'];

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
    // Abort the previous controller if any, and create a new one.
    abortGetProgrammes.abort();
    abortGetProgrammes = new AbortController();

    const requests = [
        { type: PROGRAMME_TYPE, fields: PROGRAMME_FIELDS },
        { type: SHORT_COURSE_TYPE, fields: SHORT_COURSE_FIELDS },
    ].map(({ type, fields }) => {
        const queryString = getWagtailAPIQueryString({
            search: query,
            filters,
            type,
            fields,
            limit: 50,
        });
        const url = `${WAGTAIL_API_ENDPOINT}${queryString}`;

        return fetch(url, {
            signal: abortGetProgrammes.signal,
        }).then((response) => response.json());
    });

    return Promise.all(requests).then((results) => {
        const items = results.reduce((all, res) => all.concat(res.items), []);
        // Use prop-types definitions to check that the API response matches what we expect.
        if (process.env.NODE_ENV === 'development') {
            items.forEach((item) => {
                PropTypes.checkPropTypes(programmePage, item, '', 'API client');
            });
        }

        return items;
    });
};
