# K9000 web bundle / npm package candidate

This package is created from a checked and pinned source build in CI. It includes static K9000 HTML/CSS/JS, source-approved brand icons, and a generated Babylon/Vue/jQuery demonstration build. `private: true` prevents npm registry publication, but `npm pack` produces a portable tarball for controlled review.

Run the repository's `tools/fourPackageTrain.py stage-npm` only after `npm ci --ignore-scripts` and `npm run build` in `frontEnd/prototypes/glassWorld`. `npm pack` runs from the generated staging directory. No community plugin from `frontEnd/plugins/incoming`, personal artwork, passwords, or model weights are packed. The source uses jQuery 3.7.1, Babylon Core 9.32.0, Vue 3.5.44, and Vite 8.3.5. Their corresponding own upstream licenses must be reviewed before public redistribution.

The npm archive is **not a native app, DMG, APK, or proof of a ChatGPT plugin installation**. Public npm publication remains disabled, and human Crown promotion is still required.
