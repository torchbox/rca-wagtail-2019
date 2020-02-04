import React from 'react';
import ReactDOM from 'react-dom';

import TestReact from './test-react';

describe('TestReact', () => {
    it('renders', () => {
        const mount = document.createElement('div');
        document.body.appendChild(mount);

        ReactDOM.render(<TestReact greeting="potato" />, mount);

        expect(mount.innerHTML).toContain('The greeting is potato');
    });
});
