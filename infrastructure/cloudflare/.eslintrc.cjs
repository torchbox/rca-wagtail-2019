module.exports = {
    root: true,
    extends: 'eslint:recommended',
    parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
    },
    env: {
        es2022: true,
        worker: true,
    },
    overrides: [
        {
            files: ['.eslintrc.cjs', 'tests/*.mjs'],
            env: {
                node: true,
            },
        },
    ],
};
