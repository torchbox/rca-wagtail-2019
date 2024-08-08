import { getWagtailAPIQueryString } from './programmes.api';

describe('getWagtailAPIQueryString', () => {
    const empty = {
        search: '',
        filters: {},
        type: '',
        fields: [],
        limit: null,
        fullTime: undefined,
        partTime: undefined,
    };

    it('empty', () => {
        expect(getWagtailAPIQueryString(empty)).toBe(
            '?full-time=false&part-time=false',
        );
    });

    it('all options', () => {
        expect(
            getWagtailAPIQueryString({
                type: 'core.TestPage',
                limit: 50,
                search: 'test',
                fields: ['test', 'title'],
                filters: { promoted: true, price: 15 },
                fullTime: 'true',
                partTime: 'true',
            }),
        ).toBe(
            '?type=core.TestPage&full-time=true&part-time=true&limit=50&fields=test%2Ctitle&search=test&promoted=true&price=15',
        );
    });
});
