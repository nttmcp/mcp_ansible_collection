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
module: user
short_description: Create/Update/Remove User Accounts
description:
    - Create/Update/Remove the user accounts for your organization
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
    username:
        description:
            - The username to retrieve
        required: true
        type: str
    my_user:
        description:
            - Return just my user information
            - This does not require a Org/Primary administrator role
            - Users can only update password, fullname, firstname, lastname, email, phone and phone_country_code
        required: false
        default: False
        type: bool
    password:
        description:
            - The password to use
        required: false
        type: str
    new_password:
        description:
            - Used to change the password of an existing user
        required: false
        type: str
    firstname:
        description:
            - The fistname of the user
        required: false
        type: str
    lastname:
        description:
            - The lastname of the user
        required: false
        type: str
    fullname:
        description:
            - The fullname of the user
        required: false
        type: str
    email:
        description:
            - The email address of the user
        required: false
        type: str
    phone_country_code:
        description:
            - The dialing code for the country of the user
        required: false
        type: int
    phone:
        description:
            - The phone number of the user
        required: false
        type: int
    remove_phone:
        description:
            - Remove the user's phone information
        required: false
        type: bool
        default: False
    department:
        description:
            - The department of the user
        required: false
        type: str
    custom_1:
        description:
            - User defined custom attribute 1
        required: false
        type: str
    custom_2:
        description:
            - User defined custom attribute 1
        required: false
        type: str
    roles:
        description:
            - List of roles for the user
        required: false
        type: list
        elements: str
    state:
        description:
            - The action to be performed
        required: false
        type: str
        default: present
        choices:
            - present
            - absent
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

  - name: Create/Update a user
    user:
      region: na
      username: joeyjoejoe
      password: "{joey's password"
      fullname: Joey JoeJoe
      firstname: Joey
      lastname: JoeJoe
      email: joey.joejoe@abc.local
      roles:
        - network
        - server
        - vpn
      phone: 5555555555
      phone_country_code: 1
      department: Awesomeness
      custom_1: 1st Cool
      custom_2: 2nd Cool

  - name: Change a user's password
    user:
      region: na
      username: joeyjoejoe
      new_password: "joey's new password"

  - name: Delete a user
    user:
      region: na
      username: joeyjoejoe
      state: absent
'''

RETURN = '''
msg:
    description: A useful message
    returned: success and state == absent
    type: str
    sample: Request to Delete User has been accepted. Please use appropriate Get or List API for status.
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
            returned: success
            type: complex
            contains:
                userName:
                    description: The user ID
                    type: str
                    sample: mysusername
                firstName:
                    description: The user's firstname
                    type: str
                    sample: John
                lastName:
                    description: The user's lastname
                    type: str
                    sample: Doe
                state:
                    description: The user's status
                    type: str
                    sample: NORMAL
                emailAddress:
                    description: The user's email address
                    type: str
                    sample: john.doe@abc.local
                organization:
                    description: Organizational level information about the user
                    type: complex
                    contains:
                        homeGeoApiHost:
                            description: The user's home Geo API host
                            type: str
                            sample: api-na.mcp-services.net
                        homeGeoName:
                            description: The name of the home Geo
                            type: str
                            sample: North America
                        id:
                            description: The UUID of the home Geo
                            type: str
                            sample: b2fbd7e6-ddbb-4eb6-a2dd-ad048bc5b9ae
                        homeGeoId:
                            description: The home Geo ID
                            type: str
                            sample: northamerica
                        name:
                            description: The organization name
                            type: str
                            sample: myorg
                fullName:
                    description: The user's full name
                    type: str
                    sample: John Doe
                role:
                    description: List of access roles associated with the user
                    type: list
