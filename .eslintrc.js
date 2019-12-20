const legacyCode = {
    'class-methods-use-this': 0,
    'consistent-return': 0,
    'eqeqeq': 0,
    'func-names': 0,
    'new-cap': 0,
    'no-console': 0,
    'no-empty': 0,
    'no-new': 0,
    'no-restricted-syntax': 0,
    'no-unused-vars': 0,
    'no-use-before-define': 0,
    'prefer-destructuring': 0,
    'radix': 0,
    'react/destructuring-assignment': 0,
    'react/prop-types': 0,
};

module.exports = {
    // See https://github.com/torchbox/eslint-config-torchbox for rules.
    extends: 'torchbox',
    parser: 'babel-eslint',
    rules: {
        ...legacyCode,
    },
};
