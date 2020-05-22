#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, NTT Ltd.
#
# Author: Omar Ahmad <omar.ahmad@cis.ntt.com>
#
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "NTT Ltd.",
}

DOCUMENTATION = """
---
module: credentials
short_description: Get credentials
description:
    - Get NTTMCP credentials from one of many places
version_added: "2.11"
author:
    - Omar Ahmad (@chiqomar)
options:
    auth:
        description:
            - Optional dictionary containing the authentication and API information for Cloud Control
        required: false
        type: dict
        suboptions:
            username:
                  description:
                      - The Cloud Control API username
                  required: false
                  type: str
            password:
                  description:
                      - The Cloud Control API user password
                  required: false
                  type: str
            api:
                  description:
                      - The Cloud Control API endpoint e.g. api-na.mcp-services.net
                  required: false
                  type: str
            api_version:
                  description:
                      - The Cloud Control API version e.g. 2.11
                  required: false
                  type: str
notes:
    - Requires NTT Ltd. MCP account/credentials
requirements:
    - requests
    - configparser
    - pyOpenSSL
    - netaddr
"""

EXAMPLES = """
- hosts: 127.0.0.1
  connection: local
  collections:
    - nttmcp.mcp
  tasks:
  - name: Get credentials
    nttmcp.mcp.credentials:
    register: ftp_creds
  - name: Copy an Image to FTPS
    no_log: true
    shell: |
      set -euxo pipefail
      lftp -c 'set ftps:initial-prot "";\
      set ftp:ssl-allow true ; set ssl:verify-certificate no;\
      open -u "{{ftp_creds.user_id}}","{{ftp_creds.password}}" \
      -e "put {{ import_image }}/{{ import_image }}.mf; \
      put {{ import_image }}/{{ import_image }}.ovf;\
      put {{ import_image }}/{{ import_image }}-disk1.vmdk;\
       quit" ftp://{{ sftp_host }}'
"""

RETURN = """
api_endpoint:
    description: Endpoint for the chosen MCP region
    type: str
    sample: ""api-ash99-gen.mcp-services.net"
api_version:
    description: CC API version targeted
    type: str
    sample: "2.11"
password:
    description: Password for CC
    type: str
    sample: "my_secret_password"
user_id:
    description: User ID for CC
    type: str
    sample: "jsmith"
"""

from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import (
    utils_check_imports,
    get_credentials,
)
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Main function

    :returns: Credentials
    """
    module = AnsibleModule(
        argument_spec=dict(auth=dict(type="dict")), supports_check_mode=True
    )
    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg="{}".format(e))
    else:
        module.exit_json(changed=False, **credentials)


if __name__ == "__main__":
    main()
