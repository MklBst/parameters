Grammar v3
==========

See [`GRAMMAR-CHANGELOG.md`](https://github.com/daydreaming-experiment/parameters/blob/master/GRAMMAR-CHANGELOG.md) for a description of the changes from the previous version.

Below is the full description of the grammar.

Rules
-----

The grammar is defined by the following rules:

1. The parameters file contains pure [JSON](http://json.org/).
2. The root node in the file is a JSON object (`{}`) containing the following *mandatory* properties:
  * `version`: a *string* defining the version of the parameters.
  * `backendExpId`: a *string* defining the identity of the experiment for the backend.
  * `backendDbName`: a *string* defining the name of the database to upload the results to in the backend.
  * `expDuration`: an *integer* defining the duration before publication of results if users use the app as intented.
  * `backendApiUrl`: a *string* defining the url of the backend API.
  * `resultsPageUrl`: a *string* defining the url of the results page.
  * `schedulingMinDelay`: an *integer* defining the minimal delay between two probes (in seconds).
  * `schedulingMeanDelay`: an *integer* defining the average delay between two probes (in seconds).
  * `questions`: a *list* of question definition objects (see below for a description of what question definition objects should contain).
  * `sequences`: a *list* of sequence definition objects (see below for what they should contain)
3. A *question definition* object contains the following *mandatory* properties:
  * `name`: a *string* defining a name for the question (used to reference questions when defining sequences); question names must be unique across questions.
  * `type`: a *string* representing the type of question asked; can be either `"multipleChoice"`, `"matrixChoice"`, `"autoList"`, `"manySliders"`, `"slider"`, or `"starRating"` (star-ratings appear like sliders in the app, but behave in a discreet manner instead of continuous).
  * `details`: a JSON *object* containing the details of the question, as detailed in the following rule.
4. A *details* object is the body of the question description; its content depend on the `type` property of the question:
  * If `type` is `"multipleChoice"`:
    * Mandatory fields:
      * `text`: a *string* containing the actual question asked to the user.
      * `choices`: a *list* of *strings*, each one being a choice proposed to the user (the order is conserved).
    * No optional fields
  * If `type` is `"matrixChoice"`:
    * Mandatory fields:
      * `text`: a *string* containing the actual question asked to the user.
      * `choices`: a *list* of *strings*, each one being a choice proposed to the user in the matrix (the order is conserved); for the moment choices can only be `"Home"`, `"Commuting"`, `"Work"`, `"Public space"`, or `"Outside"`, because those are the only items for which an icon is defined.
    * No optional fields
  * If `type` is `"autoList"`:
    * Mandatory fields:
      * `text`: a *string* containing the actual question asked to the user.
      * `hint`: a *string* defining what the drop-down list originally shows before the user starts typing in it.
      * `possibilities`: a *list* of *strings*, each one being a possibility proposed to the user in the drop-down list; those strings can contain tags, in a format described in a section below.
  * If `type` is `"manySliders"`:
    * Mandatory fields:
      * `text`: a *string* containing the actual question asked to the user.
      * `availableSliders`: a *list* of *strings* defining all the initially available slider titles; these can have tags as in the `autoList` question.
      * `defaultSliders`: a *list* of *strings* defining the sliders that will appear the first time the user answers this question (subsequently his editions will apply); each item here must be present in `availableSliders`.
      * `hints`: a *list* of at least two *strings*, which serves two purposes: the first and last items are shown as the extremes of on each slider, and the whole list of items is used as an indication of the user's choice as she sets the slider's progress; this indication is only shown if the `showLiveIndication` property is `true`.
      * `addItemHint`: a *string* defining what the drop-down list in edit-mode originally shows before the user starts typing in it.
      * `dialogText`: a *string* defining the text of the explanation dialog that appears when the user enters edit mode in the question.
    * Optional field:
      * `showLiveIndication`: a *boolean*; if `true`, show live indication of the user's rating as she makes her choice on sliders; defaults to `false`.
  * If `type` is `"slider"` or `"starRating"`:
    * There is a single mandatory field, `subQuestions`: it contains a *list* of sub-question objects; those sub-questions have the following *mandatory* fields:
      * `text`: a *string* containing the actual sub-question asked to the user.
      * `hints`: a *list* of at least two *strings*, which are used just like the hints in `manySliders`; note that here again, live indication is only shown if the `showLiveIndication` property is `true`.
    * sub-questions have the following *optional* properties:
      * `notApplyAllowed`: a *boolean*; if `true`, a check-box allowing the user to skip this specific sub-question will appear in the app; defaults to `false`.
      * `showLiveIndication`: a *boolean*; if `true`, show live indication of the user's rating as she makes her choice; defaults to `false`.
    * If the question `type` is `"slider"`, the following property is *optional* in sub-questions:
      * `initialPosition`: an *integer* between `0` and `100` (included), defining the initial position of the selector on the slider when the question is asked; defaults to `0` (i.e. to the left).
    * If the question `type` is `"starRating"`, the following properties are *optional*:
      * `numStars`: a positive *integer* defining the number of stars the rating would have if it were really displayed as a star-rating (and not as a discreet slider as is the case now); combined with `stepSize`, these two parameters define the number of discreet values the rating allows; defaults to `5`.
      * `stepSize`: a positive *float* defining the size of the interval between two discreet values; the total number of values allowed by the star-rating is `1 + ceiling(numStars  / stepSize)`; defaults to `0.5`.
      * `initialRating`: a *float* between `0.0` and `numStars` (included) defining the initial rating when the question is asked; this doesn't need to be a multiple of `stepSize`; defaults to `0.0` (i.e. to the left).













About question groups, slots, and positioning
---------------------------------------------

*Slots* and *groups* are used to express the way questions are selected and randomized when a probe is created. Basically, we want to be able to group questions together, randomize the *intra-group* order, randomize the *inter-group* order, and still have the possibility to put particular questions or groups of questions at specific positions in the question sequence (like the first or last).

So when creating a probe, the daydreaming app allocates `nSlotsPerProbe` *slots* to be filled, and `nSlotsPerProbe` *groups* of questions to be inserted in these slots (one group per slot). The slot into which a group is inserted can be either predefined or randomly selected (more about that below). Once the question groups are formed (more about that below, again), the predefined-position groups are inserted into their corresponding slots, and the random-position groups are inserted in random order into the remaining slots. Finally, each group of questions is itself internally randomized. This procedure allows for a broad range of question orderings and randomizations to be defined.

TODO: about positioning, slots and after
TODO: about sequences
TODO: about possibilities with tags

### Question selection and grouping

The parameters file assigns each question to a group that has either a predefined position or a random position. This is done thanks to the `slot` property, which serves to define both the group to which a question belongs and the given group's position (i.e. the slot: either predefined or random).

Here's how:

* All questions with an identical `slot` property belong to the same group; this is how groups are defined. There must be at least `nSlotsPerProbe` groups.
* `slot` is always a string, but if that string represents an *integer* (e.g. `"0"`, `"-1"`, or `"-2"`), then the corresponding group has a predefined position (so, respectively, the first, last, or penultimate slot). If `slot` does *not* represent an integer (e.g. `"A"` or `"B"`), the corresponding group will be randomly positioned.

Forming the question groups involves simply grouping together all the questions with identical `slot`, keeping *all* the predefined-position groups, and keeping only as many random-position groups as necessary (themselves randomly selected) to reach `nSlotsPerProbe` groups. So if the parameters file defines e.g. three predefined-position groups and four random-position groups, and `nSlotsPerProbe` is 5, two random-position groups are randomly selected among the available four, and the resulting five groups are fed to the slot-insertion process.

Note that if a group is to be inserted in the probe, *all* questions in that group will appear (i.e. there is no intra-group selection).

Final notes:
* Don't try stupid things with group positionning: if you define `nSlotsPerProbe` to be 5, and define a predefined-position group at position `"-7"`, I don't know what will happen (especially if there's another predefined-position group at position `"3"`).
* If there are more predefined-position groups than `nSlotsPerProbe`, I don't know what will happen either.
* `"1.0"`, `"1,0"`, `"2-1"`, etc., do **not** represent integers.
