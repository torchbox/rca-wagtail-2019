const legacyCode = {
    'class-methods-use-this': 0,
    'consistent-return': 0,
    'eqeqeq': 0,
    'no-console': 0,
    'no-unused-vars': 0,
    'prefer-destructuring': 0,
};

// Rules which point out patterns that are commonly sources of bugs.
const sourcesOfBugs = {
    radix: 0,
};

module.exports = {
    // See https://github.com/torchbox/eslint-config-torchbox for rules.
    extends: 'torchbox',
    parser: 'babel-eslint',
    rules: {
        ...legacyCode,
        ...sourcesOfBugs,
    },
};
