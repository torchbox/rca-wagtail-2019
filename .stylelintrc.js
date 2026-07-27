module.exports = {
    // See https://github.com/torchbox/stylelint-config-torchbox for rules.
    extends: 'stylelint-config-torchbox',
    rules: {
        'max-nesting-depth': null,
        'selector-max-specificity': null,
        'declaration-no-important': null,
        'comment-whitespace-inside': null,
        'selector-class-pattern': null,
        // stylelint-config-torchbox v5 moved the BEM class-name check to the
        // SCSS-aware scss/selector-class-pattern rule; disable it too to keep
        // the project's existing "don't enforce class naming" stance.
        'scss/selector-class-pattern': null,
        'scale-unlimited/declaration-strict-value': null,
        'scss/operator-no-newline-after': null,
        'nesting-selector-no-missing-scoping-root': null,
    },
};
