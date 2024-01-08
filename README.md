# okdp-drafts

This repo is aimed to store some OKDP related works before we define the an appropriate structure for the main repository.

This is currently two important folders: `bricks` and `components`

A components is an installable package (i.e jupyterhub). It is implemented as a meta-chart, a chart containing one
or several sub-chart as dependency.

A README.md file should be present in each component folder.

Some dependencies are externally hosted and some are stored locally, in the `bricks` folder. This folder contains helm
charts (or meta-charts). But, by convention, these charts are not intended to be installed independently, but only as a 
dependency of one or several components.




