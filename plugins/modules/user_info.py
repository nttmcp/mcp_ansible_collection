#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, NTT Ltd.
#
# Author: Ken Sinfield <ken.sinfield@cis.ntt.com>
#
# GNU General Public License v2.0 (see COPYING or https://www.gnu.org/licenses/gpl-2.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}
DOCUMENTATION = '''
---
module: user_info
short_description: Get and List User Accounts
description:
    - Get and List the user accounts for your organization
version_added: "1.0.4"
author:
    - Ken Sinfield (@kensinfield)
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
    region:
        description:
            - The geographical region
        required: false
        default: na
        type: str
    my_user:
        description:
            - Return just my user information
            - This does not require a Org/Primary administrator role
        required: false
        default: False
        type: bool
    username:
        description:
            - The username to retrieve
        required: false
        type: str
    firstname:
        description:
            - The fistname to search on
            - Supports using * as a wildcard
        required: false
        type: str
    lastname:
        description:
            - The lastname to search on
            - Supports using * as a wildcard
        required: false
        type: str
    email:
        description:
            - The email address to search on
            - Supports using * as a wildcard
        required: false
        type: str
    phone_country_code:
        description:
            - The dialing code for the country to search on
        required: false
        type: str
    phone:
        description:
            - The phone number to search on
        required: false
        type: str
    state:
        description:
            - The user's status
            - Supports using * as a wildcard
        required: false
        type: str
    department:
        description:
            - The department to search on
            - Supports using * as a wildcard
        required: false
        type: str
notes:
    - Requires NTT Ltd. MCP account/credentials
requirements:
    - requests
    - configparser
    - pyOpenSSL
    - netaddr
        - configparser>=3.7.4
'''

EXAMPLES = '''
- hosts: 127.0.0.1
  connection: local
  collections:
    - nttmcp.mcp
  tasks:

  - name: Get your User
    user_info:
      region: na
      my_user: True

  - name: Get a specific User
    user_info:
      region: na
      username: some_username

  - name: List all user(s) with the lastname smith
    user_info:
      region: na
      lastname: smith

  - name: List all user(s) in a failed state
    user_info:
      region: na
      state: 'FAILED*'

  - name: List all user(s) with an @abc.local email address
    user_info:
      region: na
      email: '*@abc.local'
'''

RETURN = '''
data:
    description: dict of returned Objects
    returned: success
    type: complex
    contains:
        count:
            description: The number of objects returned
            returned: success
            type: int
            sample: 1
        user:
            description: User Object
            contains:
                userName:
                    description: The user ID
                    type: string
                    sample: mysusername
                firstName:
                    description: The user's firstname
                    type: string
                    sample: John
                lastName:
                    description: The user's lastname
                    type: string
                    sample: Doe
                state:
                    description: The user's status
                    type: string
                    sample: NORMAL
                emailAddress:
                    description: The user's email address
                    type: string
                    sample: john.doe@abc.local
                organization:
                    description: Organizational level information about the user
                    type: complex
                    contains:
                        homeGeoApiHost:
                            description: The user's home Geo API host
                            type: string
                            sample: api-na.mcp-services.net
                        homeGeoName:
                            description: The name of the home Geo
                            type: string
                            sample: North America
                        id:
                            description: The UUID of the home Geo
                            type: string
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        homeGeoId:
                            description: The home Geo ID
                            type: string
                            sample: northamerica
                        name:
                            description: The organization name
                            type: string
                            sample: myorg
                fullName:
                    description: The user's full name
                    type: string
                    sample: John Doe
                role:
                    description: List of access roles associated with the user
                    type: list
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, return_object
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def main():
    """
    Main function
    :returns: IP Address List Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            my_user=dict(default=False, type='bool'),
            username=dict(default=None, type='str'),
            firstname=dict(default=None, type='str'),
            lastname=dict(default=None, type='str'),
            email=dict(default=None, type='str'),
            phone_country_code=dict(default=None, type='str'),
            phone=dict(default=None, type='str'),
            state=dict(default=None, type='str'),
            department=dict(default=None, type='str'),
        ),
        supports_check_mode=True
    )
    return_data = return_object('user')
    user = None

    try:
        credentials = get_credentials(module)
    except ImportError as e:
        module.fail_json(msg='{0}'.format(e))

    # Check the region supplied is valid
    regions = get_regions()
    if module.params.get('region') not in regions:
        module.fail_json(msg='Invalid region. Regions must be one of {0}'.format(regions))

    if credentials is False:
        module.fail_json(msg='Could not load the user credentials')

    try:
        client = NTTMCPClient(credentials, module.params.get('region'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=e.msg)

    try:
        if module.params.get('my_user'):
            user = client.get_my_user()
            if user is not None:
                return_data['user'].append(user)
        elif module.params.get('username') is not None:
            user = client.get_user(username=module.params.get('username'))
            if user is not None:
                return_data['user'].append(user)
        else:
            return_data['user'] = client.list_users(firstname=module.params.get('firstname'),
                                                    lastname=module.params.get('lastname'),
                                                    email=module.params.get('email'),
                                                    phone_country_code=module.params.get('phone_country_code'),
                                                    phone=module.params.get('phone'),
                                                    state=module.params.get('state'),
                                                    department=module.params.get('department'))
        return_data['count'] = len(return_data.get('user'))
        module.exit_json(data=return_data)
    except (KeyError, IndexError, AttributeError, NTTMCPAPIException) as e:
        module.fail_json(msg='Could not retrieve a list of users - {0}'.format(e))


if __name__ == '__main__':
    main()
