import PropTypes from 'prop-types';

import {
    PROGRAMME_PAGE_TYPE,
    SHORT_COURSE_PAGE_TYPE,
    programmePage,
} from './programmes.types';

const WAGTAIL_API_ENDPOINT = '/api/v3/pages';

/**
 * The programmes API queries multiple page types, with different fields for each.
 * This array also determines the order in which the instances are displayed.
 */
const listedPageTypes = [
    {
        type: PROGRAMME_PAGE_TYPE,
        fields: [
            'summary',
            'hero_image_square',
            'degree_level',
            'pathway_blocks',
        ],
    },
    {
        type: SHORT_COURSE_PAGE_TYPE,
        fields: ['summary', 'hero_image_square'],
    },
];

/**
 * Generates a Wagtail API query string based on the given attributes.
 */
export const getWagtailAPIQueryString = ({
    search,
    filters,
    type,
    fields,
    limit,
    fullTime,
    partTime,
}) => {
    const parameters = {
        'type': type || null,
        'full-time': fullTime !== undefined ? fullTime : 'false',
        'part-time': partTime !== undefined ? partTime : 'false',
        'limit': limit || null,
        'fields': fields.join(',') || null,
        'search': search || null,
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
 * Retrieve programme and short course pages based on:
 * @param {string} query – a textual search query.
 * @param {object} filters – A key-val mapping of filters.
 * Or both!
 */
export const getProgrammes = ({ query, filters = {} }) => {
    // Check the window for a part-time query param and apply that.
    const urlParams = new URLSearchParams(window.location.search);
    const fullTimeParam = urlParams.get('full-time');
    const partTimeParam = urlParams.get('part-time');
    const fullTime = fullTimeParam === 'true';
    const partTime = partTimeParam === 'true';

    // Abort the previous controller if any, and create a new one.
    abortGetProgrammes.abort();
    abortGetProgrammes = new AbortController();

    if (!fullTime && !partTime) {
        return Promise.resolve([]);
    }

    const requests = listedPageTypes.map(({ type, fields }) => {
        const queryString = getWagtailAPIQueryString({
            search: query,
            // Pass the fullTime and partTime values to the query string generator.
            fullTime,
            partTime,
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
        items.sort((a, b) => {
            const fa = a.title.toLowerCase();
            const fb = b.title.toLowerCase();
            if (fa < fb) {
                return -1;
            }
            if (fa > fb) {
                return 1;
            }
            return 0;
        });
        // Use prop-types definitions to check that the API response matches what we expect.
        if (process.env.NODE_ENV === 'development') {
            items.forEach((item) => {
                PropTypes.checkPropTypes(programmePage, item, '', 'API client');
            });
        }

        return items;
    });
};
