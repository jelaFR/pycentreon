"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

class Record:
    """
    """
    def __init__(self, values, api):
        self.values = values
        self.api = api
        self.default_ret = Record
        if values:
            self._parse_values(values)

    def _parse_values(self, values):
        """Parses values init arg.

        Parses values dict at init and sets object attributes with the
        values within.
        """
        for k, v in values.items():
            if isinstance(v, dict):
              pass
            elif isinstance(v, list):
              pass
            else:
                pass
            setattr(self, k, v)