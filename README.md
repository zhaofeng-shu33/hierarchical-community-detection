[![Build Status](https://travis-ci.com/zhaofeng-shu33/hierarchical-community-detection.svg?branch=master)](https://travis-ci.com/zhaofeng-shu33/hierarchical-community-detection)
[![CircleCI](https://circleci.com/gh/zhaofeng-shu33/hierarchical-community-detection.svg?style=svg)](https://circleci.com/gh/zhaofeng-shu33/hierarchical-community-detection)

# Description
`experiment_two_level.py` is the main script. It contains many utility functions for computing, data loading and saving, and plotting.
`runner.py` is the experiment runner. It is a wrapper of `experiment_two_level.py`.
`plotter.py` loads plotting point data(output from `runner.py`) and plotting the figure with `matplotlib`.

The following command will produce ideal result occasionally. By ideal result we mean the clustering tree has
the same topology structure with that of the ground truth.
```shell
python experiment_two_level.py --z_in_2=2.5 --z_o=0.2 --alg=info-clustering
```
to produce one curve for one method,
```shell
python runner.py --num_of_times=20 --mode=z_in_1 --alg=info-clustering 3 1 10 15
```


# How to reproduce the experiment results
## Medium Scale Experiment
Running artifacts can be viewed from [circleci](https://circleci.com/gh/zhaofeng-shu33/hierarchical-community-detection), which runs a medium scale experiment and plots the results.
## Full Scale Experiment
For the full running results of this experiment, check the [gitlab cicd](https://gitlab.com/zhaofeng-shu33/hierarchical-community-detection/pipelines) which uses self-hosted agent to accomplish the job. Result images are available as running artifacts.

See `reproduce_experiment.py`. You need to run for many hours since we repeat for 20 times and in each time we evaluate at 10 configuration.
