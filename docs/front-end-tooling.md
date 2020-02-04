# Front end tooling

This set of tooling should form the basis for any new wagtail projects. It can also be used for custom django builds - simply copy the `static_src` directory from here to your build.

## What's required

You can run the tooling within the VM where Node.js is pre-installed, but if you are using Mac OS, you will likely have issues with performance of `npm install` and other `npm` commands. It is adviced to Mac OS users to have node on the host machine.
To install node on the host machine we recommend using [`nvm`](https://github.com/creationix/nvm). Once you have `nvm` installed simply run `nvm install` to install and activate the version of node required for the project. Refer to the [`nvm` documentation](https://github.com/creationix/nvm#usage) for more details about available commands.

## Setting up a new project from the wagtail-kit tooling

The wagtail-kit tooling is versioned via `package.json`, and the `package-lock.json` lockfile pins all of the project’s direct and transitive dependencies. If you wish to start the project with up to date dependencies without doing manual upgrades, you can discard the lockfile and re-create it:

```sh
rm -rf node_modules
rm package-lock.json
npm install
```

Remember to then commit the updated `package-lock.json`.

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

## React support

The wagtail-kit tooling now supports react out of the box.

Note that react is installed as a dependency and imported via main.js.

You can test that compilation of react is working by uncommenting the relevant lines in `javascript/main.js` and `javascript/components/test-react.js`. If you don't need react in your project, make sure you don't uncomment these lines or remove them completely. This will help to keep the compiled js file size down.

## Third party libraries

We no longer have a 'vendor' folder for these. Instead find ones that are packaged as npm libraries and install them as dependencies (see 'using npm' above). If they have CSS that needs including, this can be imported directly from the node_modules folder - see the example for glide in main.scss.

## Using and updating the tooling in wagtail-kit

You can remove this section from the readme file for new builds.

To run the tooling inside the `wagtail-kit` build, ensure that you run `npm install` from inside the built image, i.e. `wagtail-kit/built_image/ck_repo_name`

The easiest way to install new packages is to run `npm install --save-dev package_name` in `wagtail-kit/built_image/ck_repo_name`, but then copy the resultant changes to `package.json` and `package-lock.json` over to `/wagtail-kit/rca`. Note that when you do this you need to edit the copied files and change all instances of `ck_repo_name` to `rca`.

Changes to the config files can be made directly in `/wagtail-kit/rca`.

## Further details of the packages included

- **autoprefixer** - adds vendor prefixes as necessary for the browsers defined in `browserslist` in the npm config https://www.npmjs.com/package/autoprefixer
- **babel-core** - transpiler for es6 / react https://www.npmjs.com/package/babel-core
- **babel-eslint** - add-on for extra linting of experimental features (may not be necessary for all projects) https://www.npmjs.com/package/babel-eslint
- **babel-jest** - use Babel with Jest https://jestjs.io/docs/en/getting-started#using-babel
- **babel-loader** - use babel with webpack - https://www.npmjs.com/package/babel-loader
- **babel-preset-env** - babel preset for the latest version of es6, es2015
  etc. https://www.npmjs.com/package/babel-preset-env https://babeljs.io/env/
  https://babeljs.io/docs/plugins/
- **browser-sync** - for automatic reloading of your browser when changes are made to CSS / JS files https://www.npmjs.com/package/browser-sync
- **css-loader** – add support for Webpack to load stylesheets.
- **eslint** - lint your javascript https://www.npmjs.com/package/eslint
- **jest** - testing framework for JavaScript https://jestjs.io/
- **sass** - compiles Sass to CSS https://www.npmjs.com/package/sass
- **"mini-css-extract-plugin"** - extract CSS generated by Webpack into separate files.
- **npm-run-all** - run more than one npm script concurrently - used by some of our npm scripts https://www.npmjs.com/package/npm-run-all
- **onchange** - watches for changes in a set of files - used by our watch scripts https://www.npmjs.com/package/onchange
- **postcss-cli** - required by `autoprefixer` - https://www.npmjs.com/package/postcss-cli
- **"postcss-loader"** - integrate PostCSS preprocessing into Webpack’s styles loading.
- **postcss-custom-properties** - polyfill for CSS custom properties - https://www.npmjs.com/package/postcss-custom-properties
- **sass-lint** - Linting for Sass files - https://www.npmjs.com/package/sass-lint
- **sass-loader** - integrate Sass preprocessing into Webpack’s styles loading.
- **webpack** - Bundler for js files (can do much more too) - https://www.npmjs.com/package/webpack https://webpack.js.org/concepts/
- **webpack-cli** - The webpack command calls this behind the scenese (as of webpack v 4) https://www.npmjs.com/package/webpack-cli

## React specific packages

- **babel-polyfill** - IE11 fallbacks for some js functions https://www.npmjs.com/package/babel-polyfill
- **babel-preset-react** - babel preset for react. https://www.npmjs.com/package/babel-preset-react https://babeljs.io/env/ https://babeljs.io/docs/plugins/
- **eslint-plugin-react** - linting for react and jsx https://www.npmjs.com/package/eslint-plugin-react
