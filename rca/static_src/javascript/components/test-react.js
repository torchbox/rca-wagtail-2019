import React, { Component } from 'react';

// Tests that react is working in a new build
export default class TestReact extends Component {
    constructor(props) {
        super(props);

        this.state = {
            greeting: props.greeting,
        };
    }

    render() {
        const message = `The greeting is ${this.state.greeting}`;

        return (
            <div>
                <p className="test">{message}</p>
            </div>
        );
    }
}
