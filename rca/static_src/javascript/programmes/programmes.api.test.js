import { getWagtailAPIQueryString } from './programmes.api';

describe('getWagtailAPIQueryString', () => {
    const empty = {
        search: '',
        filters: {},
        type: '',
        fields: [],
        limit: null,
        partTime: undefined,
    };

    it('empty', () => {
        expect(getWagtailAPIQueryString(empty)).toBe('?part-time=false');
    });

    it('all options', () => {
        expect(
            getWagtailAPIQueryString({
                type: 'core.TestPage',
                limit: 50,
                search: 'test',
                fields: ['test', 'title'],
                filters: { promoted: true, price: 15 },
                partTime: 'true',
            }),
        ).toBe(
            '?type=core.TestPage&part-time=true&limit=50&fields=test%2Ctitle&search=test&promoted=true&price=15',
        );
    });
});
