const path = require('path');
const autoprefixer = require('autoprefixer');
const cssnano = require('cssnano');
const CopyPlugin = require('copy-webpack-plugin');
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
        new CopyPlugin([
            {
                // Copy images to be referenced directly by Django to the "images" subfolder in static files.
                // Ignore CSS background images as these are handled separately below
                from: 'images',
                context: path.resolve(`./${projectRoot}/static_src/`),
                to: path.resolve(`./${projectRoot}/static_compiled/images`),
                ignore: ['cssBackgrounds/*'],
            },
        ]),
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
                                cssnano({
                                    preset: 'default',
                                }),
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
const webpackConfig = (environment, argv) => {
    const isProduction = argv.mode === 'production';

    options.mode = isProduction ? 'production' : 'development';

    if (!isProduction) {
        // https://webpack.js.org/configuration/stats/
        const stats = {
            // Tells stats whether to add the build date and the build time information.
            builtAt: false,
            // Add chunk information (setting this to `false` allows for a less verbose output)
            chunks: false,
            // Add the hash of the compilation
            hash: false,
            // `webpack --colors` equivalent
            colors: true,
            // Add information about the reasons why modules are included
            reasons: false,
            // Add webpack version information
            version: false,
            // Add built modules information
            modules: false,
            // Show performance hint when file size exceeds `performance.maxAssetSize`
            performance: false,
            // Add children information
            children: false,
            // Add asset Information.
            assets: false,
        };

        options.stats = stats;

        // Create JS source maps in the dev mode
        // See https://webpack.js.org/configuration/devtool/ for more options
        options.devtool = 'inline-source-map';

        const PROXY_HOST = process.env.PROXY_HOST || '0.0.0.0';
        const PROXY_PORT = process.env.PROXY_PORT || '8000';

        // See https://webpack.js.org/configuration/dev-server/.
        options.devServer = {
            // Enable gzip compression for everything served.
            compress: true,
            // Shows a full-screen overlay in the browser when there are compiler errors.
            overlay: true,
            clientLogLevel: 'error',
            contentBase: false,
            // Write compiled files to disk. This makes live-reload work on both port 3000 and 8000.
            writeToDisk: true,
            host: '0.0.0.0',
            allowedHosts: [],
            port: 3000,
            publicPath: '/static/',
            index: '',
            stats,
            proxy: {
                context: () => true,
                target: `http://${PROXY_HOST}:${PROXY_PORT}`,
            },
        };
    }

    return options;
};

module.exports = webpackConfig;
