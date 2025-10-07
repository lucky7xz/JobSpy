### user.json

The user configuration is stored in the `user.json` file. This file contains the main entry point for the user configuration.

The following keys are available in the `user.json` file:

#### `user`

The user information. This contains the following keys:

##### `name`

The name of the user. This is used to identify the user and is used in the UI.

#### `search_settings`

The search settings for the user. This contains the following keys:

##### `name`

The name of the search setting. This is used to identify the search setting and is used in the UI.

##### `site_name`

The site name of the search setting. This can be one of the following values:

* `indeed`
* `linkedin`
* `google`

##### `hours_old`

The number of hours old the search results should be. This is used to filter out search results that are older than the specified number of hours.

##### `is_remote`

Whether the search setting should be run remotely. This is used to determine whether the search should be run on the local machine or on a remote server.

##### `results_wanted`

The number of search results that should be returned. This is used to limit the number of search results that are returned.

##### `country_indeed`

The country that the search setting should be run in. This is used to filter out search results that are not from the specified country.

##### `location`

The location that the search setting should be run in. This is used to filter out search results that are not from the specified location.

##### `keywords`

The keywords that the search setting should be run with. This is used to filter out search results that do not contain the specified keywords.

The keywords should be an array of strings, where each string is a keyword that should be searched for.
