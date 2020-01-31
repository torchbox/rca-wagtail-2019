# Front end tooling

This set of tooling should form the basis for any new wagtail projects. It can also be used for custom django builds - simply copy the `static_src` directory from here to your build.

## What's required

You can run the tooling within the VM where Node.js is pre-installed, but if you are using Mac OS, you will likely have issues with performance of `npm install` and other `npm` commands. It is adviced to Mac OS users to have node on the host machine.
To install node on the host machine we recommend using [`nvm`](https://github.com/creationix/nvm). Once you have `nvm` installed simply run `nvm install` to install and activate the version of node required for the project. Refer to the [`nvm` documentation](https://github.com/creationix/nvm#usage) for more details about available commands.

## What's included

- [Sass](http://sass-lang.com/) CSS with [auto-prefixing](https://github.com/postcss/autoprefixer).
- [Babel](https://babeljs.io) for ES2015+ support.
- [Browsersync](https://www.browsersync.io) for autoreloading.
- [Webpack](https://webpack.js.org/) for module bundling.
  - With `babel-loader` to process JavaScript.
  - With `css-loader`, `postcss-loader`, and `sass-loader` to process stylesheets.
- Consideration for images, currently copying the directory only - to avoid slowdowns and non-essential dependancies. We encourage using SVG for UI vectors and pre-optimised UI photograph assets.
- [Build commands](#build-scripts) for generating testable or deployable assets only
- Sass linting with `sass-lint`
- JS linting with `eslint`
- [Jest](https://jestjs.io/) for JavaScript unit tests.
- React support

## Developing with it

- To start the development environment, run `npm start` - to stop this process press `ctrl + c`.
- This will start Browsersync and make the project available at `http://localhost:3000/html/`. If another process is using this port, check terminal for an updated URL. You can change this configuation by modifying the `browsersync.config.js` file, documented here https://www.browsersync.io/docs/options.
- Source files for developing your project are in `static_src` and the distribution folder for the compiled assets is `static_compiled`. Don't make direct changes to the `static_compiled` directory as they will be overwritten.

### Using npm

- Install all packages from `package.json`: `npm install`
- Add new packages that are only required for development, e.g. tooling: `npm install --save-dev package_name` (this will add it to `package.json` and `package-lock.json` too)
- Add new packages required in production, e.g. react: `npm install --save-prod package_name`
- To upgrade packages run `npm update package_name` or `npm update` to update them all.

## Tests

JavaScript unit tests for this project use [Jest](https://jestjs.io/). Here are commands you can use:

```sh
# Run the whole test suite once.
npm run test
# Run the whole test suite, collecting test coverage information.
npm run test:coverage
# Start Jest in watch mode, to run tests on a subset of the files.
npm run test:watch
```

## Deploying it

### Build scripts

To only build assets for either development or production you can use

- `npm run build` To build development assets
- `npm run build:prod` To build assets with minification and vendor prefixes

### Debug script

To test production, minified and vendor prefixed assets you can use

- `npm run debug` To develop with a simple http server, no browsersync and production assets
