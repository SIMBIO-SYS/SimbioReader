# SimbioReader 1.0.5

Requires Python 3.14 or later, below Python 4.

- Add selectable imaging, display, geometry and reference panels and internal
  reference filtering through `reader.reference.by_type()`.
- Group geometry and imaging metadata, accept optional downsampling and
  unnamed imaging subframes, and read HRIC detector and filter codes as
  numbers or text.
- Summarize CSV housekeeping tables with the first, middle and last samples.
- Expose the initial bit rate as `compression.ibr`, retaining
  `compression.ratio` as an alias.
- Read VIHI frame binning and support labels with optional repetition time
  and pixel coordinates.
- Exclude the `None` subphase sentinel from name and date lookups.
