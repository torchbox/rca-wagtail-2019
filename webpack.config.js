const path = require('path');
const autoprefixer = require('autoprefixer');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const postcssCustomProperties = require('postcss-custom-properties');
const sass = require('sass');

const projectRoot = 'rca';

const options = {
    entry: {
        // nultiple entries can be added here
        main: `./${projectRoot}/static_src/javascript/main.entry.js`,
        programmes: `./${projectRoot}/static_src/javascript/programmes/programmes.entry.js`,
    },
    output: {
        path: path.resolve(`./${projectRoot}/static_compiled/`),
        // based on entry name, e.g. main.js
        filename: 'js/[name].js', // based on entry name, e.g. main.js
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'css/[name].css',
        }),
    ],
    module: {
        rules: [
            {
                // tells webpack how to handle js and jsx files
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                },
            },
            {
                test: /\.(scss|css)$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: true,
                            url: false,
                        },
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: true,
                            plugins: () => [
                                autoprefixer(),
                                postcssCustomProperties(),
                            ],
                        },
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: true,
                            outputStyle: 'compressed',
                            implementation: sass,
                        },
                    },
                ],
            },
        ],
    },
    // externals are loaded via base.html and not included in the webpack bundle.
    externals: {
        // gettext: 'gettext',
    },
};

/*
  If a project requires internationalisation, then include `gettext` in base.html
    via the Django JSi18n helper, and uncomment it from the 'externals' object above.
*/

if (process.env.NODE_ENV === 'development') {
    // Create JS source maps in the dev mode
    // See https://webpack.js.org/configuration/devtool/ for more options
    options.devtool = 'inline-source-map';
}

module.exports = options;
