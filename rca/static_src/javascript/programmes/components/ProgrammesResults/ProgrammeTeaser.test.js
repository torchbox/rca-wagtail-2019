import React from 'react';
import { shallow } from 'enzyme';

import ProgrammeTeaser from './ProgrammeTeaser';

const getMock = (type = 'Page', overrides = {}, id = 4) => ({
    id,
    meta: {
        type,
        detail_url: 'http://localhost/api/v3/pages/63/',
        html_url: 'http://localhost/study/courses/architecture-summer-school/',
        slug: 'architecture-summer-school',
        first_published_at: '2020-04-27T12:38:20.275294+01:00',
    },
    title: 'Title summer school',
    summary: 'Summary intense and immersive',
    hero_image_square: {
        url: '/media/images/soa_summer_course_image.fill-580x580.jpg',
        width: 580,
        height: 580,
    },
    ...overrides,
});

const getMockShortCourse = getMock.bind(null, 'shortcourses.ShortCoursePage');
const getMockProgramme = getMock.bind(null, 'programmes.ProgrammePage', {
    degree_level: { id: 6, title: 'MA' },
    pathway_blocks: [
        {
            id: '586e1b58-c8b3-4077-9577-02b727e12cbc',
            type: 'accordion_block',
            value: {
                heading: 'Exhibition Design',
                preview_text: 'Preview text',
                body: '<p>Body text</p>',
                link: { title: '', url: '' },
            },
        },
    ],
});

describe('ProgrammeTeaser', () => {
    it('renders short course page', () => {
        expect(
            shallow(
                <ProgrammeTeaser
                    programme={getMockShortCourse()}
                    onMouseOver={() => {}}
                    onFocus={() => {}}
                />,
            ).text(),
        ).toMatchInlineSnapshot(
            `"Title summer schoolShort courseSummary intense and immersive"`,
        );
    });

    it('renders programme page', () => {
        expect(
            shallow(
                <ProgrammeTeaser
                    programme={getMockProgramme()}
                    onMouseOver={() => {}}
                    onFocus={() => {}}
                />,
            ).text(),
        ).toMatchInlineSnapshot(
            `"Title summer schoolMASummary intense and immersivePathways:Exhibition Design"`,
        );
    });

    it('renders programme page without pathways', () => {
        expect(
            shallow(
                <ProgrammeTeaser
                    programme={{ ...getMockProgramme(), pathway_blocks: [] }}
                    onMouseOver={() => {}}
                    onFocus={() => {}}
                />,
            ).text(),
        ).not.toContain('Pathways:');
    });
});
