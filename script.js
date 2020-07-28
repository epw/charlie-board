// Copyright 2020 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var REFRESH_DURATION = 60 * 1000;

var urlparams = new URLSearchParams(window.location.search);

var refresh = null;

function init() {
    if (urlparams.has("refresh")) {
	var n = parseInt(urlparams.get("refresh"));
	if (n > 1) {
	    REFRESH_DURATION = n * 1000;
	}
	refresh = setTimeout(function() { location.reload(); }, REFRESH_DURATION);
    }
}

init();
