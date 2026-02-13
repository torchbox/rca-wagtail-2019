const legacyCode = {
    'class-methods-use-this': 0,
};

module.exports = {
    // See https://github.com/torchbox/eslint-config-torchbox for rules.
    extends: 'torchbox',
    parser: '@babel/eslint-parser',
    parserOptions: {
        requireConfigFile: true,
        babelOptions: {
            configFile: './.babelrc.js',
        },
    },
    rules: {
        ...legacyCode,
        'react/jsx-no-constructed-context-values': 'warn',
        'react-hooks/exhaustive-deps': 'warn',
    },
};
