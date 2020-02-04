import React from 'react';
import { shallow } from 'enzyme';
import Icon from './Icon';

describe('Icon', () => {
    it('renders', () => {
        expect(shallow(<Icon name="rocket" />)).toMatchInlineSnapshot(`
            <svg
              aria-hidden="true"
              className={null}
              height={null}
              width={null}
            >
              <use
                xlinkHref="#rocket"
              />
            </svg>
        `);
    });

    it('#className', () => {
        expect(shallow(<Icon name="rocket" className="button__icon" />))
            .toMatchInlineSnapshot(`
            <svg
              aria-hidden="true"
              className="button__icon"
              height={null}
              width={null}
            >
              <use
                xlinkHref="#rocket"
              />
            </svg>
        `);
    });

    it('#width and #height', () => {
        expect(shallow(<Icon name="rocket" width="12px" height="8px" />))
            .toMatchInlineSnapshot(`
            <svg
              aria-hidden="true"
              className={null}
              height="8px"
              width="12px"
            >
              <use
                xlinkHref="#rocket"
              />
            </svg>
        `);
    });
});