'''

from time import sleep
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nttmcp.mcp.plugins.module_utils.utils import get_credentials, get_regions, compare_json
from ansible_collections.nttmcp.mcp.plugins.module_utils.provider import NTTMCPClient, NTTMCPAPIException


def create_user(module, client):
    """
    Create a User

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :returns: User Object
    """
    user = dict()

    # Input validation
    if None in [module.params.get('username'),
                module.params.get('password'),
                module.params.get('fullname'),
                module.params.get('firstname'),
                module.params.get('lastname'),
                module.params.get('email')]:
        module.fail_json(msg='A valid value for username, password, fullname, firstname, lastname and email are required')
    if module.params.get('phone') is not None and module.params.get('phone_country_code') is None:
        module.fail_json(msg='phone_country_code is required when a value for phone is present')
    if module.params.get('roles') is not None and type(module.params.get('roles')) != list:
        module.fail_json(msg='Roles must be in provides as a list of strings representing the role names')

    try:
        client.create_user(username=module.params.get('username'),
                           password=module.params.get('password'),
                           roles=module.params.get('roles'),
                           fullname=module.params.get('fullname'),
                           firstname=module.params.get('firstname'),
                           lastname=module.params.get('lastname'),
                           email=module.params.get('email'),
                           phone=module.params.get('phone'),
                           phone_country_code=module.params.get('phone_country_code'),
                           department=module.params.get('department'),
                           custom_1=module.params.get('custom_1'),
                           custom_2=module.params.get('custom_2')
                           )
        # Introduce a pause to allow the API to catch up
        sleep(3)
        user = client.get_user(username=module.params.get('username'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=str(e).replace('"', '\''))
    module.exit_json(changed=True, data=user)


def update_user(module, client, user):
    """
    Update a User

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg user: The user object to be updated
    :returns: User Object
    """
    username = user.get('userName')
    try:
        client.update_user(username=username,
                           fullname=module.params.get('fullname'),
                           firstname=module.params.get('firstname'),
                           lastname=module.params.get('lastname'),
                           email=module.params.get('email'),
                           phone=module.params.get('phone'),
                           phone_country_code=module.params.get('phone_country_code'),
                           department=module.params.get('department'),
                           custom_1=module.params.get('custom_1'),
                           custom_2=module.params.get('custom_2')
                           )
        # Introduce a pause to allow the API to catch up
        sleep(3)
        # Search for the user
        if module.params.get('my_user'):
            user = client.get_my_user()
        else:
            user = client.get_user(username=username)
    except NTTMCPAPIException as e:
        module.fail_json(msg=str(e).replace('"', '\''))
    module.exit_json(changed=True, data=user)


def update_user_roles(module, client):
    """
    Update a user's roles

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :returns: Something
    """
    user = dict()
    try:
        client.set_user_roles(username=module.params.get('username'), roles=module.params.get('roles'))
        # Introduce a pause to allow the API to catch up
        sleep(3)
        # Search for the user
        if module.params.get('my_user'):
            user = client.get_my_user()
        else:
            user = client.get_user(username=module.params.get('username'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=str(e).replace('"', '\''))
    return user


def change_password(module, client, user):
    """
    Change a user's password

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg user: The user object

    :returns: Something
    """
    try:
        client.change_user_password(username=user.get('userName'), password=module.params.get('new_password'))
    except NTTMCPAPIException as e:
        module.fail_json(msg=str(e).replace('"', '\''))


def delete_user(module, client, username):
    """
    Remove a User

    :arg module: The Ansible module instance
    :arg client: The CC API client instance
    :arg username: The username of the user to remove

    :returns: User Object
    """
    msg = ''
    if username is None:
        module.fail_json(msg='A valid username is required')
    try:
        msg = client.remove_user(username=username)
    except NTTMCPAPIException as e:
        module.fail_json(msg='Failed to remove the user: {0}'.format(e))
    module.exit_json(changed=True, msg=msg)


def compare_user(module, user, full_compare):
    """
    Compare the provided arguments to an existing User

    :arg module: The Ansible module instance
    :arg user: The user object to compare to

    :returns: Compare result
    """
    new_user = deepcopy(user)

    if module.params.get('fullname'):
        new_user['fullName'] = module.params.get('fullname')
    if module.params.get('lastname'):
        new_user['lastName'] = module.params.get('lastname')
    if module.params.get('firstname'):
        new_user['firstName'] = module.params.get('firstname')
    if module.params.get('email'):
        new_user['emailAddress'] = module.params.get('email')
    if full_compare:
        if module.params.get('roles'):
            new_user['role'] = module.params.get('roles')
    if module.params.get('remove_phone'):
        if new_user.get('phone'):
            new_user.pop('phone')
    else:
        if module.params.get('phone'):
            if not new_user.get('phone'):
                new_user['phone'] = dict()
            new_user['phone']['number'] = str(module.params.get('phone'))
        if module.params.get('phone_country_code'):
            if new_user.get('phone'):
                new_user['phone']['countryCode'] = str(module.params.get('phone_country_code'))
    if module.params.get('department'):
        new_user['department'] = module.params.get('department')
    if module.params.get('custom_1'):
        new_user['customDefined1'] = module.params.get('custom_1')
    if module.params.get('custom_2'):
        new_user['customDefined2'] = module.params.get('custom_2')

    compare_result = compare_json(new_user, user, None)
    # Implement Check Mode
    if module.check_mode:
        module.exit_json(data=compare_result)
    return compare_result


def compare_user_roles(module, roles):
    """
    Compare the provided roles to an existing user's roles

    :arg module: The Ansible module instance
    :arg roles: The existing roles to compare to

    :returns: Compare result
    """
    return compare_json({'role': module.params.get('roles')}, {'role': roles}, None)


def main():
    """
    Main function
    :returns: IP Address List Information
    """
    module = AnsibleModule(
        argument_spec=dict(
            auth=dict(type='dict'),
            region=dict(default='na', type='str'),
            username=dict(required=True, type='str'),
            my_user=dict(default=False, type='bool'),
            password=dict(required=False, type='str'),
            new_password=dict(required=False, type='str'),
            roles=dict(required=False, type='list'),
            fullname=dict(default=None, type='str'),
            firstname=dict(default=None, type='str'),
            lastname=dict(default=None, type='str'),
            email=dict(default=None, type='str'),
            phone_country_code=dict(default=None, type='int'),
            phone=dict(default=None, type='int'),
            remove_phone=dict(default=False, type='bool'),
            department=dict(default=None, type='str'),
            custom_1=dict(default=None, type='str'),
            custom_2=dict(default=None, type='str'),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True
    )
    user = None
    username = module.params.get('username')
    state = module.params.get('state')
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

    # Search for the user
    try:
        if module.params.get('my_user'):
            user = client.get_my_user()
        else:
            user = client.get_user(username=username)
    except NTTMCPAPIException as e:
        module.fail_json(msg=str(e).replace('"', '\''))

    if state == 'present':
        if user is None:
            if module.check_mode:
                module.exit_json(msg='A new user with the username {0} will be created'.format(username))
            # Create User
            create_user(module, client)
        else:
            try:
                changed = False
                if module.params.get('new_password'):
                    change_password(module, client, user)
                    changed = True
                # Check for role changes and for checkmode
                compare_user(module, user, True)
                if compare_user_roles(module, user.get('role')).get('changes'):
                    user = update_user_roles(module, client)
                    changed = True
                compare_result = compare_user(module, user, False)
                if compare_result.get('changes'):
                    update_user(module, client, user)
                module.exit_json(changed=changed, data=user)
            except NTTMCPAPIException as e:
                module.fail_json(msg='Failed to update the User - {0}'.format(e))
    elif state == 'absent':
        if user is None:
            module.exit_json(msg='User not found')
        # Implement Check Mode
        if module.check_mode:
            module.exit_json(msg='An existing user was found for username {0} and will be removed'.format(username))
        delete_user(module, client, username)


if __name__ == '__main__':
    main()
