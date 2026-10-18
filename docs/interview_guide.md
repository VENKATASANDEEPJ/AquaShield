# Interview guide

## What the project does

AquaShield AI is a small environmental data analysis platform. The initial city view uses historical daily rainfall estimates for Chennai. The custom data lab accepts CSV data and lets a user profile it, choose transparent cleaning actions, calculate descriptive summaries, and export cleaned results.

## Why no flood prediction model?

Rainfall is not a label for whether a location flooded. The repository did not include incident observations aligned by time and place, so generating labels from rainfall would create unsupported claims. A responsible next step is to obtain and validate a genuine event dataset, compare its coverage to rainfall, then establish a baseline before considering a model.

## Data lifecycle

The city source is retrieved over HTTP, its date and source are returned with the result, and the backend uses a short in-memory cache. Uploaded CSVs are parsed and profiled in memory. Cleaning is opt-in and reflected in row counts. Summary metadata for completed analyses is stored in SQLite; row contents and uploaded files are not.

## Current limitations

The rainfall series is an ERA5 reanalysis estimate at one coordinate. There are no active road disruption, drainage, or floodwater quality layers. This is not a real-time warning system, and deployment has not been performed. Those limits are part of the design and should be stated during a demonstration.

